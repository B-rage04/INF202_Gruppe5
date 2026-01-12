from typing import Any, Dict, List, Optional
import logging

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

        mesh_name = self._config["geometry"]["meshName"]
        self._msh = Mesh(mesh_name)

        self._visualizer = Visualizer(self._msh)

        self._timeStart: float = float(self._config["settings"]["tStart"])
        self._timeEnd: float = float(self._config["settings"]["tEnd"])
        self._nSteps: int = int(self._config["settings"]["nSteps"])
        self._writeFrequency: int = int(self._config["IO"]["writeFrequency"])

        self._dt: float = (self._timeEnd - self._timeStart) / max(1, self._nSteps)
        self._currentTime: float = float(self._timeStart)

        self._oilVals: List[float] = self.getOilVals()


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

    #getters/setters
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
            raise TypeError("current_time must be numeric")
        self._currentTime = float(value)

    @property
    def oilVals(self) -> List[float]:
        # return a copy to avoid accidental external mutation
        return list(self._oilVals)


    def getOilVals(self) -> List[float]: #TODO: ikke barre tiangle
        return [cell.oil for cell in self._msh.cells if cell.type == "triangle"]

    def _computeFlux(self, i: int, cell: Any, ngb: int) -> float: #TODO: andre formler fra config
        neighbor = self._msh.cells[ngb]
        flowAvg = (cell.flow + neighbor.flow) / 2.0
        dot = float(np.dot(flowAvg, cell.scaled_normal[i]))
        source_oil = cell.oil if dot > 0 else neighbor.oil
        return source_oil * dot

    def updateOil(self) -> None: #TODO: ikke barre tiangle
        for cell in self._msh.cells:
            if cell.type != "triangle":
                continue
            # ensure new_oil exists and is a list #TODO: lag en unit test får dette
            if cell.newOil is None:
                cell.newOil = []
            for i, ngb in enumerate(cell.ngb):
                if self._msh.cells[ngb].type != "triangle":
                    continue
                delta = -(self._dt / cell.area) * self._computeFlux(i, cell, ngb)
                cell.newOil.append(delta)

        for cell in self._msh.cells:
            if getattr(cell, "newOil", None):
                cell.oil += sum(cell.newOil)
                cell.newOil.clear()
            else:
                logger.debug("Cell %s had no pending oil updates", getattr(cell, "id", "?"))

    def run_sim(self, runNumber: Optional[int] = None, **kwargs) -> Optional[str]:

        create_video: bool = self._config.get("video", {}).get("createVideo", False)
        videoFps: int = int(self._config.get("video", {}).get("videoFPS", 30))

        total_steps = self._nSteps

        self._visualizer.plotting(self.oilVals, run=runNumber, step=0, **kwargs)

        with tqdm(total=total_steps, desc="Simulation progress", unit="steps") as pbar:
            for stepIdx in range(1, total_steps + 1):
                self.updateOil()
                self._currentTime = self._timeStart + stepIdx * self._dt
                self._oilVals = self.getOilVals()

                if stepIdx % self._writeFrequency == 0:
                    self._visualizer.plotting(self.oilVals, run=runNumber, step=stepIdx, **kwargs)
                pbar.update(1)

        videoPath: Optional[str] = None
        if create_video and runNumber is not None:
            logger.info("Creating video for run %s", runNumber)
            videoCreator = VideoCreator(fps=videoFps)
            videoPath = videoCreator.create_video_from_run(runNumber)
            logger.info("Video created successfully: %s", videoPath)

        return videoPath

