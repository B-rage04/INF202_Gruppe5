from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh

    def plotting(self, oil, filepath="Output/images/", run=None, step=None):
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "blarm", ["cadetblue", "darkcyan", "black"]
        )

        fig = plt.figure()
        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            oil,
            shading="flat",
            cmap=custom_cmap,
        )

        plt.colorbar(label="Oil concentration")

        if filepath:
            out_dir = Path(filepath)
            out_dir.mkdir(parents=True, exist_ok=True)

            if run is not None:
                run_dir = out_dir / f"run{run}"
                run_dir.mkdir(parents=True, exist_ok=True)
                if step is not None:
                    out_path = run_dir / f"oil_step{step}.png"
                else:
                    out_path = run_dir / f"oil_run{run}.png"
            else:
                nextnr = 0
                while (out_dir / f"oil_{nextnr}.png").exists():
                    nextnr += 1
                out_path = out_dir / f"oil_{nextnr}.png"

            plt.savefig(out_path)
            plt.close(fig)
            return str(out_path)
        else:
            plt.show()
            plt.close(fig)
