from src.Cells.cell import Cell


class Line(Cell):
    def __init__(self, msh, cellPoints, cell_id):
        super().__init__(msh, cellPoints, cell_id)
        self.type = "line"

    def findArea(self):  # TODO: test this
        return None

    def findScaledNormales(self, allCells=None):  # TODO: test this
        self._scaledNormal = []
        return self._scaledNormal
