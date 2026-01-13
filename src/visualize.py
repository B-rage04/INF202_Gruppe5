from pathlib import Path

import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh
        self.vmin = None
        self.vmax = None

    def plotting(self, oil, filepath="Output/images/", run=None, step=None, **kwargs):
        # Set vmin and vmax on first call
        if self.vmin is None or self.vmax is None:
            self.vmin = min(oil)
            self.vmax = max(oil)

        cmap = plt.cm.get_cmap("viridis")

        fig = plt.figure()
        ax = plt.gca()

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
        totalOilFlag = False
        if totalOilFlag:
            # Compute total oil amount (area-weighted sum over triangle cells)
            try:
                total_oil = 0.0
                for cell in self.mesh.cells:
                    if getattr(cell, "type", None) == "triangle":
                        total_oil += float(cell.oil) * float(cell.area)

                # Annotate in the top-left corner of the axes
                ax.text(
                    0.01,
                    0.99,
                    f"Total oil: {total_oil:.4f}",
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                    color="white",
                    bbox=dict(facecolor="black", alpha=0.5, boxstyle="round,pad=0.2"),
                    fontsize=10,
                )
            except Exception:
                # In case of any unexpected issue, skip annotation gracefully
                pass

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

            # ensure parent directory exists (some codepaths may target subfolders)
            outPath.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(outPath)
            plt.close(fig)
            return str(outPath)
        else:
            plt.show()
            plt.close(fig)
