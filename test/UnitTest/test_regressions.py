import types
from pathlib import Path

import pytest

from src.Geometry.triangle import Triangle
from src.Geometry.cellFactory import CellFactory
from src.IO.config import Config
from src.Simulation.simulation import Simulation


def _make_two_triangles():
    class M:
        pass

    msh = M()
    msh.points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)]

    t0 = Triangle(msh, [0, 1, 2], cell_id=0)
    t1 = Triangle(msh, [1, 3, 2], cell_id=1)
    return msh, t0, t1


def test_findNGB_returns_list():
    msh, t0, t1 = _make_two_triangles()
    # Ensure call returns a list (regression from None-return bug)
    res = t0.findNGB([t0, t1])
    assert isinstance(res, list)


def test_cellfactory_accepts_plain_dict():
    class MockBlock:
        def __init__(self):
            self.type = "triangle"
            self.data = [[0, 1, 2]]

    class MockMesh:
        def __init__(self):
            self.cells = [MockBlock()]
            self.points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

    cfg_dict = {
        "geometry": {"meshName": "dummy", "borders": [[0, 1], [0, 1]]},
        "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
        "IO": {"writeFrequency": 0},
    }

    cf = CellFactory(MockMesh(), cfg_dict)
    assert isinstance(cf.config, Config)


def test_run_sim_raises_when_no_videocreator(monkeypatch):
    # Build a minimal Config that requests video creation
    cfg = Config.from_dict(
        {"geometry": {"meshName": "x"}, "settings": {"tStart": 0, "tEnd": 0, "nSteps": 0}, "IO": {"writeFrequency": 1}, "video": {"videoFPS": 10}}
    )

    # Create a Simulation instance without running __init__ and set minimal attrs
    sim = Simulation.__new__(Simulation)
    sim._config = cfg
    sim._nSteps = 0
    sim._dt = 1.0
    sim._writeFrequency = 1
    sim._imageDir = Path("Output/images")
    sim._visualizer = types.SimpleNamespace(plotting=lambda *a, **k: None)

    # Ensure importing src.IO.video yields a module without VideoCreator to force vc_cls=None
    monkeypatch.setitem(__import__("sys").modules, "src.IO.video", types.ModuleType("src.IO.video"))

    with pytest.raises(RuntimeError):
        sim.run_sim(runNumber=0)
