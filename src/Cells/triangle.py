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
            selfPoints = set(tuple(p) for p in self.cords)
            self._pointSet = selfPoints

        scaledNormals = []
        disable_ngb_tqdm = len(self.ngb) < 10

        for ngbId in tqdm(
            self.ngb,
            desc=f"Triangle {self.id:04d} normals",
            unit="ngb",
            leave=False,
            colour="cyan",
            ascii="-#",
            disable=disable_ngb_tqdm,
        ):
            ngbCell = cellsDict.get(ngbId)
            if ngbCell is None:
                continue

            ngbPoints = getattr(ngbCell, "_pointSet", None)
            if ngbPoints is None:
                ngbPoints = set(tuple(p) for p in ngbCell.cords)
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
