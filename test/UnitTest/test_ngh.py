import numpy as np
import pytest

from src.Cells.triangle import Triangle

from .test_Shered import MockMeshTriangles


@pytest.fixture
def triangles():
    mesh = MockMeshTriangles()
    t0 = Triangle(mesh, [0, 1, 2], 0)
    t1 = Triangle(mesh, [1, 2, 3], 1)

    cells = [t0, t1]
    for c in cells:
        c.findNGB(cells)

    return cells


def test_triangles_are_neighbors(triangles):
    t0, t1 = triangles

    assert t1.id in t0.ngb
    assert t0.id in t1.ngb

    assert t0.ngb.count(t1.id) == 1
    assert t1.ngb.count(t0.id) == 1

    assert hasattr(t0, "_pointSet") and isinstance(t0._pointSet, set)
    assert hasattr(t1, "_pointSet") and isinstance(t1._pointSet, set)
