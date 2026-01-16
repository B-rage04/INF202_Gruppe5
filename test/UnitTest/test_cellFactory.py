from types import SimpleNamespace

import numpy as np
import pytest

from src.Cells.cellFactory import CellFactory
from src.LoadTOML import LoadTOML

configloader = LoadTOML()
config = configloader.loadTomlFile("Input\BaseSimConfig.toml")


@pytest.fixture
def triangle_mesh():
    pts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    cells = [SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]]))]
    return SimpleNamespace(points=pts, cells=cells)


@pytest.fixture
def triangle_line_mesh():
    pts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 0.0, 0.0]])
    cells = [
        SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]])),
        SimpleNamespace(type="line", data=np.array([[1, 3]])),
    ]
    return SimpleNamespace(points=pts, cells=cells)


def test_cell_factory_returns_one_cell(triangle_mesh):
    cells = CellFactory(triangle_mesh, config)()
    assert len(cells) == 1


def test_cell_factory_triangle_type(triangle_mesh):
    cells = CellFactory(triangle_mesh, config)()
    assert cells[0].type == "triangle"


def test_cell_factory_triangle_and_line_types(triangle_line_mesh):
    cells = CellFactory(triangle_line_mesh, config)()
    types = sorted([c.type for c in cells])
    assert types == ["line", "triangle"]
