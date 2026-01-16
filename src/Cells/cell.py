from abc import ABC, abstractmethod
from logging import config

import numpy as np

from src.config import Config


class Cell(ABC):
    """
    General parent class for all cell types

    stores all values each cell needs

    with the exception of oil and newOil all values are fixed

    Notes:
    - This class assumes triangular cell geometry for area/neighbor calculations.
      Subclasses should implement `findArea` accordingly (see `Triangle`).
    """

    def __init__(self, msh, cell_points, cell_id, config: Config = None):
        self.type = None
        self._id = cell_id

        self._msh = msh
        # validate config: require Config instance
        if not isinstance(config, Config) and config is not None:
            raise TypeError("config must be a Config instance")
        self._config = config

        # internal state / caches
        self._cords = [msh.points[i] for i in cell_points]
        self._midPoint = None
        self._area = None
        self._scaledNormal = None
        self._pointSet = None
        self._ngb = []
        self._flow = None
        self._oil = None
        self.newOil = []

        # compute derived values using centralized update routines
        self._update_geometry()

    def _update_geometry(self):
        """Update all values that depend on cordinates in the right order"""
        try:
            self._midPoint = self.findMidPoint()
        except Exception:
            # TODO log warning?
            self._midPoint = None

        try:
            self._area = self.findArea()
        except Exception:
            # TODO log warning?
            self._area = None

        try:
            self._flow = np.array(self.findFlow())
        except Exception:
            # TODO log warning?
            self._flow = None

        try:
            self._oil = self.findOil()
        except Exception:
            # TODO log warning?
            self._oil = None

        try:
            self._isFishing = self.isFishingCheck(config)
        except Exception:
            # TODO log warning?
            self._isFishing = None

    # --- public properties ----------------------------------------------

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not self._id:
            self._id = value

    @property
    def cords(self):
        return self._cords

    @property  # TODO Brage: test getters and setters
    def pointSet(self):
        if self._pointSet is None:
            self._pointSet = set(tuple(p) for p in self._cords)
        return self._pointSet

    # --- area computations -----------------------------------------

    @property
    def area(self):
        return self._area

    @abstractmethod
    def findArea(self):
        """
        See child class for individual calculations
        """
        raise NotImplementedError()

    # --- midpoint computations -----------------------------------------

    @property
    def midPoint(self):
        if self._midPoint is None:
            self._midPoint = self.findMidPoint()
        return self._midPoint

    def findMidPoint(self):
        """
        Find the middle of the cell.

        Take all the corner points and average them
        This gives us the "center" point
        """
        return np.mean(self._cords, axis=0)

    # --- normal vector computations -----------------------------------------

    @property  # TODO Brage: test getters and setters
    def scaledNormal(self):
        if self._scaledNormal is None:
            if getattr(self, "_msh", None) is not None:
                val = self.findScaledNormales(getattr(self._msh, "cells", None))
            else:
                val = self.findScaledNormales()
            self._scaledNormal = np.array(val) if val is not None else np.array([])
        return self._scaledNormal

    def findScaledNormales(self, allCells=None):
        """
        Find the outward pointing normals for each neighboring cell.
        """

        # If we have no cells or no neighbors, there is nothing to do
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        # Try to get the mesh
        msh = getattr(self, "_msh", None)

        # Make a dictionary so we can quickly find a cell by its id
        if msh is not None and hasattr(msh, "_id_to_cell"):
            cellsDict = msh._id_to_cell
        else:
            cellsDict = {cell.id: cell for cell in allCells}

        # This will store all cells normals
        scaledNormals = []

        # Go through every neighbor cell
        for ngbId in self.ngb:

            # Get the neighbor cell
            ngbCell = cellsDict.get(ngbId)
            if ngbCell is None:
                continue

            # Find the points that both cells share
            # These two points form the shared edge (the stick they touch with)
            shared = self.pointSet & ngbCell.pointSet
            if len(shared) < 2:
                # If they don’t share a full edge, skip
                continue

            # Pick the two shared points in a stable order
            shared_iter = sorted(shared)
            A = np.array(shared_iter[0])
            B = np.array(shared_iter[1])

            # Make a vector along the shared edge (A → B)
            d = np.array([B[0] - A[0], B[1] - A[1]])

            # Turn that vector sideways to get a normal (an arrow)
            # Sideways means 90 degrees
            n = np.array([d[1], -d[0]])

            # Vector from the edge to the middle of *this* cell
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])

            # If the arrow points inside the cell, flip it
            # We want arrows pointing outward
            if np.dot(n, v) > 0:
                n = -n

            # Save the arrow
            scaledNormals.append(n)

        # Store and return all arrows
        self._scaledNormal = scaledNormals
        return self._scaledNormal

    # --- neighbor computations -----------------------------------------
    @property
    def ngb(self):
        return self._ngb

    def findNGB(self, allCells):
        """
        Find which cells are touching this cell.

        that means they share at least two points.
        """

        # Try to get the big mesh that holds all cells
        Localmsh = getattr(self, "_msh", None)

        # If we have a mesh, we can remember things so we don’t redo work
        if Localmsh is not None:

            # If the mesh does not yet know which cells touch each point
            if not hasattr(Localmsh, "_point_to_cells"):
                print("Building point-to-cells map for mesh")

                # Make a table:
                # point -> list of cell IDs that use this point
                pointMap = {}
                for cell in allCells:
                    for pungt in cell._cords:
                        key = tuple(pungt)
                        pointMap.setdefault(key, []).append(cell.id)

                # Save the table on the mesh for later reuse
                Localmsh._point_to_cells = pointMap

            pointMap = Localmsh._point_to_cells

            # If the mesh does not yet know how to find a cell by ID
            if not hasattr(Localmsh, "_id_to_cell"):
                print("Building id-to-cell map for mesh")

                # Make a table:
                # cell ID -> cell object
                idMap = {cell.id: cell for cell in allCells}
                Localmsh._id_to_cell = idMap

            idMap = Localmsh._id_to_cell

        else:
            # If there is no mesh, build everything locally

            pointMap = {}
            idMap = {cell.id: cell for cell in allCells}

            for cell in allCells:
                for pungt in cell._cords:
                    key = tuple(pungt)
                    pointMap.setdefault(key, []).append(cell.id)

        # Count how many points this cell shares with every other cell
        counts = {}

        for pungt in self._cords:
            for cellID in pointMap.get(tuple(pungt), []):

                # Ignore ourselves
                if cellID == self.id:
                    continue

                # Add one more shared point for this cell
                counts[cellID] = counts.get(cellID, 0) + 1

        # Any cell that shares 2 or more points is a neighbor
        for cellID, SheredPoints in counts.items():
            if SheredPoints >= 2:

                # Get the other cell object
                other = idMap.get(cellID)
                if other is None:
                    continue

                # Add neighbor relationship both ways
                if cellID not in self._ngb:
                    self._ngb.append(cellID)

                if self.id not in other._ngb:
                    other._ngb.append(self.id)

    # --- flow computations -----------------------------------------
    @property
    def flow(self):
        if self._flow is None:
            self._flow = np.array(self.findFlow())
        return self._flow

    @flow.setter
    def flow(self, value):
        try:
            arr = np.array(value)
        except Exception:
            raise TypeError("flow must be convertible to a numpy array")
        self._flow = arr

    def findFlow(self):  # TODO Brage: add ability to set flow function
        mp = self.midPoint
        return np.array([mp[1] - mp[0] * 0.2, -mp[0]])

    # --- oil computations -----------------------------------------
    @property
    def oil(self):
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter
    def oil(self, value):
        self._oil = self._validate_and_clamp_oil(value)

    def findOil(self):  # TODO Brage: add ability to set oil function
        mp = self.midPoint
        return np.exp(-(np.linalg.norm(mp - np.array([0.35, 0.45, 0])) ** 2) / 0.01)

    def _validate_and_clamp_oil(
        self, value
    ):  # TODO: this might be the wrong solution but I got an error that oil was set negatively
        try:
            v = float(value)
        except Exception:
            raise TypeError("oil value must be numeric")

        if v < 0.0:
            v = 0.0
            # TODO log warning?
        elif v > 1.0:
            v = 1.0
            # TODO log warning?
        return v

    # --- fishing zone check ----------------------------------------------
    @property
    def isFishing(self):
        return self._isFishing

    def isFishingCheck(self, config=None):
        cfg = config if config is not None else self._config
        if cfg is None:
            return False
        if isinstance(cfg, dict):
            cfg = Config.from_dict(cfg)

        fishxmin = cfg.geometry["borders"][0][0]
        fishxmax = cfg.geometry["borders"][0][1]
        fishymin = cfg.geometry["borders"][1][0]
        fishymax = cfg.geometry["borders"][1][1]
        x = self.midPoint[0]
        y = self.midPoint[1]
        if x is None or y is None:
            return False
        return fishxmin < x < fishxmax and fishymin < y < fishymax
