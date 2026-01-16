"""Vertex cell type single point cell.

'Vertex' represents a 0-dimensional cell. It does
not enclose area, so 'findArea' returns 'None'.
"""

from src.Geometry.cell import Cell


class Vertex(Cell):
    """0D cell representing a single vertex in the mesh."""

    def __init__(self, msh, cell_points, cell_id, config=None):
        super().__init__(msh, cell_points, cell_id, config)
        self.type = "vertex"

    def findArea(self):
        """Return None: vertex has no area.

        Returns:
            None
        """
        return None
