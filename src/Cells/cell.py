from abc import ABC, abstractmethod

import numpy as np


class Cell(ABC):
    """
    General parent class for all cell types

    stores all values each cell needs
    """

    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        self.cords = [msh.points[i] for i in cell_points]
        self.midpoint = self.findMidpoint()
        self.area = self.findArea()
        self.scaledNormal = []
        self.ngb = []
        self.flow = self.findFlow()
        self.oil = self.findOil()
        self.newOil = []

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
        self._cords = list(value)
        self._midPoint = None
        self._area = None
        self._scaledNormal = None
        self._pointSet = None
        self._flow = None
        self._oil = None

    @property
    def midPoint(self):
        if self._midPoint is None:
            if len(self._cords) == 0:
                self._midPoint = np.array([0.0, 0.0, 0.0])
            else:
                self._midPoint = np.mean(self._cords, axis=0)
        return self._midPoint

    @property
    def area(self):
        if self._area is None:
            self._area = self.findArea()
        return self._area

    @property
    def scaledNormal(self):
        if self._scaledNormal is None:
            val = self.findScaledNormales()
            # ensure numpy array
            self._scaledNormal = np.array(val) if val is not None else np.zeros(3)
        return self._scaledNormal

    @property
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
        self._flow = np.array(value)

    @property
    def oil(self):
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter
    def oil(self, value):
        self._oil = value

    @abstractmethod
    def findArea(self):
        pass
        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def findMidpoint(self):  # TODO: get midpoint
        if len(self.cords) == 0:
            return np.array([0, 0, 0])
        return np.mean(self.cords, axis=0)

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def find_scaled_normales(self, all_cells=None):
        if not all_cells or not self.ngb:
            self.scaled_normal = []
            return self.scaled_normal

        cells_dict = {cell.id: cell for cell in all_cells}
        walls = []

        for ngb_id in self.ngb:
            if ngb_id not in cells_dict:
                continue

            ngb_cell = cells_dict[ngb_id]

            self_points = set(
                tuple(p) for p in self.cords
            )  # TODO: use _point_set since we already have it
            ngb_points = set(tuple(p) for p in ngb_cell.cords)
            shared_points = list(self_points & ngb_points)

            if len(shared_points) >= 2:
                A = np.array(shared_points[0])
                B = np.array(shared_points[1])
                walls.append((A, B))

        scaled_normals = []
        for A, B in walls:
            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midpoint[0] - A[0], self.midpoint[1] - A[1]])

            if np.dot(n, v) > 0:
                n = -n

            scaled_normals.append(n)

        self.scaled_normal = scaled_normals
        return self.scaled_normal





    def find_ngb(self, allCells):
        if not hasattr(self, "_point_set") or self._pointSet is None:
            self._pointSet = set(
                tuple(p) for p in self.cords
            )  # TODO: worng notation _**** for a public get set("just if none") variable.

        for other in allCells:
            if other.id == self.id:
                continue
            otherPointSet = getattr(other, "_pointSet", None)
            if otherPointSet is None:
                otherPointSet = set(tuple(p) for p in other.cords)
                other.pointSet = otherPointSet

            if len(self._pointSet & otherPointSet) >= 2:
                if other.id not in self._ngb:
                    self._ngb.append(other.id)
                if self.id not in other._ngb:
                    other._ngb.append(self.id)

    def _find_flow(self):  # TODO: add ability to set flow function
        """
        Finds the flow direction in cell
        """
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def _find_oil(self):
        """
        Finds initial value for oil in cell
        """
        return np.exp(
            -(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )