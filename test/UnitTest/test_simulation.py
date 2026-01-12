import pytest
import numpy as np

from unittest.mock import MagicMock
from src.simulation import Simulation

class FakeCell:
    def __init__(self, cid, oil, area=1.0):
        self.id = cid
        self.type = "triangle"
        self.oil = oil
        self.area = area
        self.flow = np.array([1.0, 0.0])
        self.scaled_normal = [np.array([1.0, 0.0])]
        self.ngb = []
        self.new_oil = []

class FakeMesh:
    def __init__(self):
        c0 = FakeCell(0, 1.0)
        c1 = FakeCell(1, 2.0)
        c0.ngb[1]
        c1.ngb[0]
        self.cells = [c0, c1]

@pytest.fixture
def config():
    return {
            "geometry": {"meshName": "dummy"},
            "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
            "IO": {"writeFrequency": 1}
        }

def test_sim_init(monkeypatch, config):
    from src.simulation import Simulation
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh)
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)
    sim = Simulation(config)
    assert  sim.dt == 1.0
    assert sim.CurrentStep == 0
    assert len(sim.oil_vals) == 2


def test_get_oil_vals(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    assert sim.getOilVals() == [1.0, 2.0]


def test_flux_upwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim.msh.cells

    f = sim.flux(0, c0, 1)
    assert f == c0.oil * 1.0


def test_update_oil(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    sim.update_oil()

    for cell in sim.msh.cells:
        assert cell.oil != 0


def test_run_sim_calls_plotting(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)
    monkeypatch.setattr("src.simulation.tqdm", lambda *a, **k: a[0])

    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=False)

    assert mock_vs.plotting.called
