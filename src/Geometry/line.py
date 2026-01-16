"""Line cell type — degenerate 1D cell used for boundary/edge data.

The 'Line' cell represents an edge in the mesh. It inherits from
'Cell' but does not define a planar area; 'findArea' returns 'None'.
"""

from src.Geometry.cell import Cell


class Line(Cell):
    """Cell representing a 1D line/edge in the mesh.

    Notes:
    - 'findArea' returns 'None' because a line does not enclose area.
    """

    def __init__(self, msh, cellPoints, cell_id, config=None):
        super().__init__(msh, cellPoints, cell_id, config)
        self.type = "line"

    def findArea(self):
        """Return None: line cells have no area.

        Returns:
            None
        """
        return None
