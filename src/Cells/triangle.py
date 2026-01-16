import numpy as np

from src.Cells.cell import Cell


class Triangle(Cell):
    """
    Cell of type "triangle"
    """

    def __init__(self, msh, cell_points, cell_id, config=None):
        super().__init__(msh, cell_points, cell_id, config)
        self.type = "triangle"

    def findArea(self):
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area
