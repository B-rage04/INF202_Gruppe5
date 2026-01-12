from src.Cells.line import Line
from src.Cells.triangle import Triangle


class CellFactory:
    def __init__(self, msh):
        self.msh = msh
        self.cellTypes = {"triangle": Triangle, "line": Line}
        self.cellList = []

    def register(self, key, ctype):
        if key not in self.cell_types:
            self.cell_types[key] = ctype


    def __call__(self):
  
        for cellblock in self.msh.cells[8:12]:
            cellType = cellblock.type
            for idx, cell in enumerate(cellblock.data):
                self.cellList.append(self.cellTypes[cellType](self.msh,cell,idx)) 
  
        for cell in self.cellList:
            cell.findNGB(self.cellList)
            cell.findScaledNormales(self.cellList)

        return self.cellList
