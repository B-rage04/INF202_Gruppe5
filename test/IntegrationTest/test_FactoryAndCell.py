"""Integration tests for CellFactory and Cell objects.

These tests build a tiny fake mesh with four triangular cells that share
edges in the pattern: 0-1, 1-2, 2-3, 3-1. Tests use fixtures and ensure
each test contains a single assert (parametrized across the four cells).
"""

import numpy as np
import pytest


class _CellBlock:
    def __init__(self, type_, data):
        self.type = type_
        self.data = data


class _FakeMesh:
    def __init__(self, points, cells):
        # points: list of coordinate iterables
        # cells: list of _CellBlock
        self.points = [np.array(p) for p in points]
        self.cells = cells


@pytest.fixture(scope="module")
def mesh_four():
    # Points (x, y, z)
    pts = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.5, 1.0, 0.0],
        [2.0, 0.0, 0.0],
        [2.5, 1.0, 0.0],
    ]

    # Four triangular cells arranged so that neighbor relationships are:
    # 0-1, 1-2, 2-3, 3-1
    cells_data = [
        [0, 1, 2],  # cell 0
        [1, 2, 3],  # cell 1
        [2, 3, 4],  # cell 2
        [1, 3, 4],  # cell 3
    ]

    block = _CellBlock("triangle", cells_data)
    return _FakeMesh(pts, [block])


@pytest.fixture(scope="module")
def cells(mesh_four):
    from src.Geometry.cellFactory import CellFactory

    factory = CellFactory(mesh_four, config=None)
    return factory()


@pytest.mark.parametrize("idx,expected", [(0, 0), (1, 1), (2, 2), (3, 3)])
def test_id(cells, idx, expected):
    assert cells[idx].id == expected


@pytest.mark.parametrize("idx,expected", [(0, "triangle"), (1, "triangle"), (2, "triangle"), (3, "triangle")])
def test_type(cells, idx, expected):
    assert cells[idx].type == expected


@pytest.mark.parametrize("idx,expected_idxs", [
    (0, [0, 1, 2]),
    (1, [1, 2, 3]),
    (2, [2, 3, 4]),
    (3, [1, 3, 4]),
])
def test_cords(cells, idx, expected_idxs):
    expected = [tuple(p) for p in cells[0]._msh.points]  # placeholder to access points
    # Build expected cords for the given cell from mesh points
    mesh_pts = cells[idx]._msh.points
    exp = [tuple(mesh_pts[i]) for i in expected_idxs]
    assert [tuple(c) for c in cells[idx].cords] == exp


@pytest.mark.parametrize("idx,expected_idxs", [
    (0, [0, 1, 2]),
    (1, [1, 2, 3]),
    (2, [2, 3, 4]),
    (3, [1, 3, 4]),
])
def test_pointSet(cells, idx, expected_idxs):
    mesh_pts = cells[idx]._msh.points
    exp = set(tuple(mesh_pts[i]) for i in expected_idxs)
    assert cells[idx].pointSet == exp


def _triangle_area(pts):
    # pts: list/iterable of three (x,y,...) points
    x0, y0 = pts[0][0], pts[0][1]
    x1, y1 = pts[1][0], pts[1][1]
    x2, y2 = pts[2][0], pts[2][1]
    return 0.5 * abs((x0 - x2) * (y1 - y0) - (x0 - x1) * (y2 - y0))


@pytest.mark.parametrize("idx,expected_idxs", [
    (0, [0, 1, 2]),
    (1, [1, 2, 3]),
    (2, [2, 3, 4]),
    (3, [1, 3, 4]),
])
def test_area(cells, idx, expected_idxs):
    mesh_pts = cells[idx]._msh.points
    pts = [mesh_pts[i] for i in expected_idxs]
    exp = _triangle_area(pts)
    assert cells[idx].area == pytest.approx(exp)


@pytest.mark.parametrize("idx,expected_idxs", [
    (0, [0, 1, 2]),
    (1, [1, 2, 3]),
    (2, [2, 3, 4]),
    (3, [1, 3, 4]),
])
def test_midPoint(cells, idx, expected_idxs):
    mesh_pts = cells[idx]._msh.points
    pts = np.array([mesh_pts[i] for i in expected_idxs])
    exp = np.mean(pts, axis=0)
    assert np.allclose(cells[idx].midPoint, exp)


@pytest.mark.parametrize("idx,expected_ngbs", [
    (0, {1}),
    (1, {0, 2, 3}),
    (2, {1, 3}),
    (3, {1, 2}),
])
def test_ngb(cells, idx, expected_ngbs):
    assert set(cells[idx].ngb) == expected_ngbs


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_flow_array_shape(cells, idx):
    assert isinstance(cells[idx].flow, np.ndarray) and cells[idx].flow.shape == (2,)


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_oil_in_range(cells, idx):
    assert 0.0 <= cells[idx].oil <= 1.0


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_newOil_initial_empty(cells, idx):
    assert cells[idx].newOil == []


