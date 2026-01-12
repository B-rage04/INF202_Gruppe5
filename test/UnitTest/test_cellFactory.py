from types import SimpleNamespace

import numpy as np

from src.Cells.cellFactory import CellFactory


def test_cell_factory_with_cells_list():
    class DummyMesh:
        def __init__(self):
            self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
            # simulate meshio CellBlock-like object using SimpleNamespace
            self.cells = [SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]]))]

    msh = DummyMesh()
    cells = CellFactory(msh)
    assert len(cells) == 1
    assert cells[0].type == "triangle"


def test_cell_factory_with_triangle_and_line():
    class DummyMesh:
        def __init__(self):
            self.points = np.array(
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]]
            )
            self.cells = [
                SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]])),
                SimpleNamespace(type="line", data=np.array([[1, 3]])),
            ]

    msh = DummyMesh()
    cells = CellFactory(msh)
    # should create one triangle and one line cell
    types = sorted([c.type for c in cells])
    assert types == ["line", "triangle"]
