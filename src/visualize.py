import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

from mesh import Mesh


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh

    def plotting(self, u, filename=None):

        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "blarm", ["cadetblue", "darkcyan", "black"]
        )
        plt.figure()
        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            u,
            shading="flat",
            cmap="viridis",
        )

        points = self.mesh.points
        triangles = self.mesh.triangles

        # plt.triplot(points[:, 0], points[:, 1], triangles, color="blue")
        plt.colorbar(label="Oil concentration")
        plt.show()

        if filename:
            pass
        else:
            plt.show()
