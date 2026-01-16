from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import os
from types import SimpleNamespace

import numpy as np
import pytest

from src.Simulation.visualize import Visualizer

# TODO: tests should be short and only test/assert one thing each
# TODO: Fix names and Fixtures of "repeat" tests


class TestMesh:
    def __init__(self):
        self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        self.cells_dict = {"triangle": np.array([[0, 1, 2]])}
        self.triangles = np.array([[0, 1, 2]])
        self.cells = [SimpleNamespace(type="triangle", oil=1.0, area=1.0)]


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


def test_plotting_sets_vmax(visualizer, tmp_path):
    (tmp_path / "oil").mkdir()
    visualizer.plotting([0.1], filepath=tmp_path)
    assert visualizer.vmax == 0.1


def test_plotting_sets_vmin(visualizer, tmp_path):
    (tmp_path / "oil").mkdir()
    visualizer.plotting([0.1], filepath=tmp_path)
    assert visualizer.vmin == 0.1


def test_plotting_filepath_no_run(visualizer, tmp_path):
    (tmp_path / "oil").mkdir()
    result = visualizer.plotting([0.1], filepath=tmp_path)
    ex_path = Path(tmp_path) / "oil" / "0.png"
    assert result == str(ex_path)


def test_plotting_with_run_not_step1(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1)
    assert os.path.exists(result)


def test_plotting_with_run_not_step2(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1)
    assert "run1" in result


def test_plotting_with_run_not_step(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1)
    ex_path = Path(tmp_path) / "run1" / "oilRun1.png"
    assert result == str(ex_path)


def test_plotting_run_with_steo1(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1, step=10)
    assert os.path.exists(result)


def test_plotting_run_with_steo2(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1, step=10)
    assert "run1" in result


def test_plotting_run_with_steo3(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, run=1, step=10)
    expected_path = Path(tmp_path) / "run1" / "oilStep10.png"
    assert Path(result) == expected_path


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
    oil1 = [0.1]
    visualizer.plotting(oil1, filepath=tmp_path, run=1, step=1)
    visualizer.plotting(oil2, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmin == 0.1


def test_v_persist_oil2_vmin(visualizer, tmp_path):
    oil2 = [0.2]
    oil1 = [0.1]
    visualizer.plotting(oil1, filepath=tmp_path, run=1, step=1)
    visualizer.plotting(oil2, filepath=tmp_path, run=1, step=1)
    assert visualizer.vmin == 0.1


def test_plotting_file_incr(visualizer, tmp_path):
    oil_dir = tmp_path / "oil"
    oil_dir.mkdir(parents=True, exist_ok=True)
    (oil_dir / "0.png").write_text("")
    (oil_dir / "1.png").write_text("")
    result = visualizer.plotting([0.1], filepath=tmp_path)
    ex_path = oil_dir / "2.png"
    assert Path(result) == ex_path


def test_total_oil_exception(tmp_path):
    class BadMesh:
        points = np.array([[0, 0], [1, 0], [0, 1]])
        triangles = np.array([[0, 1, 2]])
        cells = [SimpleNamespace(type="triangle", oil="invalid", area=1.0)]

    vslzr = Visualizer(BadMesh())
    result = vslzr.plotting([0.1], filepath=tmp_path)
    assert Path(result).exists()


def test_show(monkeypatch, visualizer):
    shown = {"called": False}

    def fake_show():
        shown["called"] = True

    monkeypatch.setattr("matplotlib.pyplot.show", fake_show)
    visualizer.plotting([0.1], filepath=None)
    assert shown["called"]


def test_plotting_file_incr_no_existing_files(visualizer, tmp_path):
    oil_dir = tmp_path / "oil"
    oil_dir.mkdir(parents=True, exist_ok=True)
    result = visualizer.plotting([0.1], filepath=tmp_path)
    ex_path = oil_dir / "0.png"
    assert Path(result) == ex_path


# Grrrr Gabriel
def test_total_oil_flag_false(visualizer, tmp_path):
    result = visualizer.plotting([0.1], filepath=tmp_path, totalOilFlag=False)
    assert Path(result).exists()


# Grrrrrr Me
def test_total_oil_non_triangle_cell(tmp_path):
    class Mesh:
        points = np.array([[0, 0], [1, 0], [0, 1]])
        triangles = np.array([[0, 1, 2]])
        cells = [
            SimpleNamespace(type="triangle", oil=1.0, area=1.0),
            SimpleNamespace(type="quad", oil=2.0, area=1.0),
        ]

    viz = Visualizer(Mesh())
    result = viz.plotting([0.1], filepath=tmp_path)
    assert Path(result).exists()
