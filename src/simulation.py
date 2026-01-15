import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import time

import numpy as np
from tqdm import tqdm

from src.mesh import Mesh
from src.video import VideoCreator
from src.visualize import Visualizer

from src.oil_sink import OilSinkSource

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Simulation:
    def __init__(self, config: Dict[str, Any]):
        self._validateConfig(config)
        self._config = config

        meshName = self._config["geometry"]["meshName"]
        self._msh = Mesh(meshName,self._config)

        self._visualizer = Visualizer(self._msh)

        # Output directory for images/videos; default to Output/images/
        self._imageDir: Path = Path(
            self._config.get("IO", {}).get("imagesDir", "Output/images/")
        )

        self._timeStart: float = float(self._config["settings"]["tStart"])
        self._timeEnd: float = float(self._config["settings"]["tEnd"])
        self._nSteps: int = int(self._config["settings"]["nSteps"])
        self._writeFrequency: int = int(self._config["IO"]["writeFrequency"])

        self._dt: float = (self._timeEnd - self._timeStart) / max(1, self._nSteps)
        self._currentTime: float = float(self._timeStart)

        self._oilVals = []
        self._fish_vals = []

        # Optional oil collection ship configuration
        self.shipSink = {}
        if "geometry" in self.config:
            ship_cfg = self.config["geometry"].get("ship", None)
            if isinstance(ship_cfg, list) and len(ship_cfg) >= 2:
                # Check if it's a valid [x, y] position (both elements should be numbers, not lists)
                try:
                    ship_pos = [float(ship_cfg[0]), float(ship_cfg[1])]
                    
                    from src.oil_sink import compute_ship_sink

                    self.shipSink = compute_ship_sink(
                        self._msh,
                        ship_pos=ship_pos,
                        radius=0.1,
                        sigma=1.0,
                        strength=100.0,
                        mode="gaussian",
                    )
                    if self.shipSink:
                        max_coeff = max(self.shipSink.values())
                        logger.info(f"Ship at {ship_pos}: {len(self.shipSink)} cells affected (max coeff: {max_coeff:.4f})")
                    else:
                        logger.info(f"Ship at {ship_pos}: no cells found in range")
                except (TypeError, ValueError):
                    # ship is not a valid [x, y] position, skip
                    pass
                except Exception as e:
                    logger.warning(f"Failed to initialize ship sink: {e}")

        # Oil sources from geometry.source array (can be list of [x, y] pairs)
        self.sourceSink = {}
        if "geometry" in self.config:
            sources_array = self.config["geometry"].get("source", [])
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
                            # Merge with existing source coefficients
                            for cell_id, coeff in source_coeffs.items():
                                self.sourceSink[cell_id] = self.sourceSink.get(cell_id, 0.0) + coeff
                            logger.info(f"Oil source {idx} at {source_pos}: {len(source_coeffs)} cells affected")
                        except Exception as e:
                            logger.warning(f"Failed to add source {idx}: {e}")

        # Additional sinks from geometry.sink array
        if "geometry" in self.config:
            sinks_array = self.config["geometry"].get("sink", [])
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
                            # Merge with existing sink coefficients (ship)
                            for cell_id, coeff in sink_coeffs.items():
                                self.shipSink[cell_id] = self.shipSink.get(cell_id, 0.0) + coeff
                            logger.info(f"Additional sink {idx} at {sink_pos}: {len(sink_coeffs)} cells affected")
                        except Exception as e:
                            logger.warning(f"Failed to add sink {idx}: {e}")

        # Summary log of all sources and sinks
        # Check if ship is a valid [x, y] position (not a list of lists)
        ship_cfg = self.config.get("geometry", {}).get("ship", None)
        num_ships = 1 if (isinstance(ship_cfg, list) and len(ship_cfg) >= 2 and not isinstance(ship_cfg[0], list)) else 0
        num_sources = len([s for s in self.config.get("geometry", {}).get("source", []) if isinstance(s, list) and len(s) >= 2])
        num_sinks = len([s for s in self.config.get("geometry", {}).get("sink", []) if isinstance(s, list) and len(s) >= 2])
        
        summary_parts = []
        if num_ships > 0:
            summary_parts.append(f"{num_ships} ship")
        else:
            summary_parts.append("0 ships")
            
        if num_sources > 0:
            summary_parts.append(f"{num_sources} source{'s' if num_sources != 1 else ''}")
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
    def config(self) -> Dict[str, Any]:
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

    def getOilVals(self):
        # it reads through all cells each step. Can this be optimized? TODO
        self._oilVals.append(
            [cell.oil for cell in self._msh.cells if cell.type == "triangle"]
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

    def updateOil(self):
        # Accumulate flux contributions per cell
        triangle_cells = [
            c for c in self._msh.cells if getattr(c, "type", None) == "triangle"
        ]
        for cell in triangle_cells:
            # respect existing `newOil` attribute; warn if it's explicitly None
            if not hasattr(cell, "newOil"):
                cell.newOil = []
            elif cell.newOil is None:
                print(f"Warning: Cell, {getattr(cell, 'id', '?')}, was None")
                continue

            for i, ngb in enumerate(cell.ngb):
                neighbor = self._msh.cells[ngb]
                if getattr(neighbor, "type", None) != "triangle":
                    continue
                delta = -(self._dt / cell.area) * self._computeFlux(i, cell, ngb)
                cell.newOil.append(delta)

        # Apply accumulated updates with source/sink formula:
        # u_i^{n+1} = u_i^{n+1/2} / (1 + Δt*S_i^- - Δt*S_i^+)
        for cell in triangle_cells:
            deltas = list(getattr(cell, "newOil", []))
            
            # Compute u_i^{n+1/2} = u_i^n + flux contributions
            u_intermediate = float(cell.oil) + (sum(deltas) if deltas else 0.0)
            
            # Get sink coefficient S_i^- (positive value for removal)
            sink_coeff = 0.0
            if self.shipSink and cell.id in self.shipSink:
                sink_coeff = self.shipSink[cell.id]
            
            # Get source coefficient S_i^+ (positive value for injection)
            source_coeff = 0.0
            if self.sourceSink and cell.id in self.sourceSink:
                source_coeff = self.sourceSink[cell.id]
            
            # Apply formula: u_i^{n+1} = u_i^{n+1/2} / (1 + Δt*S_i^- - Δt*S_i^+)
            denominator = 1.0 + self._dt * sink_coeff - self._dt * source_coeff
            
            if abs(denominator) > 1e-10:  # Avoid division by zero
                cell.oil = u_intermediate / denominator
            else:
                cell.oil = u_intermediate
            
            cell.newOil.clear()

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
        if self._config.get("IO", {}).get("writeFrequency", 0) is not 0:
            createVideo = True

        videoFps: int = int(self._config.get("video", {}).get("videoFPS", 30))

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
                self.updateOil()
                self._currentTime = self._timeStart + stepIdx * self._dt
                self.getOilVals()
                if self._writeFrequency != 0 and stepIdx % self._writeFrequency == 0:
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
                
        if stepIdx % self._writeFrequency == 0:
            self._visualizer.plotting(
                self._oilVals[-1],
                filepath=str(self._imageDir),
                run=runNumber,
                step=stepIdx,
                **kwargs,
            )

        videoPath: Optional[str] = None
        if createVideo and runNumber is not None:

            videoCreator = VideoCreator(imageDir=self._imageDir, fps=videoFps)

            if hasattr(videoCreator, "createVideo_from_run"):
                videoPath = videoCreator.createVideo_from_run(runNumber)
            else:
                videoPath = videoCreator.createVideoFromRun(runNumber)

        return videoPath
