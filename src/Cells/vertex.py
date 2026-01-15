from src.Cells.cell import Cell


class Vertex(Cell):
    def __init__(self, msh, cell_points, cell_id, config):
        super().__init__(msh, cell_points, cell_id, config)
        self.type = "vertex"

    def findArea(self):
        return None
