import numpy as np

from src.Geometry.cell import Cell


class Triangle(Cell):
    """
    Class for triangles that inherits from cell class
    """

    def __init__(self, msh, cell_points, cell_id, config=None):
        """
        Initializes triangle cell

        :param msh: meshio.Mesh object
        :param cell_points: list of cells belonging to this cell
        :param cekk_id: id belonging to this cell
        :param config: configuration dict for simulation
        """
        super().__init__(msh, cell_points, cell_id, config)
        self.type = "triangle"

    def findArea(self):
        """"
        Returns area of triangle using the general formula 0.5*|(x1 - x3)(y2 - y1) - (x1 - x2)(y3 - y1)|
        """
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area
