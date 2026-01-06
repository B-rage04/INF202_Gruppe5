import matplotlib.pyplot as plt
import meshio
import numpy as np


mesh = meshio.read("bay.msh")

points = mesh.points
triangles = mesh.cells_dict["triangle"]

plt.triplot(points[:, 0], points[:, 1], triangles)
plt.show()