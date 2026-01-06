import matplotlib.pyplot as plt
import meshio
import numpy as np

class Mesh:
    def __init__(self, file):
        self.mesh = meshio.read(file)

        self.points = self.mesh.points
        self.triangles = self.mesh.cells_dict["triangle"]
    
    def show(self):
        plt.triplot(self.points[:, 0], self.points[:, 1], self.triangles)
        plt.show()

mesh1 = Mesh("bay.msh")
mesh1.show()