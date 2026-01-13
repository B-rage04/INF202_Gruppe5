from unittest.mock import MagicMock

import numpy as np
import pytest

from src.simulation import Simulation


# TODO: test shood be short and only test/asert one thing each
class FakeCell:
    def __init__(self, cid, oil, area=1.0):
        self.id = cid
        self.type = "triangle"
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


# This only exists because some one specific person really wants to use tqdm
class DummyTqdm:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, n=1):
        pass


def test_sim_init(monkeypatch, config):
    from src.simulation import Simulation

    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim.dt == 1.0


def test_sim_init(monkeypatch, config):
    from src.simulation import Simulation

    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert sim.currentTime == 0.0


def test_sim_init(monkeypatch, config):
    from src.simulation import Simulation

    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert len(sim.oilVals) == 2



def test_get_oil_vals(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    assert sim.getOilVals() == [1.0, 2.0]


def test_flux_upwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim.mesh.cells

    f = sim._computeFlux(0, c0, 1)
    assert f == c0.oil * 1.0


def test_flux_downwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim.mesh.cells

    c0.scaledNormal = [np.array([-1.0, 0.0])]

    f = sim._computeFlux(0, c0, 1)
    assert f == c1.oil * -1.0


def test_update_oil_changes_oil(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    before = [cell.oil for cell in sim.mesh.cells]

    sim.updateOil()
    after = [cell.oil for cell in sim.mesh.cells]

    assert before != after


def test_run_sim_calls_plotting(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)

    monkeypatch.setattr("src.simulation.tqdm", DummyTqdm)

    sim = Simulation(config)
    sim.run_sim(runNumber=1, createVideo=False)

    assert mock_vs.plotting.called


def test_run_sim_creates_video(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)

    mock_video = MagicMock()
    monkeypatch.setattr("src.simulation.VideoCreator", lambda fps: mock_video)
    mock_video.create_video_from_run.return_value = "video.mp4"

    monkeypatch.setattr("src.simulation.tqdm", DummyTqdm)

    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=True)

    assert mock_video.create_video_from_run.called


def test_update_oil_warn(monkeypatch, config, capsys):
    class BadCell(FakeCell):
        def __init__(self, cid, oil):
            super().__init__(cid, oil)
            self.new_oil = None  # trigger the warning

    class BadMesh(FakeMesh):
        def __init__(self):
            self.cells = [BadCell(0, 1.0)]

    monkeypatch.setattr("src.simulation.Mesh", lambda _: BadMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    sim.update_oil()

    captured = capsys.readouterr()
    assert "Warning: Cell, 0, was None" in captured.out
