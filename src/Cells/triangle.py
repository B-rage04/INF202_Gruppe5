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
        """Compatibility wrapper for callers using snake_case name."""
        return self.findScaledNormales(all_cells)

    def findScaledNormales(self, allCells=None):
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        cellsDict = {cell.id: cell for cell in allCells}
        walls = []

        for ngb_id in self.ngb:
            if ngb_id not in cellsDict:
                continue

            ngb_cell = cellsDict[ngb_id]

            # prefer cached point sets when available
            self_points = getattr(self, "_pointSet", None) or set(
                tuple(p) for p in self.cords
            )
            ngb_points = getattr(ngb_cell, "_pointSet", None) or set(
                tuple(p) for p in ngb_cell.cords
            )
            sharedPoints = list(self_points & ngb_points)

            if len(sharedPoints) >= 2:
                A = np.array(sharedPoints[0])
                B = np.array(sharedPoints[1])
                walls.append((A, B))

        scaledNormals = []
        for A, B in walls:
            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])

            if np.dot(n, v) > 0:
                n = -n

            scaledNormals.append(n)

        self._scaledNormal = scaledNormals
        return self._scaledNormal
