def meshTest():
    from test.utilitiesTests.ConfigTest import configTest

    from src.mesh import Mesh

    config = configTest()
    print(type(config))
    msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)
    return msh


msh = meshTest()
