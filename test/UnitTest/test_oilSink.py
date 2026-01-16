import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from src.IO.config import Config

from src.Geometry.oil_sink import (
    _get_cells_from_mesh,
    _calculate_distance,
    _gaussian_coefficient,
    _uniform_coefficient,
    _linear_coefficient,
    _get_distribution_coefficient,
    compute_ship_sink,
    compute_source,
    OilSinkSource,
)


def test_calculate_distance_zero():
    assert _calculate_distance([0, 0], [0, 0]) == 0.0

def test_calculate_distance_simple():
    assert _calculate_distance([0, 0], [3, 4]) == 5.0

def test_calculate_distance_ignores_z():
    assert _calculate_distance([0, 0, 100], [3, 4, 200]) == 5.0

def test_calculate_distance_negative_coords():
    assert _calculate_distance([-1, -1], [2, 3]) == pytest.approx(5.0)


def test_gaussian_at_zero_distance():
    result = _gaussian_coefficient(0, 1.0)
    assert result == pytest.approx(1.0 / (2.0 * np.pi))


def test_gaussian_increases_with_sigma():
    result1 = _gaussian_coefficient(1.0, 1.0)
    result2 = _gaussian_coefficient(1.0, 2.0)
    assert result2 < result1


def test_gaussian_decreases_with_distance():
    result1 = _gaussian_coefficient(0.5, 1.0)
    result2 = _gaussian_coefficient(1.0, 1.0)
    assert result1 > result2


def test_uniform_within_radius():
    result = _uniform_coefficient(0.5, 1.0)
    assert result == 1.0


def test_uniform_outside_radius():
    result = _uniform_coefficient(1.5, 1.0)
    assert result == 0.0


def test_linear_at_zero_distance():
    assert _linear_coefficient(0, 1.0) == 1.0


def test_linear_at_radius():
    assert _linear_coefficient(1.0, 1.0) == 0.0


def test_linear_mid_distance():
    assert _linear_coefficient(0.5, 1.0) == 0.5


def test_linear_beyond_radius():
    assert _linear_coefficient(1.5, 1.0) == 0.0


def test_gaussian_mode():
    result = _get_distribution_coefficient(0, "gaussian", 1.0, 1.0)
    assert result == pytest.approx(_gaussian_coefficient(0, 1.0))


def test_uniform_mode():
    result = _get_distribution_coefficient(0.5, "uniform", 1.0, 1.0)
    assert result == 1.0


def test_linear_mode():
    result = _get_distribution_coefficient(0.5, "linear", 1.0, 1.0)
    assert result == 0.5


def test_invalid_mode():
    assert _get_distribution_coefficient(0, "invalid", 1.0, 1.0) == 0.0


def test_empty_mesh():
    msh = Mock()
    msh.cells = []
    assert _get_cells_from_mesh(msh) == []


def test_mesh_with_triangles():
    cell1, cell2 = Mock(), Mock()
    cell1.type = "triangle"
    cell2.type = "triangle"
    msh = Mock()
    msh.cells = [cell1, cell2]
    assert _get_cells_from_mesh(msh) == [cell1, cell2]


def test_mesh_filters_non_triangles():
    cell1, cell2 = Mock(), Mock()
    cell1.type = "triangle"
    cell2.type = "quad"
    msh = Mock()
    msh.cells = [cell1, cell2]
    assert _get_cells_from_mesh(msh) == [cell1]


def test_mesh_exception_handling():
    msh = Mock()
    msh.cells = None
    assert _get_cells_from_mesh(msh) == []


def test_no_cells_in_range():
    msh = Mock()
    msh.cells = []
    result = compute_ship_sink(msh, [0, 0], radius=0.1)
    assert result == {}


def test_single_cell_in_range():
    cell = Mock()
    cell.id = 1
    cell.midPoint = [0, 0]
    cell.type = "triangle"
    msh = Mock()
    msh.cells = [cell]
    result = compute_ship_sink(msh, [0, 0], radius=1.0, strength=2.0, mode="uniform")
    assert 1 in result
    assert result[1] == pytest.approx(2.0)


def test_cell_beyond_radius_excluded():
    cell = Mock()
    cell.id = 1
    cell.midPoint = [5, 5]
    cell.type = "triangle"
    msh = Mock()
    msh.cells = [cell]
    result = compute_ship_sink(msh, [0, 0], radius=0.1)
    assert result == {}


def test_multiple_cells_with_distances():
    cell1, cell2 = Mock(), Mock()
    cell1.id, cell1.midPoint, cell1.type = 1, [0, 0], "triangle"
    cell2.id, cell2.midPoint, cell2.type = 2, [0.05, 0], "triangle"
    msh = Mock()
    msh.cells = [cell1, cell2]
    result = compute_ship_sink(msh, [0, 0], radius=0.1, mode="uniform")
    assert len(result) == 2


def test_no_cells_in_range():
    msh = Mock()
    msh.cells = []
    result = compute_source(msh, [0, 0], radius=0.1)
    assert result == {}


def test_single_cell_in_range():
    cell = Mock()
    cell.id = 1
    cell.midPoint = [0, 0]
    cell.type = "triangle"
    msh = Mock()
    msh.cells = [cell]
    result = compute_source(msh, [0, 0], radius=1.0, strength=2.0, mode="uniform")
    assert 1 in result
    assert result[1] == pytest.approx(2.0)


class TestOilSinkSource:
    def test_init_with_default_config(self):
        msh = Mock()
        msh.cells = []
        sink = OilSinkSource(msh)
        assert np.array_equal(sink.position, np.array([0.5, 0.5]))
        assert sink.strength == 1.0
        assert sink.type == "gaussian"
        assert sink.radius == 1.0

    def test_init_with_dict_config(self):
        msh = Mock()
        msh.cells = []
        config = {"position": [1, 2], "strength": 2.0, "type": "uniform", "radius": 0.5}
        sink = OilSinkSource(msh, config)
        assert np.array_equal(sink.position, np.array([1, 2]))
        assert sink.strength == 2.0
        assert sink.type == "uniform"
        assert sink.radius == 0.5

    def test_init_with_config_object(self):
        msh = Mock()
        msh.cells = []
        config = Mock(spec=Config)
        config.other = {"position": [3, 4], "strength": 3.0}
        sink = OilSinkSource(msh, config)
        assert np.array_equal(sink.position, np.array([3, 4]))
        assert sink.strength == 3.0

    def test_parse_configuration_none(self):
        msh = Mock()
        msh.cells = []
        sink = OilSinkSource(msh, None)
        assert isinstance(sink, OilSinkSource)

    def test_call_applies_oil_to_cells(self):
        cell = Mock()
        cell.midPoint = [0, 0]
        cell.oil = 0.0
        msh = Mock()
        msh.cells = [cell]
        sink = OilSinkSource(msh, {"position": [0, 0], "radius": 1.0, "mode": "uniform", "strength": 1.0})
        sink(cell)
        assert cell.oil > 0.0