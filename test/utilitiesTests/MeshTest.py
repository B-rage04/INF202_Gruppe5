


from src.mesh import Mesh
from test.utilitiesTests.config import config
config = config()
print(type(config))
msh = Mesh("test/utilitiesTests/simpleMesh.msh", config)

#print(msh)