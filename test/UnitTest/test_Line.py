import numpy as np
import pytest

from src.Cells.cell import Cell
from src.Cells.line import Line


def test_line_initialization_and_area1():  # TODO: Fix names and Fixtures of "repeat" tests
    class DummyMesh:
        def __init__(self):
            self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    msh = DummyMesh()
    ln = Line(msh, [0, 1], 0)
    assert ln.type == "line"


def test_line_initialization_and_area2():  # TODO: Fix names and Fixtures of "repeat" tests
    class DummyMesh:
        def __init__(self):
            self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    msh = DummyMesh()
    ln = Line(msh, [0, 1], 0)
    assert ln.findArea() is None


def test_line_initialization_and_area3():  # TODO: Fix names and Fixtures of "repeat" tests
    class DummyMesh:
        def __init__(self):
            self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    msh = DummyMesh()
    ln = Line(msh, [0, 1], 0)
    assert ln.type == "line"


def test_line_is_subclass():
    assert issubclass(Line, Cell)
