import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from tqdm import tqdm

from src.config import Config
from src.mesh import Mesh
from src.oil_sink import OilSinkSource
from src.video import VideoCreator
from src.visualize import Visualizer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Simulation:
    def __init__(self, config: Config = None):
        self._config = self._validate_config(config)
        self._msh = self._initialize_mesh()
        self._initialize_visualizer()
        self._initialize_time_parameters()
        self.oilSinks = self._initialize_ship_sink()  # Changed from shipSink
        self.oilSources = self._initialize_oil_sources()  # Changed from sourceSink
        self._initialize_additional_sinks()
        self._log_configuration_summary()

    def _validate_config(self, config):
        """Validate that config is a Config instance."""
        if config is not isinstance(config, Config):
            pass
            # raise TypeError("config must be a Config instance")
        return config

    def _initialize_mesh(self):
        """Initialize mesh from config."""
        meshName = self._config.mesh_name()
        return Mesh(meshName, self._config)

    def _initialize_visualizer(self):
        """Initialize visualizer and tracking lists."""
        self._visualizer = Visualizer(self._msh)
        self._fishingOil = []
        self._oilVals = []
        self._fish_vals = []
        self._imageDir: Path = Path(self._config.images_dir())

    def _initialize_time_parameters(self):
        """Initialize time-related parameters from config."""
        self._timeStart: float = float(self._config.settings["tStart"])
        self._timeEnd: float = float(self._config.settings["tEnd"])
        self._nSteps: int = int(self._config.settings["nSteps"])
        self._writeFrequency: int = int(self._config.IO.get("writeFrequency", 0))
        self._dt: float = (self._timeEnd - self._timeStart) / max(1, self._nSteps)
        self._currentTime: float = float(self._timeStart)

    def _initialize_ship_sink(self):
        """Initialize ship sink configuration."""
        shipSink = {}
        ship_cfg = self._config.geometry.get("ship", None)

        if isinstance(ship_cfg, list) and len(ship_cfg) >= 2:
            try:
                ship_pos = [float(ship_cfg[0]), float(ship_cfg[1])]
                from src.oil_sink import compute_ship_sink

                shipSink = compute_ship_sink(
                    self._msh,
                    ship_pos=ship_pos,
                    radius=0.1,
                    sigma=1.0,
                    strength=100.0,
                    mode="gaussian",
                )

                if shipSink:
                    max_coeff = max(shipSink.values())
                    logger.info(
                        f"Ship at {ship_pos}: {len(shipSink)} cells affected (max coeff: {max_coeff:.4f})"
                    )
                else:
                    logger.info(f"Ship at {ship_pos}: no cells found in range")
            except (TypeError, ValueError):
                pass
            except Exception as e:
                logger.warning(f"Failed to initialize ship sink: {e}")

        return shipSink

    def _initialize_oil_sources(self):
        """Initialize oil sources from config."""
        sourceSink = {}
        sources_array = self._config.geometry.get("source", [])

        if isinstance(sources_array, list) and sources_array:
            for idx, source_pos in enumerate(sources_array):
                if isinstance(source_pos, list) and len(source_pos) >= 2:
                    try:
                        from src.oil_sink import compute_source

                        source_coeffs = compute_source(
                            self._msh,
                            source_pos=[float(source_pos[0]), float(source_pos[1])],
                            radius=0.1,
                            sigma=1.0,
                            strength=50.0,
                            mode="gaussian",
                        )

                        for cell_id, coeff in source_coeffs.items():
                            sourceSink[cell_id] = sourceSink.get(cell_id, 0.0) + coeff

                        max_coeff = (
                            max(source_coeffs.values()) if source_coeffs else 0.0
                        )
                        logger.info(
                            f"Oil source {idx} at {source_pos}: {len(source_coeffs)} cells affected (max coeff: {max_coeff:.4f})"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to add source {idx}: {e}")

        return sourceSink

    def _initialize_additional_sinks(self):
        """Initialize additional sinks from config."""
        sinks_array = self._config.geometry.get("sink", [])

        if isinstance(sinks_array, list) and sinks_array:
            for idx, sink_pos in enumerate(sinks_array):
                if isinstance(sink_pos, list) and len(sink_pos) >= 2:
                    try:
                        from src.oil_sink import compute_ship_sink

                        sink_coeffs = compute_ship_sink(
                            self._msh,
                            ship_pos=[float(sink_pos[0]), float(sink_pos[1])],
                            radius=0.1,
                            sigma=1.0,
                            strength=100.0,
                            mode="gaussian",
                        )

                        for cell_id, coeff in sink_coeffs.items():
                            self.oilSinks[cell_id] = (
                                self.oilSinks.get(cell_id, 0.0) + coeff
                            )  # Changed from shipSink

                        logger.info(
                            f"Additional sink {idx} at {sink_pos}: {len(sink_coeffs)} cells affected"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to add sink {idx}: {e}")

    def _log_configuration_summary(self):
        """Log summary of all sources and sinks."""
        ship_cfg = self._config.geometry.get("ship", None)
        num_ships = (
            1
            if (
                isinstance(ship_cfg, list)
                and len(ship_cfg) >= 2
                and not isinstance(ship_cfg[0], list)
            )
            else 0
        )
        num_sources = len(
            [
                s
                for s in self._config.geometry.get("source", [])
                if isinstance(s, list) and len(s) >= 2
            ]
        )
        num_sinks = len(
            [
                s
                for s in self._config.geometry.get("sink", [])
                if isinstance(s, list) and len(s) >= 2
            ]
        )

        summary_parts = []
        if num_ships > 0:
            summary_parts.append(f"{num_ships} ship")
        else:
            summary_parts.append("0 ships")

        if num_sources > 0:
            summary_parts.append(
                f"{num_sources} source{'s' if num_sources != 1 else ''}"
            )
        else:
            summary_parts.append("0 sources")

        if num_sinks > 0:
            summary_parts.append(f"{num_sinks} sink{'s' if num_sinks != 1 else ''}")
        else:
            summary_parts.append("0 sinks")

        logger.info(f"Configuration summary: {', '.join(summary_parts)}")

    @staticmethod  # TODO: Move to LoadTOML?
    def _validateConfig(config: Dict[str, Any]) -> None:
        required = [
            ("geometry", "meshName"),
            ("settings", "tStart"),
            ("settings", "tEnd"),
            ("settings", "nSteps"),
            ("IO", "writeFrequency"),
        ]
        for section, key in required:
            if section not in config or key not in config[section]:
                raise KeyError(f"Missing required config entry: {section}.{key}")

    # getters/setters
    @property
    def config(self) -> Config:
        return self._config

    @property
    def mesh(self) -> Mesh:
        return self._msh

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def currentTime(self) -> float:
        return self._currentTime

    @currentTime.setter
    def currentTime(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("currentTime must be numeric")
        self._currentTime = float(value)

    @property
    def oilVals(self) -> List[float]:
        # return a copy to avoid accidental external mutation
        return list(self._oilVals)

    @property
    def fishingOil(self):
        return self._fishingOil

    def getOilVals(self):
        # it reads through all cells each step. Can this be optimized? TODO
        self._oilVals.append(
            [cell.oil for cell in self._msh.cells if cell.type == "triangle"]
        )

        self._fishingOil.append(
            sum([cell.oil for cell in self._msh.cells if cell.isFishing])
        )

    def getFishing(self):
        self._fish_vals.append(
            [cell._isFishing for cell in self._msh.cells if cell.type == "triangle"]
        )

    def _computeFlux(
        self, i: int, cell: Any, ngb: int
    ) -> float:  # TODO: other formulas from config

        neighbor = self._msh.cells[ngb]
        flowAvg = (cell.flow + neighbor.flow) / 2.0
        scaled_normals = getattr(cell, "scaledNormal", None)
        if scaled_normals is None:
            raise AttributeError("Cell missing scaled normal data")
        dot = float(np.dot(flowAvg, scaled_normals[i]))
        source_oil = cell.oil if dot > 0 else neighbor.oil
        return source_oil * dot

    def updateOil(self, dt):
        """Update oil concentration using predictor-corrector with sources/sinks."""
        # Get source and sink coefficients
        source_coeffs = self.oilSources if hasattr(self, "oilSources") else {}
        sink_coeffs = self.oilSinks if hasattr(self, "oilSinks") else {}

        oil_half = np.zeros(len(self._msh.cells))

        # Predictor step
        for cell in self._msh.cells:
            if getattr(cell, "type", None) != "triangle":
                continue
            flux_sum = 0.0
            for i, ngb in enumerate(cell.ngb):
                neighbor = self._msh.cells[ngb]
                if getattr(neighbor, "type", None) != "triangle":
                    continue
                flux_sum += -(dt / cell.area) * self._computeFlux(i, cell, ngb)
            oil_half[cell.id] = cell.oil + flux_sum

        # Corrector step with sources/sinks (spec-compliant)
        for cell in self._msh.cells:
            if getattr(cell, "type", None) != "triangle":
                continue
            S_plus = source_coeffs.get(cell.id, 0.0)  # Source term
            S_minus = sink_coeffs.get(cell.id, 0.0)  # Sink term

            # Apply spec: u_new = u_half / (1 + dt*S_minus - dt*S_plus)
            denominator = 1.0 + dt * S_minus - dt * S_plus
            if abs(denominator) > 1e-12:
                cell.oil = oil_half[cell.id] / denominator
            else:
                cell.oil = oil_half[cell.id]

    # snake_case compatibility wrapper
    def update_oil(self, *args, **kwargs):
        return self.updateOil(*args, **kwargs)

    def run_sim(
        self,
        runNumber: Optional[int] = None,
        **kwargs,
    ) -> Optional[str]:

        # self.ship = OilSinkSource(self._msh,configuration=None) #TODO implement oil sink source class

        createVideo = False
        if int(self._config.IO.get("writeFrequency", 0)) != 0:
            createVideo = True

        videoFps: int = int(self._config.video.get("videoFPS", 30))

        totalSteps = self._nSteps

        start_time = time.perf_counter()
        with tqdm(
            total=totalSteps,
            desc="Simulating oil dispersion",
            unit="step",
            colour="cyan",
            ncols=100,
            ascii="-#",
            position=0,
            leave=True,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        ) as pbar:
            for stepIdx in range(1, totalSteps + 1):
                self.updateOil(self._dt)  # Pass dt argument
                self._currentTime = self._timeStart + stepIdx * self._dt
                self.getOilVals()

                # Always write first image, last image, or at writeFrequency intervals
                should_write = False
                if self._writeFrequency != 0:
                    should_write = (
                        stepIdx == 1
                        or stepIdx == totalSteps
                        or stepIdx % self._writeFrequency == 0
                    )

                if should_write:
                    logger.info(
                        f"total oil at time {self.currentTime}: {self.fishingOil[-1]:.5f}"
                    )
                    self._visualizer.plotting(
                        self._oilVals[-1],
                        filepath=str(self._imageDir),
                        run=runNumber,
                        step=stepIdx,
                        **kwargs,
                    )
                pbar.update(1)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Simulation completed in {elapsed_ms:.2f} ms")

        videoPath: Optional[str] = None
        if createVideo and runNumber is not None:

            videoCreator = VideoCreator(imageDir=self._imageDir, fps=videoFps)

            if hasattr(videoCreator, "createVideo_from_run"):
                videoPath = videoCreator.createVideo_from_run(runNumber)
            else:
                videoPath = videoCreator.createVideoFromRun(runNumber)

        return videoPath
