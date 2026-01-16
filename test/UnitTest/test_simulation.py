from dataclasses import asdict
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.simulation import Simulation

from test.utilitiesTests.ConfigTest import configTest
from src.IO.LoadTOML import LoadTOML
from src.Simulation.simulation import Simulation

configloader = LoadTOML()
config = configloader.loadConfigFile("Input\BaseSimConfig.toml")


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
        self._isFishing = False
        self.isFishing = False


class FakeMesh:
    def __init__(self):
        c0 = FakeCell(0, 1.0)
        c1 = FakeCell(1, 2.0)
        c0.ngb = [1]
        c1.ngb = [0]
        self.cells = [c0, c1]

def clone_config(base_cfg, **updates):
    cfg_dict = asdict(base_cfg)
    cfg_dict.update(updates)
    return base_cfg.from_dict(cfg_dict)


@pytest.fixture
def config():
    return configTest()


# --- Tests ---
def test_sim_init_dt(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim._dt == 0.01


def test_sim_init_ct(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim._currentTime == 0


def test_sim_init_ov(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert len(sim._oilVals) == 0


def test_get_oil_vals(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    sim.getOilVals()
    assert sim.oilVals[-1] == [1.0, 2.0]
    assert sim.fishingOil[-1] == 0.0


def test_flux_upwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    c0, c1 = sim._msh.cells
    f = sim._computeFlux(0, c0, 1)
    assert f == c0.oil * 1.0


def test_flux_downwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    c0, c1 = sim._msh.cells
    c0.scaledNormal = [np.array([-1.0, 0.0])]
    f = sim._computeFlux(0, c0, 1)
    assert f == c1.oil * -1.0


def test_update_oil_changes_oil(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    before = [c.oil for c in sim._msh.cells]
    sim.updateOil(sim._dt)
    after = [c.oil for c in sim._msh.cells]
    assert before != after


def test_run_sim_video(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda *args, **kwargs: mock_vs)

    class MockVideo:
        def __init__(self, **kwargs):
            self.called = False

        def createVideoFromRun(self, runNumber):
            self.called = True
            return "video.mp4"

    video = MockVideo()
    monkeypatch.setattr("src.simulation.VideoCreator", lambda **kwargs: video)
    sim = Simulation(config)
    sim.run_sim(runNumber=1, create_video=True)
    assert video.called


def test_run_sim_no_video(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda *args, **kwargs: mock_vs)
    config = clone_config(
        config,
        IO={"writeFrequency": 0},
    )
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.run_sim(runNumber=None, create_video=False)
    assert not mock_vs.plotting.called


def test_run_sim_multiple_steps(monkeypatch, config):
    config = clone_config(
        config,
        settings={"tStart": 0, "tEnd": 2, "nSteps": 2},
    )
    monkeypatch.setattr("src.simulation.Mesh", lambda *args, **kwargs: FakeMesh())
    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda *args, **kwargs: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    sim = Simulation(config)
    sim.run_sim(runNumber=1, create_video=False)
    assert mock_vs.plotting.called
