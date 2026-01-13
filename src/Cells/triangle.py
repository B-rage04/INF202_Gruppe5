import numpy as np
from tqdm import tqdm

from src.Cells.cell import Cell


class Triangle(Cell):
    """
    Cell of type "triangle"
    """

    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "triangle"

    def findArea(self):
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area

    def findScaledNormales(self, allCells=None):
        """Compatibility wrapper for callers using snake_case name."""
        return self.findScaledNormales(allCells)

    def findScaledNormales(self, allCells=None):
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        cellsDict = {cell.id: cell for cell in allCells}
        walls = []

        for ngbId in tqdm(
            self.ngb,
            desc=f"Triangle {self.id:04d} normals",
            unit="ngb",
            leave=False,
            colour="cyan",
            ascii="-#",
            disable=len(self.ngb) < 10,
        ):
            if ngbId not in cellsDict:
                continue

            ngbCell = cellsDict[ngbId]

            # prefer cached point sets when available
            selfPoints = getattr(self, "_pointSet", None) or set(
                tuple(p) for p in self.cords
            )
            ngbPoints = getattr(ngbCell, "_pointSet", None) or set(
                tuple(p) for p in ngbCell.cords
            )
            sharedPoints = list(selfPoints & ngbPoints)

            if len(sharedPoints) >= 2:
                A = np.array(sharedPoints[0])
                B = np.array(sharedPoints[1])
                walls.append((A, B))

        scaledNormals = []
        for A, B in tqdm(
            walls,
            desc="Scaling wall normals",
            unit="wall",
            leave=False,
            colour="blue",
            ascii="-#",
            disable=len(walls) < 5,
        ):
            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])

            if np.dot(n, v) > 0:
                n = -n

            scaledNormals.append(n)

        self._scaledNormal = scaledNormals
        return self._scaledNormal
