from unittest.mock import MagicMock

import numpy as np
import pytest

from src.IO.LoadTOML import LoadTOML
from src.Simulation.simulation import Simulation

configloader = LoadTOML()
config = configloader.loadTomlFile("Input\BaseSimConfig.toml")


class FakeCell:
    def __init__(self, cid, oil, area=1.0, cell_type="triangle"):
        self.id = cid
        self.type = cell_type
        self.oil = oil
        self.area = area
        self.flow = np.array([1.0, 0.0])
        self.scaledNormal = [np.array([1.0, 0.0])]
        self.ngb = []
        self.newOil = []


class FakeMesh:
    def __init__(self):
        c0 = FakeCell(0, 1.0)
        c1 = FakeCell(1, 2.0)
        c0.ngb = [1]
        c1.ngb = [0]
        self.cells = [c0, c1]


@pytest.fixture
def config():
    return {
        "geometry": {"meshName": "dummy"},
        "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
        "IO": {"writeFrequency": 1},
    }


# --- Tests ---
def test_sim_init_dt(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim._dt == 1.0


def test_sim_init_ct(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim._currentTime == 0


def test_sim_init_ov(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert len(sim._oilVals) == 2


def test_get_oil_vals(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim.getOilVals() == [1.0, 2.0]


def test_flux_upwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    c0, c1 = sim._msh.cells
    f = sim._computeFlux(0, c0, 1)
    assert f == c0.oil * 1.0


def test_flux_downwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    c0, c1 = sim._msh.cells
    c0._scaledNormal = [np.array([-1.0, 0.0])]
    f = sim._computeFlux(0, c0, 1)
    assert f == c1.oil * -1.0


def test_update_oil_changes_oil(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    before = [c.oil for c in sim._msh.cells]
    sim.updateOil()
    after = [c.oil for c in sim._msh.cells]
    assert before != after


def test_update_oil_warn(monkeypatch, config, capsys):
    class BadCell(FakeCell):
        def __init__(self, cid, oil):
            super().__init__(cid, oil)
            self.new_oil = None

    class BadMesh(FakeMesh):
        def __init__(self):
            self.cells = [BadCell(0, 1.0)]

    monkeypatch.setattr("src.simulation.Mesh", lambda _: BadMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    sim.updateOil()
    captured = capsys.readouterr()
    assert "Warning: Cell, 0, was None" in captured.out


def test_update_oil_skips_non_triangle(monkeypatch):
    class NonTriCell(FakeCell):
        def __init__(self, cid, oil):
            super().__init__(cid, oil)
            self.type = "quad"

    class NonTriMesh(FakeMesh):
        def __init__(self):
            self.cells = [NonTriCell(0, 1.0)]

    monkeypatch.setattr("src.simulation.Mesh", lambda _: NonTriMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(
        {
            "geometry": {"meshName": "dummy"},
            "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
            "IO": {"writeFrequency": 1},
        }
    )
    sim.update_oil()
    sim = Simulation(
        {
            "geometry": {"meshName": "dummy"},
            "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
            "IO": {"writeFrequency": 1},
        }
    )
    sim.updateOil()


def test_run_sim_plotting(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=False)
    assert mock_vs.plotting.called


def test_run_sim_video(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    mock_video = MagicMock()
    monkeypatch.setattr("src.simulation.VideoCreator", lambda fps: mock_video)
    mock_video.create_video_from_run.return_value = "video.mp4"
    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=True)
    assert mock_video.create_video_from_run.called


def test_run_sim_no_video(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.run_sim(run_number=None, create_video=False)
    assert mock_vs.plotting.called


def test_run_sim_skips_loop(monkeypatch):
    config = {
        "geometry": {"meshName": "dummy"},
        "settings": {"tStart": 0, "tEnd": 0, "nSteps": 1},
        "IO": {"writeFrequency": 1},
    }
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.CurrentStep = 1
    sim.run_sim(run_number=None, create_video=False)
    assert mock_vs.plotting.called


def test_run_sim_multiple_steps(monkeypatch):
    config = {
        "geometry": {"meshName": "dummy"},
        "settings": {"tStart": 0, "tEnd": 2, "nSteps": 2},
        "IO": {"writeFrequency": 1},
    }
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=False)
    assert mock_vs.plotting.called


def test_update_oil_warn_and_assign(monkeypatch, config, capsys):
    # Create a cell with new_oil=None but valid oil
    class BadCell(FakeCell):
        def __init__(self, cid, oil):
            super().__init__(cid, oil)
            self.new_oil = None

    class BadMesh(FakeMesh):
        def __init__(self):
            self.cells = [BadCell(42, 7.0)]

    monkeypatch.setattr("src.simulation.Mesh", lambda _: BadMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    sim.updateOil()

    captured = capsys.readouterr()
    assert "Warning: Cell, 42, was None" in captured.out
