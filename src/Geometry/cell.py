from abc import ABC, abstractmethod
import numpy as np
from src.IO.config import Config


"""
Geometry: Cell base class

This module defines 'Cell', an abstract base class representing a polygonal
cell in the mesh. The class stores geometry (corner coordinates, area,
midpoint), The physical state ('oil', 'flow'), and relationships to neighboring
cells. Child classes must implement 'findArea' to compute area from corners.

Design principles:
- Keep computed values cached on first access to avoid repeated work.
- Store references to the parent mesh when available so global lookup
  structures (point->cells, id->cell) can be built once and reused.
"""


class Cell(ABC):
    """
    Abstract base for mesh cells.

    Purpose:
    - Provide common data used by all cell
      types (triangles, quads, ....).

    Key responsibilities:
    - Hold corner coordinates ('_cords') and provide 'midPoint' and 'area'.
    - Cache computed properties (area, midpoint, neighbor lists, normals).
    - Provide hooks for physical values ('oil', 'flow') with validation.

    Args:
        msh: Mesh object. The mesh is used
             to calculate neighbor/lookup operations.
        cell_points: Iterable of integer indices into 'msh.points' describing
                     the corners of this cell in order.
        cell_id: Unique identifier for the cell.
        config : Simulation configuration

    Returns:
        An initialized 'Cell' instance. Concrete subclasses must implement
        'findArea()' to compute the polygon area.
    """

    def __init__(self, msh, cell_points, cell_id, config: Config = None):
        self.type = None
        self._id = cell_id

        # Reference to the mesh that holds this cell. This allows access to
        # global lookup tables on the mesh object to avoid expensive scans.
        self._msh = msh
        self._config = config

        # Internal state / caches.
        self._cords = [msh.points[i] for i in cell_points]
        self._midPoint = None
        self._area = None
        self._scaledNormal = None
        self._pointSet = None
        self._ngb = []
        self._flow = None
        self._oil = None
        self._isFishing = None

        # 'newOil' is used externally to accumulate oil changes between
        # simulation steps; leave it public so callers can append to it.
        self.newOil = []

    def _update_geometry(self, cellList=None):
        """
        Compute derived values in a safe order.

        Why ordering? Some derived attributes depend on other
        attributes (e.g. normals depend on neighbor depends on midPoint and so on).
        Calling the properties in an order that respects those dependencies
        ensures caches are populated consistently.
        Args:
            cellList: list of all cells in the mesh 
        """

        self._midPoint = self.midPoint
        self._area = self.area
        # neighbor computation may build mesh-level lookup maps
        self.findNGB(cellList)
        # normals depend on neighbors and midPoint
        self.findScaledNormales(cellList)
        self._flow = self.flow
        self._oil = self.oil
        self._isFishing = self.isFishing

    # --- area computations -----------------------------------------

    @property
    def area(self):
        """Return the area of the cell (cached).

        The area is computed on first access by delegating to 'findArea', a
        method implemented by concrete subclasses. Caching avoids repeated
        geometric work during simulation loops.

        Returns:
            float: area of the cell.
        """
        if self._area is None:
            self._area = self.findArea()
        return self._area

    @abstractmethod
    def findArea(self):
        """Compute the geometric area of the cell.

        Subclasses implement the actual formula (e.g., triangle area
        using the shoelace formula). The method should return a numeric
        scalar area.
        Returns:
            float: area of the cell.
        """
        pass

    # --- fishing zone check ----------------------------------------------

    @property
    def isFishing(self):
        """Boolean indicating if the cell lies inside the fishing zone.

        The result is cached. Errors while checking return False to keep
        simulations robust (better to assume not fishing than crash).
        Returns:
            bool: True if the cell is inside the fishing zone.
        """
        if self._isFishing is None:
            try:
                self._isFishing = self.isFishingCheck()
            except Exception:
                # Keep simulation robust: default to not-fishing on errors.
                self._isFishing = False
        return self._isFishing

    def isFishingCheck(self):
        """Perform the geometric check against configured borders.

        Returns True if the cell midpoint lies within the rectangular box
        defined by 'self._config.geometry['borders']'.
        Returns:
            bool: True if the cell is inside the fishing zone.
        """

        fishxmin = self._config.geometry["borders"][0][0]
        fishxmax = self._config.geometry["borders"][0][1]
        fishymin = self._config.geometry["borders"][1][0]
        fishymax = self._config.geometry["borders"][1][1]
        x = self.midPoint[0]
        y = self.midPoint[1]
        if x is None or y is None:
            return False
        return fishxmin < x < fishxmax and fishymin < y < fishymax

    # --- flow computations -----------------------------------------

    @property
    def flow(self):
        """Return the cell flow vector as a numpy array (cached).

        Flow can be programmatically set via the 'flow' setter. When not set
        it defaults to the value returned by 'findFlow' (which can be
        overridden or replaced by configuration in future versions).
        Returns:
            numpy.ndarray: 1D array representing the flow vector.
        """
        if self._flow is None:
            self._flow = np.array(self.findFlow())
        return self._flow

    @flow.setter
    def flow(self, value):
        """Validate and set the flow vector.

        Accepts any object convertible to a numpy array; raises 'TypeError'
        when conversion fails. Keeping the conversion centralized simplifies
        callers and guarantees 'flow' is always a numpy array internally.
        Args:
            value: object convertible to numpy array.
        Raises:
            TypeError: when 'value' cannot be converted to numpy array.
        """
        try:
            arr = np.array(value)
        except Exception:
            raise TypeError("flow must be convertible to a numpy array")
        self._flow = arr

    def findFlow(self):  # TODO Brage: add ability to set flow function
        """Default flow function.

        The default is a simple analytic field based on the midpoint. This
        is a placeholder so unit tests and simple simulations have a
        deterministic flow; production code can inject a different
        'findFlow' or set 'flow' directly.
        Returns:
            numpy.ndarray: 1D array representing the flow vector.
        """
        mp = self.midPoint
        return np.array([mp[1] - mp[0] * 0.2, -mp[0]])

    # --- midpoint computations -----------------------------------------

    @property
    def midPoint(self):
        """Return the geometric center (average of corner coordinates).

        The midpoint is used for many derived computations (flow evaluation,
        fishing zone checks, normals) so it's cached for performance.
        Returns:
            numpy.ndarray: 1D array with the mean x,y,(z) coordinates.
        """
        if self._midPoint is None:
            self._midPoint = self.findMidPoint()

        return self._midPoint

    def findMidPoint(self):
        """Compute the average (centroid) of corner coordinates.

        Returns:
            numpy.ndarray: 1D array with the mean x,y,(z) coordinates.
        """
        return np.mean(self._cords, axis=0)

    # --- neighbor computations -----------------------------------------

    @property
    def ngb(self):
        """Return list of neighbor cell IDs touching this cell.

        The list is computed lazily by 'findNGB'. A neighbor is defined as
        another cell sharing two or more corner points (i.e. a shared edge).
        Returns:
            list: list of integer cell IDs representing neighbors.
        """
        if self._ngb is None:
            try:
                self._ngb = self.findNGB(getattr(self._msh, "cells", None))
            except Exception:
                # Keep simulation robust on unexpected errors
                self._ngb = []
        return self._ngb

    def findNGB(self, allCells):
        """Populate neighbor relationships for this cell.

        Algorithm and rationale:
        - Build a mapping from point coordinate -> list of cell IDs that
          include that point. Cells that share two or more points are
          considered neighbors (sharing an edge). Building a point->cells
          map allows us to count shared points efficiently.
        - If a mesh object is available, we cache 'point->cells' and
          'id->cell' maps on the mesh so subsequent calls are O(1) lookups
          instead of scanning all cells repeatedly.

        Args:
            allCells: list of all cells in the mesh. 

        Effects:
        - This method mutates both this cell's '_ngb' list and the neighbor
          cell's '_ngb' to ensure the relationship is bidirectional.
        

        """

        # Try to use mesh-level cached maps if possible
        msh = getattr(self, "_msh", None)

        # If we have a mesh, prepare cached lookup structures there
        if msh is not None:

            if not hasattr(msh, "_point_to_cells"):                     #O(N*K) K average points per cell
                pointMap = {}
                for cell in allCells:                                   # for each cell in the mesh
                    for pungt in cell._cords:                           # for each corner point in the cell 
                        key = tuple(pungt)                              # use tuple as dict key
                        pointMap.setdefault(key, []).append(cell.id)    # point -> list of cell IDs

                
                msh._point_to_cells = pointMap                          # Cache

            pointMap = msh._point_to_cells

            if not hasattr(msh, "_id_to_cell"):                         #O(N)
                idMap = {cell.id: cell for cell in allCells}            # Cache for future neighbor queries
                msh._id_to_cell = idMap                                 # id -> cell object map

            idMap = msh._id_to_cell                                     # Cache

        else:
            # No mesh available: build maps locally
            pointMap = {}
            idMap = {cell.id: cell for cell in allCells}            # id -> cell object map

            for cell in allCells:                                   # for each cell in the mesh
                for pungt in cell._cords:                           # for each corner point in the cell
                    key = tuple(pungt)                              # use tuple as dict key
                    pointMap.setdefault(key, []).append(cell.id)    # point -> list of cell IDs

        # Count shared points between this cell and every other cell
        counts = {}

        for pungt in self._cords:                           # for each corner point in this cell
            for cellID in pointMap.get(tuple(pungt), []):   # for each cell sharing that point
                if cellID == self.id:                       # skip self
                    continue
                counts[cellID] = counts.get(cellID, 0) + 1  # count shared points

        # Cells sharing two or more points are neighbors (share an edge)
        for cellID, SheredPoints in counts.items():         # O(N) for each cell and its count of shared points
            if SheredPoints >= 2:                           # if they share an edge
                other = idMap.get(cellID)                   # get the other cell object
                if other is None:                           # skip if not found TODO ERROR?
                    continue

                if cellID not in self._ngb:                 # add Other cell to this cell's neighbor list
                    self._ngb.append(cellID)

                if self.id not in other._ngb:               # add this cell to the other cell's neighbor list
                    other._ngb.append(self.id)

    # --- normal vector computations -----------------------------------------

    @property  # TODO Brage: test getters and setters
    def scaledNormal(self):
        """Return outward-pointing normals for each neighbor edge.

        Each normal is scaled by the length of the shared edge. Normals
        point outward from this cell; the sign is chosen by testing which
        side contains the cell midpoint.
        Returns:
            list: list of numpy arrays representing scaled normals.
        """
        if self._scaledNormal is None:
            val = self.findScaledNormales(self._msh.cells)
            self._scaledNormal = np.array(val)
        return self._scaledNormal

    def findScaledNormales(self, allCells=None):
        """Compute outward normals for every neighbor edge.

        Implementation notes / why it works:
        - A shared edge is defined by the two corner points common to both
          cells. The edge vector d = B - A points along the shared edge.
        - A perpendicular vector n = [d_y, -d_x] is one of the two normals
          to the edge. To ensure the normal points outward from *this* cell
          we inspect the vector v from one shared point to this cell's
          midpoint: if the dot(n, v) > 0 then n points towards the cell
          interior and must be flipped.
        - The method returns a list of numpy arrays, one per neighbor.
        Args:
            allCells: list of all cells in the mesh.
        Returns:
            list: list of numpy arrays representing scaled normals.
        """

        msh = getattr(self, "_msh", None)

        if not allCells or not self.ngb or not msh:
            ValueError       #TODO ERROR?
        
        cellsDict = msh._id_to_cell                # O(1) lookup map from cell ID to cell object


        scaledNormals = []

        for ngbId in self.ngb:                      # for each neighbor cell ID
            ngbCell = cellsDict.get(ngbId)          # get neighbor cell object
            if ngbCell is None:                     # skip if not found TODO ERROR?
                continue

            # Intersection of point sets gives shared corner coordinates
            shared = self.pointSet & ngbCell.pointSet 
            if len(shared) < 2:
                # Not a full edge
                continue

            shared_iter = sorted(shared)                # get two shared points as sorted list
            A = np.array(shared_iter[0])                # first shared point
            B = np.array(shared_iter[1])                # second shared point

            # Edge vector and a perpendicular (normal) vector
            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])

            # Vector from edge to this cell's midpoint: used to orient n
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])

            # If n points into the cell, flip it so it points outward
            if np.dot(n, v) > 0:
                n = -n

            scaledNormals.append(n)

        self._scaledNormal = scaledNormals
        return self._scaledNormal

    # --- oil computations -----------------------------------------
    @property
    def oil(self):
        """Return the scalar oil concentration for this cell (0.0-1.0).

        Value is computed on first access by 'findOil' unless set by a
        caller. The setter clamps values into the [0.0, 1.0] range to avoid
        negative or >1.0 values which would be physically invalid for this
        simulation.
        Returns:
            float: scalar oil concentration in [0.0, 1.0].
        """
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter
    def oil(self, value):
        """
        Set and validate the oil concentration.
        Args:
            value: numeric scalar representing oil concentration.
        Raises:
            TypeError: when 'value' is not numeric.
        
        """
        self._oil = self._validate_and_clamp_oil(value)

    def findOil(self):  # TODO Brage: add ability to set oil function
        """Default oil distribution: gaussian-like blob for tests.

        The default uses the cell midpoint to return a scalar in 0..1. production use may override
        this to read from initial condition files.
        Returns:
            float: scalar oil concentration in [0.0, 1.0].
        """
        mp = self.midPoint
        return np.exp(-(np.linalg.norm(mp - np.array([0.35, 0.45, 0])) ** 2) / 0.01)

    def _validate_and_clamp_oil(self, value):
        """Validate numeric oil input and clamp to [0.0, 1.0].

        Rationale: tests and simulation code may accidentally set small
        negative values due to numerical error; clamping keeps the state
        physically meaningful while signalling (TODO) a warning.
        Args:
            value: numeric scalar representing oil concentration.
        Raises:
            TypeError: when 'value' is not numeric.
        Returns:
            float: clamped oil concentration in [0.0, 1.0].
        """
        try:
            v = float(value)
        except Exception:
            raise TypeError("oil value must be numeric")

        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0
        return v

    # --- public properties ----------------------------------------------

    @property
    def id(self):
        """Unique identifier for the cell.
        Returns:
            int: unique cell ID.
        """
        return self._id

    @id.setter
    def id(self, value):
        """Set the cell ID only if it wasn't set at construction.
        Args:
            value: integer cell ID.
        behaves:
            sets only if self._id is None.
        """
        # Allow id to be set only if it wasn't provided at construction
        if not self._id:
            self._id = value

    @property
    def cords(self):
        """List of corner coordinate arrays (in mesh coordinate space).
        Returns:
            list: list of numpy arrays representing corner coordinates.
        """
        return self._cords

    @property  # TODO Brage: test getters and setters
    def pointSet(self):
        """Return a set of corner coordinate tuples for fast intersection.

        Using tuples of coordinates allows quick set intersection operations
        when computing shared edges with neighbor cells.
        Returns:
            set: set of tuples representing corner coordinates.
        """
        if self._pointSet is None:
            self._pointSet = set(tuple(p) for p in self._cords)
        return self._pointSet
