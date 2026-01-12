import matplotlib
matplotlib.use("Agg")

import pytest
import os
import numpy as np
from src.visualize import Visualizer
from types import SimpleNamespace


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

def test_visualizer_init(test_mesh):
    vslzr = Visualizer(test_mesh)
    assert vslzr.mesh == test_mesh
    assert vslzr.vmin == None
    assert vslzr.vmax == None

def test_plotting_sets_vmin_vmax(visualizer):
    oil = [0.1]
    visualizer.plotting(oil)
    assert visualizer.vmin == 0.1
    assert visualizer.vmax == 0.1

def test_plotting_filepath_no_run(visualizer, tmp_path):
    oil = [0.1]
    result = visualizer.plotting(oil, filepath=tmp_path)
    assert os.path.exists(result)
    assert "oil_0.png" in result

def test_plotting_with_run_not_step(visualizer):
    oil = [0.1]
    filepath = "test_images"
    if not os.path.exists(filepath):
        os.makedir(filepath)
    result = visualizer.plotting(oil, filepath=filepath, run=1)
    assert os.path.exists(result)
    assert "run1" in result
    assert "oil_run1.png" in result

def test_plotting_run_with_steo(visualizer):
    oil = [0.1]
    filepath = "test_images"
    if not os.path.exists(filepath):
        os.makedir(filepath)
    result = visualizer.plotting(oil, filepath=filepath, run=1, step=10)
    assert os.path.exists(result)
    assert "run1" in result
    assert "oil_step10.png" in result

def test_v_persist(visualizer):
    oil1 = [0.1]
    oil2 = [0.2]
    filepath = "test_images"
    if not os.path.exists(filepath):
        os.makedir(filepath)
    visualizer.plotting(oil1, filepath=filepath, run=1, step=1)
    assert visualizer.vmax == 0.1
    assert visualizer.vmin == 0.1

    visualizer.plotting(oil2, filepath=filepath, run=1, step=1)
    assert visualizer.vmax == 0.1
    assert visualizer.vmin == 0.1

def test_plotting_file_incr(visualizer, tmp_path):
    oil = [0.1]

    (tmp_path / "oil_0.png").write_text("")
    (tmp_path / "oil_1.png").write_text("")
    filepath = "test_images"

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    result = visualizer.plotting(oil, filepath=tmp_path)
    assert "oil_2.png" in result

def test_show(monkeypatch, visualizer):
    shown = {"called": False}

    def fake_show():
        shown["called"] = True
    
    monkeypatch.setattr("matplotlib.pyplot.show", fake_show)
    visualizer.plotting([0.1], filepath = None)
    assert shown["called"]
