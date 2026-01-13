import numpy as np
import pytest

from src.Cells.cell import Cell
from src.Cells.line import Line


def test_line_initialization_and_area():
    class DummyMesh:
        def __init__(self):
            self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    msh = DummyMesh()
    ln = Line(msh, [0, 1], 0)
    assert ln.type == "line"
    assert ln.findArea() is None
    assert ln.area is None


def test_line_is_subclass():
    assert issubclass(Line, Cell)
