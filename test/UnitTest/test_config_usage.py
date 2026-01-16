import pytest

from src.Cells.cellFactory import CellFactory
from src.Cells.triangle import Triangle
from src.IO.config import Config
from src.Geometry.mesh import Mesh
from src.Simulation.simulation import Simulation


def valid_config_dict():
    return {
        "geometry": {"meshName": "dummy", "borders": [[0, 1], [0, 1]]},
        "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
        "IO": {"writeFrequency": 0},
    }


def test_simulation_requires_config_instance():
    cfg = Config.from_dict(valid_config_dict())
    # Should accept a Config instance
    sim = Simulation(cfg)
    assert isinstance(sim.config, Config)


def test_simulation_rejects_plain_dict():
    # New API: plain dict should be rejected (anchor new Config usage)
    with pytest.raises(TypeError):
        Simulation(valid_config_dict())


def test_mesh_requires_config_instance(tmp_path, monkeypatch):
    # create a tiny dummy mesh file path for constructor signature checks
    dummy = tmp_path / "dummy.msh"
    dummy.write_text("")

    cfg = Config.from_dict(valid_config_dict())
    # Should accept Config instance
    m = Mesh(str(dummy), cfg)
    assert getattr(m, "config", None) is cfg

    # Passing a plain dict should raise
    with pytest.raises(TypeError):
        Mesh(str(dummy), valid_config_dict())


def test_cellfactory_and_triangle_require_config(monkeypatch):
    # Build a minimal mock mesh with the interface CellFactory expects
    class MockBlock:
        def __init__(self):
            self.type = "triangle"
            self.data = [[0, 1, 2]]

    class MockMesh:
        def __init__(self):
            self.cells = [MockBlock()]

    msh = MockMesh()
    cfg = Config.from_dict(valid_config_dict())

    # CellFactory should accept Config instance
    cf = CellFactory(msh, cfg)
    assert cf.config is cfg

    # Passing plain dict should raise
    with pytest.raises(TypeError):
        CellFactory(msh, valid_config_dict())

    # Triangle/Cell constructors should require Config (or None for legacy tests)
    with pytest.raises(TypeError):
        Triangle(msh, [0, 1, 2], 0, valid_config_dict())
