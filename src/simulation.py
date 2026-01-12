import numpy as np
from tqdm import tqdm

from src.mesh import Mesh
from src.video import VideoCreator
from src.visualize import Visualizer
from src.oil_sink import compute_ship_sink, compute_source


class Simulation:
    def __init__(self, config):
        self.config = config
        self.msh = Mesh(config["geometry"]["meshName"])

        self.oil_vals = self.getOilVals()
        self.vs = Visualizer(self.msh)
        self.CurrentStep = 0
        self.time_start = self.config["settings"]["tStart"]
        self.time_end = self.config["settings"]["tEnd"]
        self.nSteps = self.config["settings"]["nSteps"]
        self.writeFrequency = self.config["IO"]["writeFrequency"]
        self.dt = self.time_end / self.nSteps

        # Optional oil collection ship sink configuration
        self.ship_pos = None
        if "geometry" in self.config and isinstance(self.config["geometry"].get("ship", None), list):
            ship_cfg = self.config["geometry"].get("ship", None)
            if ship_cfg is not None and len(ship_cfg) >= 2:
                self.ship_pos = [float(ship_cfg[0]), float(ship_cfg[1])]

        # Precompute sink coefficients for ship if configured
        self.ship_sink = {}
        if self.ship_pos is not None:
            self.ship_sink = compute_ship_sink(
                self.msh,
                ship_pos=self.ship_pos,
                radius=0.1,
                sigma=1.0,
                strength=100.0,
                mode="uniform",
            )

        # Optional oil source configuration (injection point)
        self.source_pos = None
        if "geometry" in self.config and isinstance(self.config["geometry"].get("source", None), list):
            source_cfg = self.config["geometry"].get("source", None)
            if source_cfg is not None and len(source_cfg) >= 2:
                self.source_pos = [float(source_cfg[0]), float(source_cfg[1])]

        # Precompute source coefficients if configured
        self.source_sink = {}
        if self.source_pos is not None:
            self.source_sink = compute_source(
                self.msh,
                source_pos=self.source_pos,
                radius=0.1,
                sigma=1.0,
                strength=10.0,
                mode="uniform",
            )

    def getOilVals(self):
        return [cell.oil for cell in self.msh.cells if cell.type == "triangle"]

    def update_oil(self):
        # Accumulate flux contributions (to reach u^{n+1/2})
        for cell in self.msh.cells:
            if cell.type != "triangle":
                continue
            for i, ngb in enumerate(cell.ngb):
                if self.msh.cells[ngb].type != "triangle":
                    continue
                cell.new_oil.append(-(self.dt / cell.area) * self.flux(i, cell, ngb))

        # Apply half-step update and then sink/source adjustment
        for cell in self.msh.cells:
            if cell.type != "triangle":
                continue

            if cell.new_oil is not None:
                u_half = cell.oil + sum(cell.new_oil)
                cell.new_oil.clear()
            else:
                print(f"Warning: Cell, {cell.id}, was None")  # TODO: try except
                u_half = cell.oil

            # Sinks (ship) and sources per formula:
            # u^{n+1}_i = u^{n+1/2}_i / (1 + dt*S^-_i - dt*S^+_i)
            s_minus = 0.0
            s_plus = 0.0

            if getattr(self, "use_ship_sink", True) and self.ship_sink and cell.id in self.ship_sink:
                s_minus = self.ship_sink[cell.id]

            if getattr(self, "use_sources", True) and self.source_sink and cell.id in self.source_sink:
                s_plus = self.source_sink[cell.id]

            denom = 1.0 + self.dt * s_minus - self.dt * s_plus
            # Prevent division by very small or negative denominators
            if denom <= 1e-12:
                denom = 1e-12

            cell.oil = u_half / denom

    def flux(self, i, cell, ngb):
        flow_avg = (cell.flow + self.msh.cells[ngb].flow) / 2
        if np.dot(flow_avg, cell.scaled_normal[i]) > 0:
            return cell.oil * np.dot(flow_avg, cell.scaled_normal[i])
        else:
            return self.msh.cells[ngb].oil * np.dot(flow_avg, cell.scaled_normal[i])

    def run_sim(self, run_number=None, create_video=True, video_fps=60, use_ship_sink=True, use_sources=True, **kwargs):
        # Allow enabling/disabling ship sink and sources from the run entry point
        self.use_ship_sink = bool(use_ship_sink)
        self.use_sources = bool(use_sources)
        step_idx = 0
        self.vs.plotting(self.oil_vals, run=run_number, step=step_idx, **kwargs)

        with tqdm(total=self.nSteps, desc="Simulation progress", unit="steps") as pbar:
            while self.CurrentStep <= self.time_end:
                self.update_oil()
                self.CurrentStep += self.dt
                step_idx += 1
                self.oil_vals = self.getOilVals()

                if step_idx % self.writeFrequency == 0:  # TODO fix edje cases
                    self.vs.plotting(
                        self.oil_vals, run=run_number, step=step_idx, **kwargs
                    )
                pbar.update(1)

        if create_video and run_number is not None:
            print(f"Creating video for run {run_number}...")
            video_creator = VideoCreator(fps=video_fps)
            video_path = video_creator.create_video_from_run(run_number)
            print(f"Video created successfully: {video_path}")
