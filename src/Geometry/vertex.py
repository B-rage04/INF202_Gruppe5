from src.Geometry.cell import Cell


class Vertex(Cell):
    """Class for vertex class cells"""
    def __init__(self, msh, cell_points, cell_id, config=None):
        """
        Docstring for __init__
        
        :param msh: meshio.Mesh object
        :param cell_points: list of points belonigng to cell
        :param cell_id: id of cell
        :param config: config for simulation as dict
        """

        super().__init__(msh, cell_points, cell_id, config)
        self.type = "vertex"

    def findArea(self):
        """Returns 0 always since a single vertex/point does not have any area"""
        return None
