from src.Cells.cell import Cell


class Vertex(Cell):
    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "vertex"

    def findArea(self):
        return None
