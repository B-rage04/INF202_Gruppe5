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
        self.new_oil = 0.0
    
    def __str__(self):
        return (f"Cell(id={self.id}, type={self.type}, midpoint={self.midpoint}, "
                f"area={self.area:.4f}, flow={self.flow}, oil={self.oil:.4f}, "
                f"new_oil={self.new_oil:.4f}, neighbors={self.ngb}, "
                f"scaled_normal={self.scaled_normal})")

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
        return np.array([self.midpoint[1] - (self.midpoint[0] * 0.2), -self.midpoint[0]])

    def find_oil(self):
        return np.exp(
            -(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )
