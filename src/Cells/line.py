from src.Cells.cell import Cell


class Line(Cell):
    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "line"

    def find_area(self):
        return None

    def findScaledNormales(self, all_cells=None):
        self._scaledNormal = []
        return self._scaledNormal
