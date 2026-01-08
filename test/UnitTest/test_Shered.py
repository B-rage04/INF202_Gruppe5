import numpy as np
import numpy.testing as npt
import pytest

from src.Cells.cell import Cell
from src.Cells.triangle import Triangle


class MockMesh:
    def __init__(self):
        # Define 3 points forming a right triangle in the XY plane
        self.points = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        )

        # Single triangle using all three points
        self.triangles = np.array([[0, 1, 2]])


@pytest.fixture
def mesh():
    return MockMesh()


@pytest.fixture
def cell(mesh):
    return Cell(mesh, 0)


@pytest.fixture
def triangle(mesh):
    return Triangle(mesh, 0)


def test_triangle_coordinates(triangle):
    expected = [
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    ]

    for c, e in zip(triangle.cords, expected):
        npt.assert_array_equal(c, e)


class DummyVisualizer:
    def __init__(self, msh):
        self.msh = msh
        self.last_plotted = None

    def plotting(self, oil_vals):
        self.last_plotted = list(oil_vals)
