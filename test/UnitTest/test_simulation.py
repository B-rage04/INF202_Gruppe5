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
        c0.ngb = [1]
        c1.ngb = [0]
        self.cells = [c0, c1]

@pytest.fixture
def config():
    return {
            "geometry": {"meshName": "dummy"},
            "settings": {"tStart": 0, "tEnd": 1, "nSteps": 1},
            "IO": {"writeFrequency": 1}
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

def test_flux_downwind(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim.msh.cells

    c0.scaled_normal = [np.array([-1.0, 0.0])]

    f = sim.flux(0, c0, 1)
    assert f == c1.oil * -1.0


def test_update_oil_changes_oil(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())
    monkeypatch.setattr("src.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    before = [cell.oil for cell in sim.msh.cells]

    sim.update_oil()
    after = [cell.oil for cell in sim.msh.cells]

    assert before != after


def test_run_sim_calls_plotting(monkeypatch, config):
    monkeypatch.setattr("src.simulation.Mesh", lambda _: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr("src.simulation.Visualizer", lambda _: mock_vs)
    monkeypatch.setattr("src.simulation.VideoCreator", MagicMock)

    monkeypatch.setattr("src.simulation.tqdm", DummyTqdm)


    sim = Simulation(config)
    sim.run_sim(run_number=1, create_video=False)

    assert mock_vs.plotting.called


<<<<<<< HEAD
    assert True  # TODO fix test


def test_ship_sink_reduces_oil():
    import numpy as np
    from src.simulation import Simulation
    from src.mesh import Mesh

    config = {
        "settings": {"nSteps": 1, "tStart": 0.0, "tEnd": 0.5},
        "geometry": {
            "meshName": "Exsample/Geometry/bay.msh",
            "borders": [[0, 0.45], [0, 0.2]],
            "ship": [0.35, 0.45],
        },
        "IO": {"logName": "log", "writeFrequency": 1},
    }

    sim = Simulation(config)

    # Identify cells within ship radius
    ship_xy = np.array(config["geometry"]["ship"])
    in_radius_ids = []
    for cell in sim.msh.cells:
        if cell.type != "triangle":
            continue
        d = np.linalg.norm(np.array([cell.midpoint[0], cell.midpoint[1]]) - ship_xy)
        if d <= 0.1:
            in_radius_ids.append(cell.id)

    # Ensure there are some cells in radius
    assert len(in_radius_ids) > 0

    # Snapshot oil, update once, and check reduced values in radius
    before = {cell.id: cell.oil for cell in sim.msh.cells if cell.type == "triangle"}
    sim.update_oil()
    after = {cell.id: cell.oil for cell in sim.msh.cells if cell.type == "triangle"}

    reduced = [after[i] < before[i] for i in in_radius_ids]
    assert any(reduced), "Expected some oil reduction within ship radius"
=======
>>>>>>> tests_video_branch
