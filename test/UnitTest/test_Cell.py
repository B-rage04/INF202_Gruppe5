import numpy as np
import numpy.testing as npt
import pytest

from src.Cells.triangle import Triangle


class DummyMesh:
    def __init__(self):
        self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        self.triangles = np.array([[0, 1, 2]])


@pytest.fixture
def triangle():
    msh = DummyMesh()
    return Triangle(msh, msh.triangles[0], 0)


def test_flow(triangle):
    cx, cy = triangle.midPoint[0], triangle.midPoint[1]
    expected_flow = np.array([cy - cx * 0.2, -cx])
    npt.assert_allclose(triangle.flow, expected_flow)


def test_oil(triangle):
    center = triangle.midPoint
    reference = np.array([0.35, 0.45, 0.0])
    expected_oil = np.exp(-(np.linalg.norm(center - reference) ** 2) / 0.01)
    assert triangle.oil == pytest.approx(expected_oil)
