from src.Geometry.cell import Cell


class Line(Cell):
    """
    Line class that inherits from cell class
    """
    def __init__(self, msh, cellPoints, cell_id, config=None):
        """Initializes line object with points, cell_id, configuration
        
        :param cellPoints: list of points belonging to cell
        :param cell_id: cell id
        :param config: default 0, simulation config
        """
        super().__init__(msh, cellPoints, cell_id, config)
        self.type = "line"

    def findArea(self):
        """Line should always return an area of 0"""
        return None
