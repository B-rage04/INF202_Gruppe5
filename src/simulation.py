from src.Cells.cell import Cell
from src.visualize import Visualizer
 

class Simulation:
    def __init__(self, msh):
        self.cells = msh.cells
        self.triangle_cells = [cell for cell in self.cells if cell.type == "triangle"]
        self.oil_vals = [cell.oil for cell in self.triangle_cells]
        self.vs = Visualizer(msh)
        self.time = 0

    def run_sim(self):
        self.vs.plotting(self.oil_vals)
