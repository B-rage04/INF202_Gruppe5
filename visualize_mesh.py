import matplotlib.pyplot as plt
import meshio
import numpy as np

import pyvista as pv

mesh = meshio.read("bay.msh")

pl = pv.Plotter()

pl.add_mesh(mesh, color="blue", show_edges=True, cmap="virdis")

pl.show()