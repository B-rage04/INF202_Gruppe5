import pytest

from src.Geometry.cellFactory import CellFactory
from src.Geometry.triangle import Triangle
from src.IO.config import Config
from src.Geometry.mesh import Mesh
from src.Simulation.simulation import Simulation


def valid_config_dict():
    return {
        "geometry": {"meshName": "dummy", "borders": [[0, 1], [0, 1]]},
        "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
        "IO": {"writeFrequency": 0},
    }






def test_mesh_requires_config_instance(tmp_path, monkeypatch):
    # create a tiny dummy mesh file path for constructor signature checks
    dummy = tmp_path / "dummy.msh"
    dummy.write_text("")




def test_cellfactory_and_triangle_require_config(monkeypatch):
    # Build a minimal mock mesh with the interface CellFactory expects
    class MockBlock:
        def __init__(self):
            self.type = "triangle"
            self.data = [[0, 1, 2]]

    class MockMesh:
        def __init__(self):
            self.cells = [MockBlock()]
            # also expose point coordinates required by Triangle
            self.points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

    msh = MockMesh()
    cfg = Config.from_dict(valid_config_dict())

    # CellFactory should accept Config instance
    cf = CellFactory(msh, cfg)
    assert cf.config is cfg

    # Passing plain dict should be accepted by the refactored API
    cf2 = CellFactory(msh, valid_config_dict())
    from src.IO.config import Config as _C

    assert isinstance(cf2.config, _C)

    # Triangle/Cell constructors accept config/dict in new API
    t = Triangle(msh, [0, 1, 2], 0, valid_config_dict())
    assert getattr(t, "_config", None) is not None
