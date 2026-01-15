import numpy as np
import pytest

from src.Cells.line import Line
from src.Cells.triangle import Triangle



class MockMesh:
    """Mock mesh for testing."""

    def __init__():
        points = [
            np.array([0.0, 0.0, 0.0]),  # Point 0
            np.array([1.0, 0.0, 0.0]),  # Point 1
            np.array([0.5, 1.0, 0.0]),  # Point 2
            np.array([1.0, 1.0, 0.0]),  # Point 3
            np.array([0.0, 1.0, 0.0]),  # Point 4
        ]


# TODO: why is it a class?
# TODO: Fix names and Fixtures of "repeat" tests Oskar
# TODO: tests should be short and only test/assert one thing each
    """Test suite for Triangle.find_scaled_normales()."""

def test_no_neighbors_returns_empty():
    """Test that normals are empty when no neighbors exist."""
    msh = MockMesh()
    tri = Triangle(msh, [0, 1, 2], config = config cell_id=0,)
    result = tri.findScaledNormales(allCells=[tri])

    assert result == [], "Should return empty list when no neighbors"
    assert tri.scaledNormal == [], "scaledNormal should be empty"

def test_normals_count_matches_neighbors():
    """Test that number of normals equals number of neighbors."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)
    tri3 = Triangle(msh, [0, 2, 4], cell_id=2)

    all_cells = [tri1, tri2, tri3]
    tri1.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)

    assert len(tri1.scaledNormal) == len(
        tri1.ngb
    ), f"Expected {len(tri1.ngb)} normals, got {len(tri1.scaledNormal)}"

def test_normals_perpendicular_to_edges():
    """Test that each normal is perpendicular to its corresponding edge."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)

    all_cells = [tri1, tri2]
    tri1.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)

    cells_by_id = {c.id: c for c in all_cells}

    for i, ngb_id in enumerate(tri1.ngb):
        ngb = cells_by_id[ngb_id]

        # Find shared edge
        _pts = set(tuple(p) for p in tri1.cords)
        ngb_pts = set(tuple(p) for p in ngb.cords)
        shared_pts = list(_pts & ngb_pts)

        assert len(shared_pts) >= 2, f"Expected shared edge with neighbor {ngb_id}"

        # Build edge vector
        A = np.array(shared_pts[0], dtype=float)
        B = np.array(shared_pts[1], dtype=float)
        edge = np.array([B[0] - A[0], B[1] - A[1]])
        normal = np.array(tri1.scaledNormal[i], dtype=float)

        # Check perpendicularity: dot product should be ~0
        dot = np.dot(edge, normal)
        assert np.isclose(
            dot, 0.0, atol=1e-9
        ), f"Normal {i} not perpendicular to edge: dot={dot}"

def test_normals_point_outward():
    """Test that normals point outward from triangle midpoint."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)

    all_cells = [tri1, tri2]
    tri1.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)

    cells_by_id = {c.id: c for c in all_cells}

    for i, ngb_id in enumerate(tri1.ngb):
        ngb = cells_by_id[ngb_id]

        # Find shared edge midpoint
        _pts = set(tuple(p) for p in tri1.cords)
        ngb_pts = set(tuple(p) for p in ngb.cords)
        shared_pts = list(_pts & ngb_pts)

        A = np.array(shared_pts[0], dtype=float)
        B = np.array(shared_pts[1], dtype=float)
        edge_mid = np.array([(A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0])

        # Vector from edge midpoint to triangle midpoint
        to_midpoint = np.array(
            [tri1.midPoint[0] - edge_mid[0], tri1.midPoint[1] - edge_mid[1]],
            dtype=float,
        )

        normal = np.array(tri1.scaledNormal[i], dtype=float)

        # Outward means dot product with "to_midpoint" should be <= 0
        dot = np.dot(normal, to_midpoint)
        assert dot <= 1e-9, f"Normal {i} does not point outward: dot={dot}"

def test_normals_toward_neighbor():
    """Test that normals point toward neighbor midpoint."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)

    all_cells = [tri1, tri2]
    tri1.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)

    cells_by_id = {c.id: c for c in all_cells}

    for i, ngb_id in enumerate(tri1.ngb):
        ngb = cells_by_id[ngb_id]

        # Find shared edge midpoint
        _pts = set(tuple(p) for p in tri1.cords)
        ngb_pts = set(tuple(p) for p in ngb.cords)
        shared_pts = list(_pts & ngb_pts)

        A = np.array(shared_pts[0], dtype=float)
        B = np.array(shared_pts[1], dtype=float)
        edge_mid = np.array([(A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0])

        # Vector from edge midpoint to neighbor midpoint
        to_neighbor = np.array(
            [ngb.midPoint[0] - edge_mid[0], ngb.midPoint[1] - edge_mid[1]],
            dtype=float,
        )

        normal = np.array(tri1.scaledNormal[i], dtype=float)

        # Toward neighbor means dot product should be >= 0
        dot = np.dot(normal, to_neighbor)
        assert dot >= -1e-9, f"Normal {i} does not point toward neighbor: dot={dot}"

def test_normals_ordered_match_neighbors():
    """Test that normals are ordered to match ngb list."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)
    tri3 = Triangle(msh, [0, 2, 4], cell_id=2)

    all_cells = [tri1, tri2, tri3]
    tri1.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)

    # Verify that each normal corresponds to its neighbor in order
    assert len(tri1.scaledNormal) == len(
        tri1.ngb
    ), f"Length mismatch: normals={len(tri1.scaledNormal)}, ngb={len(tri1.ngb)}"

    cells_by_id = {c.id: c for c in all_cells}

    for i, ngb_id in enumerate(tri1.ngb):
        ngb = cells_by_id[ngb_id]

        # Check that this normal is associated with this neighbor
        _pts = set(tuple(p) for p in tri1.cords)
        ngb_pts = set(tuple(p) for p in ngb.cords)
        shared_pts = list(_pts & ngb_pts)

        assert (
            len(shared_pts) >= 2
        ), f"Normal {i} should correspond to shared edge with neighbor {ngb_id}"

def test_line_cell_normals_empty():
    """Test that Line cells return empty normals."""
    msh = MockMesh()
    line = Line(msh, [0, 1], cell_id=0)
    result = line.findScaledNormales(allCells=[line])

    assert result == [], "Line cell should return empty normals"
    assert line.scaledNormal == [], "Line cell scaledNormal should be empty"

def test_single_triangle_with_one_neighbor(
    ,
):  # TODO: Fix names and Fixtures of \"repeat\" tests
    """Test simple case: two triangles sharing one edge."""
    msh = MockMesh()
    tri1 = Triangle(msh, [0, 1, 2], cell_id=0)
    tri2 = Triangle(msh, [1, 3, 2], cell_id=1)

    all_cells = [tri1, tri2]
    tri1.findNGB(all_cells)
    tri2.findNGB(all_cells)
    tri1.findScaledNormales(all_cells)
    tri2.findScaledNormales(all_cells)

    # Each should have exactly one neighbor and one normal
    assert len(tri1.ngb) == 1, f"tri1 should have 1 neighbor, got {len(tri1.ngb)}"
    assert len(tri2.ngb) == 1, f"tri2 should have 1 neighbor, got {len(tri2.ngb)}"
    assert (
        len(tri1.scaledNormal) == 1
    ), f"tri1 should have 1 normal, got {len(tri1.scaledNormal)}"
    assert (
        len(tri2.scaledNormal) == 1
    ), f"tri2 should have 1 normal, got {len(tri2.scaledNormal)}"

    # Verify the normal is a 2D vector (numpy array)
    normal1 = np.array(tri1.scaledNormal[0])
    assert normal1.shape == (2,), f"Normal should be 2D, got shape {normal1.shape}"
