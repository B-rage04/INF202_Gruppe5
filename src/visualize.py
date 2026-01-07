import matplotlib.colors as mcolors
from mesh import Mesh
import numpy as np


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh

        custom_cmap = mcolors.LinearSegmentedColormap.from_list("blarm", ["cadetblue", "gray", "black"])
        plt.figure()
        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            u,
            shading="flat",
            cmap=custom_cmap,
        )

        points = self.mesh.points
        triangles = self.mesh.triangles

        #plt.triplot(points[:, 0], points[:, 1], triangles, color="blue")
        plt.colorbar(label="Oil concentration")
        plt.show()

        if filename:
            pass
        else:
            plt.show()
