import numpy as np
import pytest

from src.Geometry.triangle import Triangle


class _MockMesh:
    def __init__(self, points):
        self.points = points


def make_mesh_and_triangles():
    # simple square split into two triangles
    points = [
        (0.0, 0.0, 0.0),  # 0
        (1.0, 0.0, 0.0),  # 1
        (0.0, 1.0, 0.0),  # 2
        (1.0, 1.0, 0.0),  # 3
    ]
    msh = _MockMesh(points)
    t0 = Triangle(msh, [0, 1, 2], 0, config=None)
    t1 = Triangle(msh, [1, 3, 2], 1, config=None)
    return msh, t0, t1


def test_midpoint_and_area():
    msh, t0, _ = make_mesh_and_triangles()
    expected_mid = np.mean([msh.points[i] for i in [0, 1, 2]], axis=0)
    assert np.allclose(t0.midPoint, expected_mid)

    # area for right triangle with legs 1 and 1 should be 0.5
    assert pytest.approx(t0.area, rel=1e-12) == 0.5


def test_oil_clamping_and_type_validation():
    msh, t0, _ = make_mesh_and_triangles()
    # default oil in (0,1)
    val = t0.oil
    assert 0.0 <= val <= 1.0

    # clamp negative
    t0.oil = -5
    assert t0.oil == 0.0

    # clamp above 1
    t0.oil = 2.5
    assert t0.oil == 1.0

    # non-numeric raises
    with pytest.raises(TypeError):
        t0.oil = "not-a-number"


def test_flow_computation_matches_formula():
    msh, t0, _ = make_mesh_and_triangles()
    mp = t0.midPoint
    expected = np.array([mp[1] - mp[0] * 0.2, -mp[0]])
    assert np.allclose(t0.flow, expected)


def test_getters_setters_pointset_and_scalednormal_empty_by_default():
    msh, t0, _ = make_mesh_and_triangles()
    # pointSet should be a set of tuples representing cords
    ps = t0.pointSet
    assert isinstance(ps, set)
    assert tuple(msh.points[0]) in ps

    # scaledNormal should be empty array initially (no neighbours)
    sn = t0.scaledNormal
    assert isinstance(sn, np.ndarray)
    assert sn.size == 0

    # cords setter updates midpoint and area
    old_mid = t0.midPoint.copy()
    new_cords = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 2.0, 0.0)]
    t0.cords = new_cords
    assert not np.allclose(t0.midPoint, old_mid)
    assert pytest.approx(t0.area, rel=1e-12) == 2.0


def test_findNGB_and_neighbor_lists_and_mesh_caches():
    msh, t0, t1 = make_mesh_and_triangles()
    allcells = [t0, t1]
    # ensure no neighbors initially
    assert t0.ngb == []
    assert t1.ngb == []

    # compute neighbors
    t0.findNGB(allcells)
    t1.findNGB(allcells)

    # they share two points (1 and 2) so should be neighbors
    assert t0.ngb == [1]
    assert t1.ngb == [0]

    # mesh caches should have been created for compatibility
    assert hasattr(msh, "_point_to_cells")
    assert hasattr(msh, "_id_to_cell")


def test_scaled_normals_with_neighbors_produces_vectors():
    msh, t0, t1 = make_mesh_and_triangles()
    allcells = [t0, t1]
    t0.findNGB(allcells)
    # request scaled normals with access to all cells
    normals = t0.findScaledNormales(allcells)
    # There should be at least one normal vector
    assert isinstance(normals, list)
    assert len(normals) >= 1
    # each normal should be a 2-element numeric array
    for n in normals:
        assert len(n) == 2
        assert np.isfinite(n).all()
