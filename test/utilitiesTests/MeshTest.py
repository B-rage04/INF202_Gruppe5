def meshTest():
    from src.mesh import Mesh
    from test.utilitiesTests.ConfigTest import configTest
    config = configTest()
    print(type(config))
    msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)
    return msh

msh = meshTest()