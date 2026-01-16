import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from tqdm import tqdm

from src.IO.config import Config
from src.Geometry.mesh import Mesh
from src.Geometry.oil_sink import OilSinkSource
.
from importlib import import_module

try:
    _shim = import_module("src.simulation")
    VideoCreator = getattr(_shim, "VideoCreator", None)
except Exception:
    VideoCreator = None

if VideoCreator is None:
    try:
        from src.IO.video import VideoCreator
    except Exception:
        VideoCreator = None
from src.Simulation.visualize import Visualizer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Simulation:
    """Manage oil-dispersion simulation lifecycle.

    Responsible for initializing configuration and mesh, running the
    time-stepping loop, collecting per-step diagnostics, and producing
    visualization output.

    init args:
        config (Config): Simulation configuration instance.
    """

    def __init__(self, config: Config = None):
        self._config = self._validate_config(config)
        self._msh = self._initialize_mesh()
        self._initialize_visualizer()
        self._initialize_time_parameters()
        self.oilSinks = self._initialize_ship_sink()  # Changed from shipSink
        self.oilSources = self._initialize_oil_sources()  # Changed from sourceSink
        self._initialize_additional_sinks()
        self._log_configuration_summary()

    def updateOil(self, dt):
        """Update oil concentration for all cells
        args:
            dt (float): time step size
        behavior:

        
        """
        # Get source and sink coefficients
        source_coeffs = self.oilSources if hasattr(self, "oilSources") else {}
        sink_coeffs = self.oilSinks if hasattr(self, "oilSinks") else {}

        oil_half = np.zeros(len(self._msh.cells))   # Temporary storage

        # Predictor step
        for cell in self._msh.cells:                                                # for all cells
            if getattr(cell, "type", None) != "triangle":                           # Skip non-triangle cells
                continue
            flux_sum = 0.0
            for i, ngb in enumerate(cell.ngb):                                      # for all neighbors
                neighbor = self._msh.cells[ngb]                                     # get neighbor cell
                if getattr(neighbor, "type", None) != "triangle":                   # Skip non-triangle neighbors   
                    continue
                flux_sum += -(dt / cell.area) * self._computeFlux(i, cell, ngb)     # accumulate fluxes
            oil_half[cell.id] = cell.oil + flux_sum                                 # update oil concentration

        # Corrector step with sources/sinks (spec-compliant)
        for cell in self._msh.cells:                                    # for all cells 
            if getattr(cell, "type", None) != "triangle":               # Skip non-triangle cells
                continue
            S_plus = source_coeffs.get(cell.id, 0.0)                    # Source term
            S_minus = sink_coeffs.get(cell.id, 0.0)                     # Sink term

            # Apply spec: u_new = u_half / (1 + dt*S_minus - dt*S_plus)
            denominator = 1.0 + dt * S_minus - dt * S_plus              # compute source/sink adjustment
            if abs(denominator) > 1e-12:                                # avoid division by zero
                cell.oil = oil_half[cell.id] / denominator              # update oil concentration
            else:
                cell.oil = oil_half[cell.id]                            # fallback to half-step value

    def _computeFlux(
        self, i: int, cell: Any, ngb: int
    ) -> float:  # TODO: other formulas from config
        """Compute flux across edge

        Returns the signed flux contribution used by the predictor step.
        args:
            i (int): index of the neighbor in cell.ngb
            cell (Cell): the current cell
            ngb (int): neighbor cell ID
        returns:
            float: signed flux contribution
        """

        neighbor = self._msh.cells[ngb]                             # get neighbor cell
        flowAvg = (cell.flow + neighbor.flow) / 2.0                 # average flow vector
        scaled_normals = getattr(cell, "scaledNormal", None)        # get scaled normals
        if scaled_normals is None:                                  # check if scaled normals exist
            raise AttributeError("Cell missing scaled normal data")
        dot = float(np.dot(flowAvg, scaled_normals[i]))             #find dot product
        source_oil = cell.oil if dot > 0 else neighbor.oil          # upwind oil value
        return source_oil * dot                                     # return flux contribution    


    def getOilVals(self):
        """Collect per-step oil diagnostics.

        Appends a snapshot of oil values for all triangle cells to
        ''self._oilVals'' and the total oil on fishing cells to
        ''self._fishingOil''.

        behavior:

        """

        # it reads through all cells each step. Can this be optimized? TODO
        self._oilVals.append(
            [cell.oil for cell in self._msh.cells if cell.type == "triangle"]
        )

        self._fishingOil.append(
            sum([cell.oil for cell in self._msh.cells if cell.isFishing])
        )

    def getFishing(self): #TODO: ^^is this a duplicate of _fishingOil?^^
        """Record per-cell fishing flags for diagnostic purposes.

        Appends a list of boolean fishing flags for triangle cells to
        ''self._fish_vals''.
        """

        self._fish_vals.append(
            [cell._isFishing for cell in self._msh.cells if cell.type == "triangle"]
        )

    def run_sim(
        self,
        runNumber: Optional[int] = None,
        **kwargs,
    ) -> Optional[str]:

        """Execute the simulation loop.

        Runs ''self._nSteps'' time steps, collects diagnostics, optionally
        writes images according to ''writeFrequency'', and can create a
        video for the run. Returns the path to the created video or
        ''None'' if no video was produced.
        args:
            runNumber (Optional[int]): run number for output organization
        returns:
            Optional[str]: path to created video or None
        """

        # self.ship = OilSinkSource(self._msh,configuration=None) #TODO implement oil sink source class

        createVideo = False
        if int(self._config.IO.get("writeFrequency", 0)) != 0:      # enable video if writeFrequency > 0
            createVideo = True

        videoFps: int = int(self._config.video.get("videoFPS", 30)) # frames per second for video

        totalSteps = self._nSteps

        start_time = time.perf_counter()                     # start timing
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
            for stepIdx in range(1, totalSteps + 1):                        # time-stepping loop
                self.updateOil(self._dt)                                    # update oil concentrations
                self._currentTime = self._timeStart + stepIdx * self._dt    # update current time
                self.getOilVals()                                           # collect oil diagnostics #TODO can this be optimized?
                self.getFishing()                                           # collect fishing diagnostics #TODO can this be optimized?

                # Always write first image, last image, or at writeFrequency intervals
                should_write = False
                if self._writeFrequency != 0:                       # only if writeFrequency > 0
                    should_write = (
                        stepIdx == 1                                # first step   
                        or stepIdx == totalSteps                    # last step
                        or stepIdx % self._writeFrequency == 0      # at intervals
                    )

                if should_write:                                    # write output image
                    logger.info(
                        f"total Fishing oil at time {self.currentTime}: {self.fishingOil[-1]:.5f}"
                    )
                    logger.info(f"total oil at time {self.currentTime}: {self.oilVals[-1]:.5f}")

                    self._visualizer.plotting( #TODO add Fishing Oil?
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
            # Resolve VideoCreator at runtime so tests can monkeypatch 'src.simulation.VideoCreator'
            from importlib import import_module

            try:                                                # try to get from simulation module first because of monkeypatching in tests
                _shim = import_module("src.simulation")
                vc_cls = getattr(_shim, "VideoCreator", None)
            except Exception:
                vc_cls = None

            if vc_cls is None:                                  # try to import normally
                try:
                    from src.IO.video import VideoCreator as vc_cls
                except Exception:
                    vc_cls = None

            if vc_cls is None:                                 
                raise RuntimeError("No VideoCreator available to create video")

            videoCreator = vc_cls(imageDir=self._imageDir, fps=videoFps)

            if hasattr(videoCreator, "createVideo_from_run"):
                videoPath = videoCreator.createVideo_from_run(runNumber)
            else:
                videoPath = videoCreator.createVideoFromRun(runNumber)

        return videoPath

    # getters/setters (grouped together)
    @property
    def config(self) -> Config:
        """Get the simulation configuration.
        returns:
            Config: simulation configuration
        """
        return self._config

    @property
    def mesh(self) -> Mesh:
        """Get the simulation mesh.
        returns:
            Mesh: simulation mesh
        """
        return self._msh

    @property
    def dt(self) -> float:
        """Get the simulation time step size.
        returns:
            float: time step size
        """
        return self._dt

    @property
    def currentTime(self) -> float:
        """Get or set the current simulation time.
        returns:
            float: current simulation time
        """
        return self._currentTime

    @currentTime.setter
    def currentTime(self, value: float) -> None:
        """Set the current simulation time.
        args:
            value (float): new current time
        behavior:
            Sets the current simulation time to the given value.
        """
        if not isinstance(value, (int, float)):
            raise TypeError("currentTime must be numeric")
        self._currentTime = float(value)

    @property
    def oilVals(self) -> List[float]:
        """Get recorded oil values over time.
        returns:
            List[float]: recorded oil values
        """
        # return a copy to avoid accidental external mutation
        return list(self._oilVals)

    @property
    def fishingOil(self):
        """Get recorded fishing oil values over time.
        returns:
            List[float]: recorded fishing oil values
        """
        # TODO self.getFishing()?
        return self._fishingOil

    
    def _initialize_mesh(self):
        """Initialize mesh from config.
        returns:
            Mesh: initialized mesh
        behavior:
            Loads the mesh specified in the configuration.
        raises:
            RuntimeError: if no Mesh implementation is available
        """
        # Resolve Mesh class at runtime so tests can monkeypatch 'src.simulation.Mesh'
        meshName = self._config.mesh_name()
        from importlib import import_module

        try:
            _shim = import_module("src.simulation")
            mesh_cls = getattr(_shim, "Mesh", None)
        except Exception:
            mesh_cls = None

        if mesh_cls is None:
            try:
                from src.Geometry.mesh import Mesh as mesh_cls
            except Exception:
                mesh_cls = None

        if mesh_cls is None:
            raise RuntimeError("No Mesh implementation available")

        return mesh_cls(meshName, self._config)

    def _initialize_visualizer(self):
        """Initialize visualizer and tracking lists.
        behavior:
            Sets up the visualizer and initializes lists for oil
            and fishing oil tracking."""
        self._visualizer = Visualizer(self._msh)
        self._fishingOil = []
        self._oilVals = []
        self._fish_vals = []
        self._imageDir: Path = Path(self._config.images_dir())

    def _initialize_time_parameters(self):
        """Initialize time-related parameters from config.
        behavior:
            Sets up time start, end, number of steps, write frequency,
            and computes the time step size."""
        self._timeStart: float = float(self._config.settings["tStart"])
        self._timeEnd: float = float(self._config.settings["tEnd"])
        self._nSteps: int = int(self._config.settings["nSteps"])
        self._writeFrequency: int = int(self._config.IO.get("writeFrequency", 0))
        self._dt: float = (self._timeEnd - self._timeStart) / max(1, self._nSteps)
        self._currentTime: float = float(self._timeStart)

    def _initialize_ship_sink(self):
        """Initialize ship sink configuration.
        returns:
            Dict[int, float]: mapping of cell IDs to sink coefficients
        behavior:
            Sets up the ship sink based on configuration.
        raises:
            Warning: if ship sink initialization fails
        """
        shipSink = {}
        ship_cfg = self._config.geometry.get("ship", None)

        if isinstance(ship_cfg, list) and len(ship_cfg) >= 2:
            try:
                ship_pos = [float(ship_cfg[0]), float(ship_cfg[1])]
                from src.Geometry.oil_sink import compute_ship_sink

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
        """Initialize oil sources from config.
        returns:
            Dict[int, float]: mapping of cell IDs to source coefficients
        behavior:
            Sets up oil sources based on configuration.
        raises:
            Warning: if source initialization fails
        """
        sourceSink = {}
        sources_array = self._config.geometry.get("source", [])

        if isinstance(sources_array, list) and sources_array:
            for idx, source_pos in enumerate(sources_array):
                if isinstance(source_pos, list) and len(source_pos) >= 2:
                    try:
                        from src.Geometry.oil_sink import compute_source

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
        """Initialize additional sinks from config.
        behavior:
            Sets up additional oil sinks based on configuration.
        raises:
            Warning: if sink initialization fails
        """
        sinks_array = self._config.geometry.get("sink", [])

        if isinstance(sinks_array, list) and sinks_array:
            for idx, sink_pos in enumerate(sinks_array):
                if isinstance(sink_pos, list) and len(sink_pos) >= 2:
                    try:
                        from src.Geometry.oil_sink import compute_ship_sink

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
        """Log summary of all.
        logger.info("Logging configuration summary...")
        behavior:
            Logs the number of ships, sources, and sinks configured.
        
        """
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
