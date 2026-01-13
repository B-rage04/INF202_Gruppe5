import numpy as np
import numpy.testing as npt
import pytest

from src.Cells.cell import Cell
from src.Cells.triangle import Triangle


# TODO: test shood be short and only test/asert one thing each
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

        # Provide ready-made cells for Simulation (list of Cell objects)
        self.cells = [Triangle(self, self.triangles[0], 0)]


@pytest.fixture
def mesh():
    return MockMesh()


@pytest.fixture
def cell(mesh):
    return Cell(mesh, mesh.triangles[0], 0)


@pytest.fixture
def triangle(mesh):
    return Triangle(mesh, mesh.triangles[0], 0)


def test_triangle_coordinates(triangle):
    expected = [
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    ]

    for c, e in zip(triangle.cords, expected):
        npt.assert_array_equal(c, e)


class DummyVisualizer:
    def __init__(self, mesh):
        self.mesh = mesh
        self.last_plotted = None

    def plotting(self, oilVals, run=None, step=None, **kwargs):
        self.last_plotted = list(oilVals)


class MockMeshTriangles:
    def __init__(self):
        self.points = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        )
