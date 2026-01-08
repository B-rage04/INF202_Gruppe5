from .cell import Cell

class Line(Cell):
    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "line"

    def find_area(self):
        return None
