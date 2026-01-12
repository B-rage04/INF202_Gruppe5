from pathlib import Path

import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh
        self.vmin = None
        self.vmax = None

    def plotting(self, oil, filepath="Output/images/", run=None, step=None):
        # Set vmin and vmax on first call
        if self.vmin is None or self.vmax is None:
            self.vmin = min(oil)
            self.vmax = max(oil)

        cmap = plt.cm.get_cmap("viridis")

        fig = plt.figure()

        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            oil,
            shading="flat",
            cmap=cmap,
            vmin=self.vmin,
            vmax=self.vmax,
        )

        plt.colorbar(label="Oil concentration")

        if filepath:
            outDir = Path(filepath)
            outDir.mkdir(parents=True, exist_ok=True)

            if run is not None:
                runDir = outDir / f"run{run}"
                runDir.mkdir(parents=True, exist_ok=True)
                if step is not None:
                    outPath = runDir / f"oilStep{step}.png"
                else:
                    outPath = runDir / f"oilRun{run}.png"
            else:
                nextnr = 0
                while (outDir / f"oil/{nextnr}.png").exists():
                    nextnr += 1
                outPath = outDir / f"oil/{nextnr}.png"

            plt.savefig(outPath)
            plt.close(fig)
            return str(outPath)
        else:
            plt.show()
            plt.close(fig)
