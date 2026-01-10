import numpy as np
from tqdm import tqdm

from src.LoadTOML import LoadTOML
from src.video import VideoCreator
from src.visualize import Visualizer


class Simulation:
    def __init__(self, msh, config):
        self.config = LoadTOML.load_toml_file(config)
        self.cells = msh.cells
        self.triangle_cells = [cell for cell in self.cells if cell.type == "triangle"]
        self.oil_vals = [cell.oil for cell in self.triangle_cells]
        self.vs = Visualizer(msh)
        self.ct = 0
        self.time_start = 0
        self.time_end = self.config["settings"]["tEnd"]
        self.nSteps = self.config["settings"]["nSteps"]
        self.writeFrequency = self.config["IO"]["writeFrequency"]
        self.dt = (self.time_end - self.time_start) / self.nSteps

    def update_oil(self):
        for cell in self.cells:
            if cell.type != "triangle":
                continue
            for i, ngb in enumerate(cell.ngb):
                if self.cells[ngb].type != "triangle":
                    continue
                cell.new_oil.append(-(self.dt / cell.area) * self.flux(i, cell, ngb))

        for cell in self.cells:
            if cell.new_oil is not None:
                cell.oil += sum(cell.new_oil)
                cell.new_oil.clear()
            else:
                print(f"Warning: Cell, {cell.id}, was None")  # TODO: try except
                cell.oil = cell.oil

    def flux(self, i, cell, ngb):
        flow_avg = (cell.flow + self.cells[ngb].flow) / 2
        if np.dot(flow_avg, cell.scaled_normal[i]) > 0:
            return cell.oil * np.dot(flow_avg, cell.scaled_normal[i])
        else:
            return self.cells[ngb].oil * np.dot(flow_avg, cell.scaled_normal[i])

    def run_sim(self, run_number=None, create_video=True, video_fps=60, **kwargs):
        step_idx = 0
        self.vs.plotting(self.oil_vals, run=run_number, step=step_idx, **kwargs)

        with tqdm(total=self.nSteps, desc="Simulation progress", unit="steps") as pbar:
            while self.ct <= self.time_end:
                self.update_oil()
                self.ct += self.dt
                step_idx += 1
                self.oil_vals = [cell.oil for cell in self.triangle_cells]

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
