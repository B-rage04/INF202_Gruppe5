import numpy as np
import pytest

from src.Cells.triangle import Triangle
from src.LoadTOML import LoadTOML

from .test_Shered import MockMeshTriangles

configloader = LoadTOML()
config = configloader.loadConfigFile("Input\BaseSimConfig.toml")


@pytest.fixture
def triangles():
    mesh = MockMeshTriangles()
    t0 = Triangle(mesh, [0, 1, 2], 0, config)
    t1 = Triangle(mesh, [1, 2, 3], 1, config)

    cells = [t0, t1]
    for c in cells:
        c.findNGB(cells)

    return cells


def test_triangle_t1_neighbor_to_t0(triangles):
    t0, t1 = triangles

    assert t1.id in t0.ngb


def test_triangle_t0_neighbor_to_t1(triangles):
    t0, t1 = triangles

    assert t0.id in t1.ngb


def test_triangle_t1_neighbor_to_t0_with_ID(triangles):
    t0, t1 = triangles

    assert t1.ngb.count(t0.id) == 1


def test_triangle_t0_neighbor_to_t1_with_ID(triangles):
    t0, t1 = triangles

    assert t0.ngb.count(t1.id) == 1
