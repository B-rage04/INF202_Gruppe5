import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh

    def plotting(self, oil, filepath="Output/images/"):
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "blarm", ["cadetblue", "darkcyan", "black"]
        )
        from pathlib import Path

        fig = plt.figure()
        plt.tripcolor(
            self.mesh.points[:, 0],
            self.mesh.points[:, 1],
            self.mesh.triangles,
            oil,
            shading="flat",
            cmap="viridis",
        )

        plt.colorbar(label="Oil concentration")

        if filepath:
            nextnr = 0
            while Path(filepath) / Path(f"oil_concentration{nextnr}.png").exists():
                nextnr += 1
            filename = Path(filepath) / Path(f"oil_concentration{nextnr}.png")

        if filename:
            out_dir = Path("output")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / filename
            if out_path.suffix == "":
                out_path = out_path.with_suffix(".png")
            plt.savefig(out_path)
            plt.close(fig)
            return str(out_path)
        else:
            plt.show()
