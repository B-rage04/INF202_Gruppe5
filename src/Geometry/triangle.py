"""Triangle cell implementation.
"""

import numpy as np

from src.Geometry.cell import Cell


class Triangle(Cell):
    """Concrete 'Cell' for triangular elements.

    Methods:
        findArea(): returns the scalar area of the triangle.
    """

    def __init__(self, msh, cell_points, cell_id, config=None):
        super().__init__(msh, cell_points, cell_id, config)
        self.type = "triangle"

    def findArea(self):
        """Compute triangle area.

        Returns:
            float: positive area of the triangle.
        """
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area
