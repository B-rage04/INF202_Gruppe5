import numpy as np
import numpy.testing as npt
import pytest

from src.Geometry.triangle import Triangle
from src.IO.LoadTOML import LoadTOML

configloader = LoadTOML()
config = configloader.loadConfigFile("Input\BaseSimConfig.toml")


# TODO: tests should be short and only test/assert one thing each
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

        # Avoid populating `cells` before creating triangle instances; create
        # an empty placeholder and fill it afterwards so initialization
        # doesn't cache incomplete state.
        self.cells = None
        t = Triangle(self, self.triangles[0], 0, config)
        self.cells = [t]


@pytest.fixture
def mesh():
    return MockMesh()


@pytest.fixture
def triangle(mesh):
    return Triangle(mesh, mesh.triangles[0], 0, config)


def test_triangle_coordinates(triangle):
    expected = [
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    ]

    for c, e in zip(triangle.cords, expected):
        npt.assert_array_equal(c, e)


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
        # minimal attribute used by Cell.scaledNormal during init
        self.cells = None
