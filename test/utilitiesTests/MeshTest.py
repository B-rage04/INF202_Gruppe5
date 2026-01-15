class MeshTest:
    def __init__(self):
        pass

    def __call__(self):
        from src.mesh import Mesh
        from test.utilitiesTests.config import ConfigTest
        config = ConfigTest()()
        msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)
        return msh
