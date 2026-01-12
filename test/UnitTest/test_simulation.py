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

def test_update_oil(read_config):
    sim = Simulation(read_config)
