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

    def _initialize_color_range(self, oil):
        """Initialize vmin and vmax based on oil concentration."""
        if self.vmin is None or self.vmax is None:
            self.vmin = min(oil)
            self.vmax = max(oil)

    def _get_config(self, kwargs):
        """Retrieve and normalize config from kwargs or mesh."""
        cfg = kwargs.get("config", None)
        if cfg is None:
            cfg = getattr(self.mesh, "config", None)

        if isinstance(cfg, dict):
            try:
                cfg = Config.from_dict(cfg)
            except Exception:
                cfg = None

        return cfg

    def _create_base_plot(self, oil, cmap):
        """Create figure, axes, and base tripcolor plot with colorbar."""
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

        return fig, ax

    def _draw_fishing_zones(self, ax):
        """Draw fishing zones as red transparent polygons."""
        fishing_triangles = [
            cell.cords
            for cell in self.mesh.cells
            if cell.type == "triangle" and cell._isFishing
        ]

        if fishing_triangles:
            verts = [np.array(t)[:, :2] for t in fishing_triangles]

            coll = PolyCollection(
                verts,
                facecolors="red",
                alpha=0.1,
                edgecolors="none",
                linewidth=0,
                antialiased=False,
            )

            ax.add_collection(coll)

    def _draw_ship_marker(self, ax, config):
        """Draw ship marker if configured."""
        if not isinstance(config, Config):
            return False

        geometry = config.geometry if isinstance(config, Config) else {}
        ship_cfg = geometry.get("ship") if isinstance(geometry, dict) else None

        if ship_cfg and isinstance(ship_cfg, list) and len(ship_cfg) >= 2:
            ax.plot(
                ship_cfg[0],
                ship_cfg[1],
                marker="s",
                markersize=12,
                color="red",
                markeredgecolor="white",
                markeredgewidth=2,
                label="Ship (sink)",
                zorder=10,
            )
            return True

        return False

    def _draw_source_markers(self, ax, config):
        """Draw source markers if configured."""
        if not isinstance(config, Config):
            return False

        geometry = config.geometry if isinstance(config, Config) else {}
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
            return True

        return False

    def _draw_sink_markers(self, ax, config):
        """Draw sink markers if configured."""
        if not isinstance(config, Config):
            return False

        geometry = config.geometry if isinstance(config, Config) else {}
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
            return True

        return False

    def _add_legend(self, ax, has_ship, has_sources, has_sinks):
        """Add legend if any markers were drawn."""
        if has_ship or has_sources or has_sinks:
            ax.legend(loc="upper right", framealpha=0.8)

    def _add_total_oil_annotation(self, ax, config):
        """Add total oil annotation if totalOilFlag is enabled."""
        if not isinstance(config, Config):
            return

        totalOilFlag = bool(config.video.get("totalOilFlag", False))

        if totalOilFlag:
            try:
                total_oil = 0.0
                for cell in self.mesh.cells:
                    if getattr(cell, "type", None) == "triangle":
                        total_oil += float(cell.oil) * float(cell.area)

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
                pass

    def _save_or_show_plot(self, fig, filepath, run, step):
        """Save plot to file or show it."""
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

            outPath.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(outPath)
            plt.close(fig)
            return str(outPath)
        else:
            plt.show()
            plt.close(fig)
            return None

    def plotting(
        self,
        oil,
        filepath="Output/images/",
        run=None,
        step=None,
        **kwargs,
    ):
        """Create and save/show a visualization of oil concentration."""
        self._initialize_color_range(oil)

        config = self._get_config(kwargs)

        cmap = plt.cm.get_cmap("viridis")
        fig, ax = self._create_base_plot(oil, cmap)

        self._draw_fishing_zones(ax)

        has_ship = self._draw_ship_marker(ax, config)
        has_sources = self._draw_source_markers(ax, config)
        has_sinks = self._draw_sink_markers(ax, config)

        self._add_legend(ax, has_ship, has_sources, has_sinks)

        self._add_total_oil_annotation(ax, config)

        return self._save_or_show_plot(fig, filepath, run, step)
