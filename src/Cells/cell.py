from abc import ABC, abstractmethod

import numpy as np
from tqdm import tqdm


class Cell(ABC):
    """
    General parent class for all cell types

    stores all values each cell needs

    with the exception of oil and newOil all values are fixed
    """

    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        # keep reference to mesh so we can compute geometry against all cells
        self._msh = msh
        # set backing fields directly to avoid invoking property setters
        self._cords = [msh.points[i] for i in cell_points]
        self._midPoint = self.findMidpoint()
        self._area = self.findArea()
        self._scaledNormal = None
        self._pointSet = None
        self._ngb = []
        self._flow = np.array(self.findFlow())
        self._oil = self.findOil()
        self.newOil = []

    @property  # TODO: test getters and setters
    def id(self):
        return self._id

    @id.setter  # TODO: test getters and setters
    def id(self, value):
        self._id = value

    @property  # TODO: test getters and setters
    def cords(self):
        return self._cords

    @cords.setter  # TODO: test getters and setters
    def cords(self, value):
        self._cords = list(value)
        self._midPoint = None
        self._area = None
        self._scaledNormal = None
        self._pointSet = None
        self._flow = None
        self._oil = None

    @property  # TODO: test getters and setters
    def midPoint(self):
        if self._midPoint is None:
            if len(self._cords) == 0:
                self._midPoint = np.array([0.0, 0.0, 0.0])
            else:
                self._midPoint = np.mean(self._cords, axis=0)
        return self._midPoint

    @property  # TODO: test getters and setters
    def area(self):
        if self._area is None:
            self._area = self.findArea()
        return self._area

    @property  # TODO: test getters and setters
    def scaledNormal(self):
        if self._scaledNormal is None:
            # try to compute scaled normals with access to all cells when available
            if getattr(self, "_msh", None) is not None:
                val = self.findScaledNormales(self._msh.cells)
            else:
                val = self.findScaledNormales()
            # ensure numpy array
            self._scaledNormal = np.array(val) if val is not None else np.zeros(3)
        return self._scaledNormal

    @property  # TODO: test getters and setters
    def pointSet(self):
        if self._pointSet is None:
            self._pointSet = set(tuple(p) for p in self._cords)
        return self._pointSet

    @property  # TODO: test getters and setters
    def ngb(self):
        return self._ngb

    @property  # TODO: test getters and setters
    def flow(self):
        if self._flow is None:
            self._flow = np.array(self.findFlow())
        return self._flow

    @flow.setter  # TODO: test getters and setters
    def flow(self, value):
        self._flow = np.array(value)

    @property
    def oil(self):
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter  # TODO: test getters and setters
    def oil(self, value):  # can not be more than x
        self._oil = value

    @abstractmethod
    def findArea(self):  # TODO: test this
        pass
        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def findMidpoint(self):  # TODO: get midpoint # TODO: test this
        if len(self.cords) == 0:
            return np.array([0, 0, 0])
        return np.mean(self.cords, axis=0)

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def findScaledNormales(self, all_cells=None):  # TODO: all_cells?
        self._scaledNormal = []
        return self._scaledNormal

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def findNGB(self, allCells):
        for other in tqdm(
            allCells,
            desc=f"Cell {self.id:04d} topology",
            unit="cell",
            leave=False,
            colour="green",
            ascii="-#",
            disable=len(allCells) < 100,
        ):
            if other.id == self.id:
        for other in allCells:
            if other.id == self.id:  # TODO: test this
                continue
            otherPointSet = getattr(
                other, "_pointSet", None
            )  # uses wrong notation _**** # TODO: test this
            if otherPointSet is None:
                otherPointSet = set(tuple(p) for p in other.cords)
                other._pointSet = otherPointSet
            # ensure this cell has a point set cached
            selfPointSet = getattr(self, "_pointSet", None)
            if selfPointSet is None:
                self._pointSet = set(tuple(p) for p in self.cords)
                selfPointSet = self._pointSet

            if len(selfPointSet & otherPointSet) >= 2:
                if other.id not in self._ngb:
                    self._ngb.append(other.id)  # TODO: test this
                if self.id not in other._ngb:
                    other._ngb.append(self.id)  # TODO: test this

    def findFlow(self):  # TODO: add ability to set flow function
        return np.array(
            [self.midPoint[1] - self.midPoint[0] * 0.2, -self.midPoint[0]]
        )  # TODO: test this

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def findOil(self):  # TODO: add ability to set oil function
        return np.exp(
            -(np.linalg.norm(self.midPoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )  # TODO: test this
