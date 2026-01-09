import numpy as np

from src.LoadTOML import LoadTOML
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
        self.dt = (self.time_end - self.time_start) / self.nSteps

    def update_oil(self):
        for cell in self.cells:
            if cell.type != "triangle":
                continue    
            for i, ngb in enumerate(cell.ngb):
                if self.cells[ngb].type != "triangle":
                    continue
                cell.new_oil = cell.oil - (self.dt / cell.area) * self.flux(i, cell, ngb)
        
        for cell in self.cells:
            if cell.new_oil is not None:
                cell.oil = cell.new_oil
            else:
                print(f"Warning: Cell, {cell.id}, was None") #TODO: try except
                cell.oil = cell.oil
 


    def flux(self, i, cell, ngb):
        flow_avg = (cell.flow + self.cells[ngb].flow) / 2
        if np.dot(flow_avg, cell.scaled_normal[i]) > 0:
            return cell.oil * np.dot(flow_avg, cell.scaled_normal[i])
        else:
            print(self.cells[ngb].oil)
            print(self.cells[ngb])
            return self.cells[ngb].oil * np.dot(flow_avg, cell.scaled_normal[i])
        

    def run_sim(self):
        self.vs.plotting(self.oil_vals)
        c = 0
        while self.ct <= self.time_end:
            self.update_oil()
            if c < 15:
                print(f"Oljeverdi: {self.cells[673].oil}, Newoilverdi: {self.cells[673].new_oil}")
                c+=1
            self.ct += self.dt
        self.vs.plotting(self.oil_vals)