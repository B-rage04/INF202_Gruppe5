from src.Cells.cell import Cell
from src.visualize import Visualizer
from src.LoadTOML import LoadTOML

class Simulation:
    def __init__(self, msh, config):
        self.config = LoadTOML.load_toml_file(config)
        self.cells = msh.cells
        self.triangle_cells = [cell for cell in self.cells if cell.type == "triangle"]
        self.oil_vals = [cell.oil for cell in self.triangle_cells]
        self.vs = Visualizer(msh)
        self.time_start = 0
        self.time_end = self.config["settings"]["tEnd"]
        self.nSteps = self.config["settings"]["nSteps"]
        self.dt = (self.time_end - self.time_start)/self.nSteps
    def run_sim(msh, self):

        
        for cell in self.cells:
            if cell.type == "triangle":
                cell.update_oil(msh ,self.dt)


        self.vs.plotting(self.oil_vals)
