"""
Unit tests for the Simulation class.

These tests validate:
- Correct initialization of simulation time parameters
- Oil value tracking
- Flux computation (upwind / downwind behavior)
- Oil update mechanics
- Video creation logic during simulation runs

All external dependencies (Mesh, Visualizer, VideoCreator) are mocked
to isolate Simulation behavior.
"""

from dataclasses import asdict
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.Simulation.simulation import Simulation
from test.utilitiesTests.ConfigTest import configTest
from src.IO.LoadTOML import LoadTOML


# ---------------------------------------------------------------------
# Test configuration loading
# ---------------------------------------------------------------------

configloader = LoadTOML()
base_config = configloader.loadConfigFile("Input/BaseSimConfig.toml")


# ---------------------------------------------------------------------
# Fake test doubles (minimal implementations)
# ---------------------------------------------------------------------

class FakeCell:
    """
    Minimal stand-in for a real mesh cell.

    Only implements the attributes accessed by Simulation.
    """

    def __init__(self, cid, oil, area=1.0, cell_type="triangle"):
        self.id = cid
        self.type = cell_type
        self.oil = oil
        self.area = area

        # Simple constant flow to make flux predictable
        self.flow = np.array([1.0, 0.0])

        # Single face normal
        self.scaledNormal = [np.array([1.0, 0.0])]

        # Neighbor list (filled externally)
        self.ngb = []

        # Attributes expected by Simulation
        self.newOil = []
        self._isFishing = False
        self.isFishing = False


class FakeMesh:
    """
    Minimal mesh with two neighboring triangular cells.
    """

    def __init__(self):
        c0 = FakeCell(0, 1.0)
        c1 = FakeCell(1, 2.0)

        # Make the two cells neighbors of each other
        c0.ngb = [1]
        c1.ngb = [0]

        self.cells = [c0, c1]


# ---------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------

def clone_config(base_cfg, **updates):
    """
    Create a modified copy of a Config object.

    Parameters
    ----------
    base_cfg : Config
        Original configuration.
    **updates
        Key-value pairs to override.

    Returns
    -------
    Config
        Updated configuration instance.
    """
    cfg_dict = asdict(base_cfg)
    cfg_dict.update(updates)
    return base_cfg.from_dict(cfg_dict)


# ---------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def config():
    """
    Provide a default test configuration.
    """
    return configTest()


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_sim_init_dt(monkeypatch, config):
    """
    Ensure timestep dt is computed correctly during initialization.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    assert sim._dt == 0.01


def test_sim_init_ct(monkeypatch, config):
    """
    Ensure current time starts at tStart.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    assert sim._currentTime == 0


def test_sim_init_ov(monkeypatch, config):
    """
    Ensure oil value history is empty on initialization.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    assert len(sim._oilVals) == 0


def test_get_oil_vals(monkeypatch, config):
    """
    Verify that getOilVals records oil values and fishing oil correctly.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    sim.getOilVals()

    assert sim.oilVals[-1] == [1.0, 2.0]
    assert sim.fishingOil[-1] == 0.0


def test_flux_upwind(monkeypatch, config):
    """
    Test upwind flux selection when flow aligns with normal.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim._msh.cells

    f = sim._computeFlux(0, c0, 1)
    assert f == c0.oil * 1.0


def test_flux_downwind(monkeypatch, config):
    """
    Test downwind flux selection when flow opposes normal.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)
    c0, c1 = sim._msh.cells

    # Flip normal direction
    c0.scaledNormal = [np.array([-1.0, 0.0])]

    f = sim._computeFlux(0, c0, 1)
    assert f == c1.oil * -1.0


def test_update_oil_changes_oil(monkeypatch, config):
    """
    Ensure oil values change after an update step.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())
    monkeypatch.setattr("src.Simulation.simulation.Visualizer", MagicMock)

    sim = Simulation(config)

    before = [c.oil for c in sim._msh.cells]
    sim.updateOil(sim._dt)
    after = [c.oil for c in sim._msh.cells]

    assert before != after


def test_run_sim_video(monkeypatch, config):
    """
    Verify that a video is created when writeFrequency is enabled.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr(
        "src.Simulation.simulation.Visualizer",
        lambda *a, **k: mock_vs
    )

    class MockVideo:
        """Mock VideoCreator that tracks invocation."""

        def __init__(self, **kwargs):
            self.called = False

        def createVideoFromRun(self, runNumber):
            self.called = True
            return "video.mp4"

    video = MockVideo()
    monkeypatch.setattr("src.IO.video.VideoCreator", lambda **k: video)

    sim = Simulation(config)
    sim.run_sim(runNumber=1, create_video=True)

    assert video.called


def test_run_sim_no_video(monkeypatch, config):
    """
    Ensure no plotting or video creation when writeFrequency is zero.
    """
    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr(
        "src.Simulation.simulation.Visualizer",
        lambda *a, **k: mock_vs
    )

    config = clone_config(
        config,
        IO={"writeFrequency": 0},
    )

    monkeypatch.setattr("src.IO.video.VideoCreator", MagicMock)

    sim = Simulation(config)
    sim.run_sim(runNumber=None, create_video=False)

    assert not mock_vs.plotting.called


def test_run_sim_multiple_steps(monkeypatch, config):
    """
    Verify plotting occurs across multiple timesteps.
    """
    config = clone_config(
        config,
        settings={"tStart": 0, "tEnd": 2, "nSteps": 2},
    )

    monkeypatch.setattr("src.Geometry.mesh.Mesh", lambda *a, **k: FakeMesh())

    mock_vs = MagicMock()
    monkeypatch.setattr(
        "src.Simulation.simulation.Visualizer",
        lambda *a, **k: mock_vs
    )

    monkeypatch.setattr("src.IO.video.VideoCreator", MagicMock)

    sim = Simulation(config)
    sim.run_sim(runNumber=1, create_video=False)

    assert mock_vs.plotting.called
