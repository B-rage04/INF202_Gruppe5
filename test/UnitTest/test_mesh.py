import pytest
from src.Geometry.mesh import Mesh
from test.utilitiesTests.MeshTest import meshTest
from test.utilitiesTests.ConfigTest import configTest

@pytest.fixture
def tmpMsh():
    msh = meshTest()
    return msh

@pytest.fixture
def tmpConfig():
    config = configTest()
    return config


#Tests for wheter the mesh loads correctly from .msh file

def testMeshLoadsShape(tmpConfig):
    config = tmpConfig
    msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)
    assert msh.points.shape == (5,3)


def testMeshLoadsTriangles(tmpConfig):
    config = tmpConfig
    msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)
    assert len(msh.triangles) == (4)

#Tests for error catching in init

def testMeshInitTypeError(tmpConfig):
    config = tmpConfig
    with pytest.raises(TypeError):
        Mesh([], config)

def testMeshInitFileNotFoundError(tmpConfig):
    config = tmpConfig
    with pytest.raises(FileNotFoundError):
        Mesh("test/utilitiesTests/doesntexist.msh", config)


def testMeshInitTypeErrorConfig():
    config = 123
    with pytest.raises(TypeError):
        Mesh("test/utilitiesTests/simpleMesh.msh", config)


#Tests for reload-method

def testReload(tmpMsh):
    msh= tmpMsh
    file = "test/utilitiesTests/simpleMesh.msh"
    msh.reload(file)
    assert msh._cells == msh._cellFactory()

def testReloadFileNotString(tmpMsh):
    msh = tmpMsh
    file = 0
    with pytest.raises(TypeError):
        msh.reload(file)

def testReloadFilePathError(tmpMsh):
    msh= tmpMsh
    file = "test/utilitiesTests/doesntexist.msh"
    with pytest.raises(FileNotFoundError):
        msh.reload(file)
 