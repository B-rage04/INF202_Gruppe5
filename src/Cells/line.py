from src.Cells.cell import Cell


class Line(Cell):
    def __init__(self, msh, cellPoints, cell_id, config=None):
        super().__init__(msh, cellPoints, cell_id, config)
        self.type = "line"

    def findArea(self):
        return None
