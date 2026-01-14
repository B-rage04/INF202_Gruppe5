import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from tqdm import tqdm

from src.mesh import Mesh
from src.video import VideoCreator
from src.visualize import Visualizer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Simulation:
    def __init__(self, config: Dict[str, Any]):
        self._validateConfig(config)
        self._config: Dict[str, Any] = config

        meshName = self._config["geometry"]["meshName"]
        self._msh = Mesh(meshName)

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

        self._oilVals: List[float] = self.getOilVals()

        self.shipPos = None
        if "geometry" in self.config and isinstance(
            self.config["geometry"].get("ship", None), list
        ):
            shipCfg = self.config["geometry"].get("ship", None)
            if shipCfg is not None and len(shipCfg) >= 2:
                self.shipPos = [float(shipCfg[0]), float(shipCfg[1])]

        self.shipSink = {}
        if self.shipPos is not None:
            try:
                from src.oil_sink import compute_ship_sink

                self.shipSink = compute_ship_sink(
                    self._msh,
                    ship_pos=self.shipPos,
                    radius=0.1,
                    sigma=1.0,
                    strength=100.0,
                    mode="uniform",
                )
            except Exception:
                self.shipSink = {}

        # Optional oil source configuration (injection point)
        self.sourcePos = None
        if "geometry" in self.config and isinstance(
            self.config["geometry"].get("source", None), list
        ):
            sourceCfg = self.config["geometry"].get("source", None)
            if sourceCfg is not None and len(sourceCfg) >= 2:
                self.sourcePos = [float(sourceCfg[0]), float(sourceCfg[1])]

        # Precompute source coefficients if configured
        self.sourceSink = {}
        if self.sourcePos is not None:
            try:
                from src.oil_sink import compute_source

                self.sourceSink = compute_source(
                    self._msh,
                    source_pos=self.sourcePos,
                    radius=0.1,
                    sigma=1.0,
                    strength=10.0,
                    mode="uniform",
                )
            except Exception:
                self.sourceSink = {}

    @staticmethod
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
        # den leser gjenom alle cellene hvert step. kan dette opimatiseres? TODO
        return [cell.oil for cell in self._msh.cells if cell.type == "triangle"]

    def _computeFlux(
        self, i: int, cell: Any, ngb: int
    ) -> float:  # TODO: andre formler fra config
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

        # Apply accumulated updates
        for cell in triangle_cells:
            deltas = list(getattr(cell, "newOil", []))
            if deltas:
                cell.oil = float(cell.oil) + float(sum(deltas))
                cell.newOil.clear()
            else:
                logger.debug(
                    "Cell %s had no pending oil updates", getattr(cell, "id", "?")
                )

    # snake_case compatibility wrapper
    def update_oil(self, *args, **kwargs):
        return self.updateOil(*args, **kwargs)

    def run_sim(
        self,
        runNumber: Optional[int] = None,
        createVideo: Optional[bool] = None,
        **kwargs,
    ) -> Optional[str]:

        # allow createVideo to be passed, otherwise fall back to config
        if createVideo is None:
            createVideo: bool = self._config.get("video", {}).get("createVideo", False)
        else:
            createVideo = bool(createVideo)

        videoFps: int = int(self._config.get("video", {}).get("videoFPS", 30))

        totalSteps = self._nSteps

        # initial plotting
        self._visualizer.plotting(
            self.oilVals,
            filepath=str(self._imageDir),
            run=runNumber,
            step=0,
            config=self._config,
            **kwargs,
        )

        with tqdm(
            total=totalSteps,
            desc="Simulating oil dispersion",
            unit="step",
            colour="cyan",
            ncols=100,
            ascii="-#",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        ) as pbar:
            for stepIdx in range(1, totalSteps + 1):
                self.updateOil()
                self._currentTime = self._timeStart + stepIdx * self._dt
                self._oilVals = self.getOilVals()

                if stepIdx % self._writeFrequency == 0:
                    self._visualizer.plotting(
                        self.oilVals,
                        filepath=str(self._imageDir),
                        run=runNumber,
                        step=stepIdx,
                        **kwargs,
                    )
                pbar.update(1)

        videoPath: Optional[str] = None
        if createVideo and runNumber is not None:
            logger.info("Creating video for run %s", runNumber)

            videoCreator = VideoCreator(imageDir=self._imageDir, fps=videoFps)

            if hasattr(videoCreator, "createVideo_from_run"):
                videoPath = videoCreator.createVideo_from_run(runNumber)
            else:
                videoPath = videoCreator.createVideoFromRun(runNumber)
            logger.info("Video created successfully: %s", videoPath)

        return videoPath
