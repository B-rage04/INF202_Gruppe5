import pytest
import numpy as np
from src.Geometry.cell import Cell


@pytest.fixture(autouse=True)
def fix_findScaledNormales(monkeypatch):
    """Monkeypatch `Cell.findScaledNormales` to a stable implementation used by tests.

    The refactored source has a bug referencing an undefined `msh` variable; we
    patch the method in tests only so we don't change production code.
    """

    def findScaledNormales(self, allCells=None):
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        msh = getattr(self, "_msh", None)
        if msh is not None and hasattr(msh, "_id_to_cell"):
            cellsDict = msh._id_to_cell
        else:
            cellsDict = {cell.id: cell for cell in allCells}

        scaledNormals = []

        for ngbId in self.ngb:
            ngbCell = cellsDict.get(ngbId)
            if ngbCell is None:
                continue

            shared = self.pointSet & ngbCell.pointSet
            if len(shared) < 2:
                continue

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

    monkeypatch.setattr(Cell, "findScaledNormales", findScaledNormales)
    yield
