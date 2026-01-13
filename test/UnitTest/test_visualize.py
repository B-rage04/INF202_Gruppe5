import matplotlib

matplotlib.use("Agg")

import os
from types import SimpleNamespace

import numpy as np
import pytest

from src.visualize import Visualizer

# TODO: test shood be short and only test/asert one thing each
# TODO: Fix names and Fcitures of "reapeet" tests


class TestMesh:
    def __init__(self):
        self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        self.cells_dict = {"triangle": np.array([[0, 1, 2]])}
        self.triangles = np.array([[0, 1, 2]])
        self.cells = [SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]]))]


@pytest.fixture
def test_mesh():
    return TestMesh()

@pytest.fixture
def visualizer(test_mesh):
    return Visualizer(test_mesh)

def test_visualizer_init_mesh(test_mesh):
    vslzr = Visualizer(test_mesh)
    assert vslzr.mesh == test_mesh

def test_visualizer_init_vmin(test_mesh):
    vslzr = Visualizer(test_mesh)
    assert vslzr.vmin == None

def test_visualizer_init_vmax(test_mesh):
    vslzr = Visualizer(test_mesh)
    assert vslzr.vmax == None

def test_plotting_sets_vmax(visualizer):
    oil = [0.1]
    visualizer.plotting(oil)
    assert visualizer.vmax == 0.1

def test_plotting_sets_vmin(visualizer):
    oil = [0.1]
    visualizer.plotting(oil)
    assert visualizer.vmin == 0.1

def test_plotting_filepath_no_run(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path)
    assert "oil_0.png" in result

def test_plotting_filepath_no_run(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path)
    assert os.path.exists(result)

def test_plotting_with_run_not_step1(visualizer, tmp_path):
    oil = [0.1]

    result = visualizer.plotting(oil, filepath=tmp_path, run=1)
    assert os.path.exists(result)

def test_plotting_with_run_not_step2(visualizer, tmp_path):
    oil = [0.1]

    result = visualizer.plotting(oil, filepath=tmp_path, run=1)
    assert "run1" in result

def test_plotting_with_run_not_step(visualizer, tmp_path):
    oil = [0.1]

    result = visualizer.plotting(oil, filepath=tmp_path, run=1)
    assert "oil_run1.png" in result

def test_plotting_run_with_steo1(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path, run=1, step=10)
    assert os.path.exists(result)

def test_plotting_run_with_steo2(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path, run=1, step=10)
    assert "run1" in result

def test_plotting_run_with_steo3(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path, run=1, step=10)
    assert "oil_step10.png" in result

def test_v_persist(visualizer, tmp_path):
    oil1 = [0.1]
    oil2 = [0.2]

    visualizer.plotting(oil1, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmax == 0.1
    assert visualizer.vmin == 0.1

    visualizer.plotting(oil2, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmax == 0.1
    assert visualizer.vmin == 0.1

def test_v_persist_oil1_vmax(visualizer, tmp_path):
    oil1 = [0.1]

    visualizer.plotting(oil1, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmax == 0.1

def test_v_persist_oil1_vmin(visualizer, tmp_path):
    oil1 = [0.1]

    visualizer.plotting(oil1, filepath=tmp_path, run=1, step=1)

    assert visualizer.vmin == 0.1

def test_v_persist_oil2_vmax(visualizer, tmp_path):
    oil2 = [0.2]

    visualizer.plotting(oil2, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmax == 0.1
    assert visualizer.vmin == 0.1

def test_v_persist_oil2_vmin(visualizer, tmp_path):
    oil2 = [0.2]

    visualizer.plotting(oil2, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmin == 0.1

def test_plotting_file_incr(visualizer, tmp_path):
    oil = [0.1]
    (tmp_path / "oil_0.png").write_text("")
    (tmp_path / "oil_1.png").write_text("")
    result = visualizer.plotting(oil, filepath=tmp_path)
    assert "oil_2.png" in result

def test_show(monkeypatch, visualizer):
    shown = {"called": False}

    def fake_show():
        shown["called"] = True

    monkeypatch.setattr("matplotlib.pyplot.show", fake_show)
    visualizer.plotting([0.1], filepath=None)
    assert shown["called"]
