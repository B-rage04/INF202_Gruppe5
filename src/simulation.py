from src.Cells.cell import Cell
from src.visualize import Visualizer


class Simulation:
    def __init__(self, msh):
        self.cells = [Cell(msh, i) for i in range(len(msh.triangles))]
        self.oil_vals = [cell.oil for cell in self.cells]
        self.vs = Visualizer(msh)
        self.time = 0

    def run_sim(self):
        self.vs.plotting(self.oil_vals)
