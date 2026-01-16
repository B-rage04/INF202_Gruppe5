from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

from src.config import Config


class Visualizer:
    def __init__(self, mesh):
        self.mesh = mesh
        self.vmin = None
        self.vmax = None

        self.triangle_cells = [
            cell for cell in mesh.cells if getattr(cell, "type", None) == "triangle"
        ]

    def plotting(
        self,
        oil,
        filepath="Output/images/",
        run=None,
        step=None,
        **kwargs,
    ):
        # Set vmin and vmax on first call
        if self.vmin is None or self.vmax is None:
            self.vmin = min(oil)
            self.vmax = max(oil)

        # Prefer an explicit config passed in kwargs, otherwise fall back
        # to `mesh.config` (new OOP `Config`). Accept legacy dict too.
        cfg = kwargs.get("config", None)
        if cfg is None:
            cfg = getattr(self.mesh, "config", None)

        if isinstance(cfg, dict):
            try:
                cfg = Config.from_dict(cfg)
            except Exception:
                cfg = None

        totalOilFlag = False
        if isinstance(cfg, Config):
            totalOilFlag = bool(cfg.video.get("totalOilFlag", False))

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

        fishing_triangles = [
            cell.cords
            for cell in self.mesh.cells
            if cell.type == "triangle" and cell._isFishing
        ]

        if fishing_triangles:
            # 2. Convert to a collection of polygons
            # We only care about the (x, y) coordinates for each triangle
            verts = [np.array(t)[:, :2] for t in fishing_triangles]

            # 3. Create the collection
            coll = PolyCollection(
                verts,
                facecolors="red",
                alpha=0.1,
                edgecolors="none",
                linewidth=0,
                antialiased=False,
            )

            ax.add_collection(coll)

        plt.colorbar(label="Oil concentration")

        # Draw ship position (if configured)
        geometry = cfg.geometry if isinstance(cfg, Config) else {}
        ship_cfg = geometry.get("ship") if isinstance(geometry, dict) else None
        if ship_cfg:
            ship_pos = ship_cfg
            if isinstance(ship_pos, list) and len(ship_pos) >= 2:
                ax.plot(
                    ship_pos[0],
                    ship_pos[1],
                    marker="s",
                    markersize=12,
                    color="red",
                    markeredgecolor="white",
                    markeredgewidth=2,
                    label="Ship (sink)",
                    zorder=10,
                )

        # Draw source positions (if configured)
        sources = geometry.get("source", []) if isinstance(geometry, dict) else []
        if isinstance(sources, list) and sources:
            for idx, source_pos in enumerate(sources):
                if isinstance(source_pos, list) and len(source_pos) >= 2:
                    ax.plot(
                        source_pos[0],
                        source_pos[1],
                        marker="^",
                        markersize=12,
                        color="lime",
                        markeredgecolor="white",
                        markeredgewidth=2,
                        label=f"Source {idx+1}" if idx == 0 else "",
                        zorder=10,
                    )

        # Draw sink positions (if configured)
        sinks = geometry.get("sink", []) if isinstance(geometry, dict) else []
        if isinstance(sinks, list) and sinks:
            for idx, sink_pos in enumerate(sinks):
                if isinstance(sink_pos, list) and len(sink_pos) >= 2:
                    ax.plot(
                        sink_pos[0],
                        sink_pos[1],
                        marker="v",
                        markersize=12,
                        color="orange",
                        markeredgecolor="white",
                        markeredgewidth=2,
                        label=f"Sink {idx+1}" if idx == 0 else "",
                        zorder=10,
                    )

        # Add legend if any markers were drawn
        if ship_cfg or sources or sinks:
            ax.legend(loc="upper right", framealpha=0.8)

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
