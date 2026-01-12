from abc import ABC, abstractmethod

import numpy as np


class Cell(ABC):
    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        self.cords = [msh.points[i] for i in cell_points]
        self.midpoint = self.find_midpoint()
        self.area = self.find_area()
        self.scaledNormal = []
        self.ngb = []
        self.flow = self.find_flow()
        self.oil = self.find_oil()
        self.newOil = []
        self._pointSet = None

    @abstractmethod
    def find_area(self):
        pass
        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def find_midpoint(self):  # TODO: get midpoint
        if len(self.cords) == 0:
            return np.array([0, 0, 0])
        return np.mean(self.cords, axis=0)

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def find_scaled_normales(self, all_cells=None):  # TODO: all_cells?
        self.scaledNormal = []
        return self.scaledNormal

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def find_ngb(self, all_cells):
        if not hasattr(self, "_point_set") or self._pointSet is None:
            self._pointSet = set(
                tuple(p) for p in self.cords
            )  # TODO: worng notation _**** for a public get set("just if none") variable.

        for other in all_cells:
            if other.id == self.id:
                continue

            other_point_set = getattr(other, "_point_set", None)
            if other_point_set is None:
                other_point_set = set(tuple(p) for p in other.cords)
                other._point_set = other_point_set

            if len(self._pointSet & other_point_set) >= 2:
                if other.id not in self.ngb:
                    self.ngb.append(other.id)
                if self.id not in other.ngb:
                    other.ngb.append(self.id)

    def find_flow(self):  # TODO: add ability to set flow function
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def find_oil(self):  # TODO: add ability to set oil function
        return np.exp(
            -(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )

    def flux(self, ngb):  # TODO: add ability to set flux function
        flow_avg = (self.flow + ngb.flow) / 2
        if np.dot(flow_avg, self.scaledNormal) > 0:
            return self.oil * np.dot(flow_avg, self.scaledNormal)
        else:
            return ngb.oil * np.dot(flow_avg, self.scaledNormal)
