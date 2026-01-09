import numpy as np
import pytest

from src.Cells.cell import Cell
from src.simulation import Simulation

from .test_Shered import DummyVisualizer, MockMesh
 

def test_simulation_runs_and_calls_visualizer(monkeypatch):
    mesh = MockMesh()

    import src.simulation as sim_mod

    monkeypatch.setattr(sim_mod, "Visualizer", DummyVisualizer)

    s = Simulation(mesh)
    assert s.vs.last_plotted is None

    s.run_sim()
    assert isinstance(s.vs.last_plotted, list)
    assert len(s.vs.last_plotted) == len(s.cells)
