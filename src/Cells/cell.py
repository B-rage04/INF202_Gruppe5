import time
from abc import ABC, abstractmethod

import numpy as np
from tqdm import tqdm
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
        self._flow = np.array(self.findFlow())
        self._oil = self.findOil()
        self._isFishing = self.isFishingCheck(config)

    

    # --- validate -----------------------------------------

    def _validate_and_clamp_oil(self, value):  # TODO: this might be the wrong solution but I got an error that oil was set negatively
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
    def isFishing(self):
        return self._isFishing

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def cords(self):
        return self._cords

    @cords.setter
    def cords(self, value):
        self._update_cords(value)

    @property
    def midPoint(self):
        return self._midPoint

    @property
    def area(self):
        return self._area

    @property  # TODO Brage: test getters and setters
    def scaledNormal(self):
        if self._scaledNormal is None:
            if getattr(self, "_msh", None) is not None:
                val = self.findScaledNormales(getattr(self._msh, "cells", None))
            else:
                val = self.findScaledNormales()
            self._scaledNormal = np.array(val) if val is not None else np.array([])
        return self._scaledNormal

    @property  # TODO Brage: test getters and setters
    def pointSet(self):
        if self._pointSet is None:
            self._pointSet = set(tuple(p) for p in self._cords)
        return self._pointSet

    @property
    def ngb(self):
        return self._ngb

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

    @property
    def oil(self):
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter 
    def oil(self, value):
        self._oil = self._validate_and_clamp_oil(value)

    @abstractmethod
    def findArea(self):
        """
        See child class for individual calculations
        """
        raise NotImplementedError()

    # --- geometric computations -----------------------------------------
    def findMidPoint(self):  # TODO Brage: test this
        return np.mean(self._cords, axis=0)

    def findScaledNormales(self, allCells=None):
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        msh = getattr(self, "_msh", None)

        # Reuse mesh-level id map if available to avoid rebuilding per cell
        if msh is not None and hasattr(msh, "_id_to_cell"):
            cellsDict = msh._id_to_cell
        else:
            cellsDict = {cell.id: cell for cell in allCells}

        # cache point sets
        selfPoints = getattr(self, "_pointSet", None)
        if selfPoints is None:
            selfPoints = set(tuple(p) for p in self._cords)
            self._pointSet = selfPoints

        scaledNormals = []

        for ngbId in self.ngb:

            ngbCell = cellsDict.get(ngbId)
            if ngbCell is None:
                continue

            ngbPoints = getattr(ngbCell, "_pointSet", None)
            if ngbPoints is None:
                ngbPoints = set(tuple(p) for p in ngbCell._cords)
                ngbCell._pointSet = ngbPoints

            # find up to two shared points without creating intermediate lists
            shared = selfPoints & ngbPoints
            if len(shared) < 2:
                continue
            # deterministic ordering: sort for reproducibility
            shared_iter = sorted(shared)
            A = np.array(shared_iter[0])
            B = np.array(shared_iter[1])

            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])
            if np.dot(n, v) > 0:
                n = -n
            scaledNormals.append(n)

        self._scaledNormal = scaledNormals
        return self._scaledNormal

    def findNGB(self, allCells):
        Localmsh = getattr(self, "_msh", None)

        # Build or reuse a mapping from point (tuple) -> list of cell ids
        if Localmsh is not None:
            if not hasattr(Localmsh, "_point_to_cells"):
                # create a table that gives all cell IDs that share a point
                pointMap = {}
                for cell in allCells:
                    for pungt in cell._cords:
                        key = tuple(pungt)
                        pointMap.setdefault(key, []).append(cell.id)
                Localmsh._point_to_cells = pointMap
            pointMap = Localmsh._point_to_cells

            if not hasattr(Localmsh, "_id_to_cell"):
                # create a table that gives the cell object from an ID
                idMap = {cell.id: cell for cell in allCells}
                Localmsh._id_to_cell = idMap
            idMap = Localmsh._id_to_cell
        else:
            pointMap = {}
            idMap = {cell.id: cell for cell in allCells}
            for cell in allCells:
                for pungt in cell._cords:
                    key = tuple(pungt)
                    pointMap.setdefault(key, []).append(cell.id)

        # Find IDs of neighbor cells that have shared points
        counts = {}
        for pungt in self._cords:
            for cellID in pointMap.get(tuple(pungt), []):
                if cellID == self.id:
                    continue
                counts[cellID] = counts.get(cellID, 0) + 1

        # Any cell sharing two or more points is a neighbor
        for cellID, SheredPoints in counts.items():
            if SheredPoints >= 2:
                other = idMap.get(cellID)
                if other is None:
                    continue
                if cellID not in self._ngb:
                    self._ngb.append(cellID)
                if self.id not in other._ngb:
                    other._ngb.append(self.id)

    def findFlow(self):  # TODO Brage: add ability to set flow function
        mp = self._midPoint if self._midPoint is not None else self.findMidPoint()
        return np.array([mp[1] - mp[0] * 0.2, -mp[0]])

    def findOil(self):  # TODO Brage: add ability to set oil function
        mp = self._midPoint if self._midPoint is not None else self.findMidPoint()
        return np.exp(-(np.linalg.norm(mp - np.array([0.35, 0.45, 0])) ** 2) / 0.01)

    def _update_cords(self, value):
        try:
            pts = [np.array(v) for v in value]
        except Exception:
            raise TypeError("cords must be an iterable of numeric points")
        self._cords = pts
        self.invalidate_all_caches()

    def _update_geometry(self):
        try:
            self._midPoint = self.findMidPoint()
        except Exception:
            self._midPoint = None
        try:
            self._area = self.findArea()
        except Exception:
            self._area = None

    def invalidate_geometry_cache(self):
        self._midPoint = None
        self._area = None
        self._scaledNormal = None
        self._pointSet = None

    def invalidate_physics_cache(self):
        self._flow = None
        self._oil = None

    def invalidate_all_caches(self):
        self.invalidate_geometry_cache()
        self.invalidate_physics_cache()

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
        x = self._midPoint[0] if self._midPoint is not None else None
        y = self._midPoint[1] if self._midPoint is not None else None
        if x is None or y is None:
            return False
        return fishxmin < x < fishxmax and fishymin < y < fishymax
