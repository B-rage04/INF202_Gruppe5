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

        print(
            f"len: {len(oil)}, mesh points: {len(self.mesh.points)}, mesh triangles: {len(self.mesh.triangles)}"
        )  # TODO remove

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
