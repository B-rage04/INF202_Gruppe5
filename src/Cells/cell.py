from abc import ABC, abstractmethod

import numpy as np


class Cell(ABC):
    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        self.cords = [msh.points[i] for i in cell_points]
        self.midpoint = self.find_midpoint()
        self.area = self.find_area()
        self.scaled_normal = []
        self.ngb = []
        self.flow = self.find_flow()
        self.oil = self.find_oil()
        self.new_oil = None

    @abstractmethod
    def find_area(self):
        pass

    def find_midpoint(self):
        if len(self.cords) == 0:
            return np.array([0, 0, 0])
        return np.mean(self.cords, axis=0)

    def find_scaled_normales(self, all_cells=None):
        self.scaled_normal = []
        return self.scaled_normal

    def find_ngb(self, all_cells):
        if not hasattr(self, "_point_set") or self._point_set is None:
            self._point_set = set(tuple(p) for p in self.cords)

        for other in all_cells:
            if other.id == self.id:
                continue

            other_point_set = getattr(other, "_point_set", None)
            if other_point_set is None:
                other_point_set = set(tuple(p) for p in other.cords)
                other._point_set = other_point_set

            if len(self._point_set & other_point_set) >= 2:
                if other.id not in self.ngb:
                    self.ngb.append(other.id)
                if self.id not in other.ngb:
                    other.ngb.append(self.id)

    def find_flow(self):
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

    def find_oil(self):
        return np.exp(
            -(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )

    def update_oil(self, ngb, delta_time):

        for ngb in self.ngb:
            self.new_oil = self.oil - delta_time / self.area * self.flux(ngb)

    def flux(self, ngb):
        flow_avg = (self.flow + ngb.flow) / 2
        if np.dot(flow_avg, self.scaled_normal) > 0:
            return self.oil * np.dot(flow_avg, self.scaled_normal)
        else:
            return ngb.oil * np.dot(flow_avg, self.scaled_normal)
