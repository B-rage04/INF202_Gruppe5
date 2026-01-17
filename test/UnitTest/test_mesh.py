from types import SimpleNamespace

import numpy as np
import numpy.testing as npt
import pytest

from src.IO.LoadTOML import LoadTOML
from src.Geometry.mesh import Mesh

configloader = LoadTOML()
config = configloader.loadConfigFile("Input\BaseSimConfig.toml")

from test.utilitiesTests.MeshTest import meshTest
from test.utilitiesTests.ConfigTest import configTest


@pytest.fixture
def tmpMsh():
    msh = meshTest()
    config = configTest()
  

    return msh, config
class DummyMeshIO:
    def __init__(self):
        self.points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        self.cells_dict = {"triangle": np.array([[0, 1, 2]])}
        self.cells = [SimpleNamespace(type="triangle", data=np.array([[0, 1, 2]]))]


@pytest.fixture
def tmp_mesh(monkeypatch, tmp_path):
    # monkeypatch meshio.read to return our dummy mesh
    def fake_read(path):
        return DummyMeshIO()

    monkeypatch.setattr("meshio.read", fake_read)
    # create a dummy file path
    p = tmp_path / "dummy.msh"
    p.write_text("dummy")
    return str(p)


def test_mesh_loads_points_and_triangles(
    tmp_mesh,
):  # TODO: assert should be the last thing in the test
    m = Mesh(tmp_mesh, config)
    assert m.points.shape == (3, 3)
    npt.assert_array_equal(m.triangles, np.array([[0, 1, 2]]))


#Tests for reload-method

def testReload(tmpMsh):
    msh, config = tmpMsh
    file = "test/utilitiesTests/simpleMesh.msh"
    msh.reload(file, config)
    assert msh._cells == msh._cellFactory()

def testReloadFileNotString(tmpMsh):
    msh, config = tmpMsh
    file = 0
    with pytest.raises(TypeError):
        msh.reload(file, config)

def testReloadFilePathError(tmpMsh):
    msh, config = tmpMsh
    file = "test/utilitiesTests/doesntexist.msh"
    with pytest.raises(FileNotFoundError):
        msh.reload(file, config)
 