from src.Cells.line import Line
from src.Cells.triangle import Triangle
from src.Cells.vertex import Vertex


class CellFactory:
    def __init__(self, msh):
        self.msh = msh
        self.cellTypes = {"triangle": Triangle, "line": Line, "vertex": Vertex}
        self.cellList = []

    def register(self, key, ctype):
        if key not in self.cell_types:
            self.cell_types[key] = ctype

    def __call__(self):
        IDx = 0
        for cellblock in self.msh.cells:
            cellType = cellblock.type
            for cell in cellblock.data:
                self.cellList.append(self.cellTypes[cellType](self.msh, cell, IDx))
                IDx += 1
        for cell in self.cellList:
            cell.findNGB(self.cellList)

        
        for cell in self.cellList:
            cell.findScaledNormales(self.cellList)

        return self.cellList
