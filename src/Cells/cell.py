from abc import ABC, abstractmethod

import numpy as np


class Cell(ABC):

    """
    General parent class for all cell types
    
    stores all values each cell needs

    with the exception of oil and newOil all values are fixed
    """

    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        self.cords = [msh.points[i] for i in cell_points]
        self.midpoint = self._find_midpoint()
        self.area = self._find_area()
        self.scaledNormal = []
        self.ngb = []
        self.flow = self._find_flow()
        self.oil = self._find_oil()
        self.newOil = []
        self._pointSet = None

    @abstractmethod
    def _find_area(self):
        pass
        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def _find_midpoint(self):  # TODO: get midpoint
        """
        Find the midpoint of cell
        """
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

    def _find_flow(self):  # TODO: add ability to set flow function
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

        # TODO: if has attribute return it
        # TODO: else calculate it and set and return it

    def _find_oil(self):  # TODO: add ability to set oil function
        return np.exp(
            -(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )