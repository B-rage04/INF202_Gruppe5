import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

 
class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh

    def plotting(self, oil, filename=None):

        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "blarm", ["cadetblue", "darkcyan", "black"]
        )
        plt.figure()
        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            oil,
            shading="flat",
            cmap="viridis",
        )

        plt.colorbar(label="Oil concentration")
        plt.show()

        if filename:
            pass
        else:
            plt.show()
