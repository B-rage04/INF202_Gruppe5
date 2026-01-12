import numpy as np

from src.Cells.cell import Cell


class Triangle(Cell):
    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "triangle"

    def find_area(self):
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area

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
