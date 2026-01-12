import numpy as np

from src.Cells.cell import Cell


class Quad(Cell):  # TODO:see mesh.py
    def __init__(self, msh, cellPoints, cellId):
        super().__init__(msh, cellPoints, cellId)
        self.type = "quad"

    def findArea(self):
        # polygon area (shoelace) on the xy components
        pts = np.array(self.cords)[:, :2]
        x = pts[:, 0]
        y = pts[:, 1]
        # close polygon
        x2 = np.roll(x, -1)
        y2 = np.roll(y, -1)
        return 0.5 * abs(np.sum(x * y2 - x2 * y))
