from tqdm import tqdm
from src.Cells.line import Line
from src.Cells.triangle import Triangle
from src.Cells.vertex import Vertex


class CellFactory:
    def __init__(self, msh):
        self.msh = msh
        self.cellTypes = {"triangle": Triangle, "line": Line, "vertex": Vertex}
        self.cellList = []

    # msh.cells is a list of CellBlock objects
    IDx = 0
    for _, cellBlock in tqdm(
        enumerate(msh.cells),
        desc="Processing mesh geometry",
        total=len(msh.cells),
        unit="block",
        colour="yellow",
        ncols=100,
        ascii="-#",
    ):
        cellType = cellBlock.type
        cellsArray = cellBlock.data
        if cellType == "triangle":
            for cellPoints in tqdm(
                cellsArray,
                desc=f"Creating {cellType} cells",
                leave=False,
                ascii="-#",
            ):
                cellList.append(Triangle(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "quad" or cellType == "quadrilateral":
            for cellPoints in tqdm(
                cellsArray,
                desc=f"Creating {cellType} cells",
                leave=False,
                ascii="-#",
            ):
                cellList.append(Quad(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "line":
            for cellPoints in tqdm(
                cellsArray,
                desc=f"Creating {cellType} cells",
                leave=False,
                ascii="-#",
            ):
                cellList.append(Line(msh, cellPoints, IDx))
                IDx += 1
    # find neighbors
    for cell in tqdm(
        cellList,
        desc="Computing cell topology",
        unit="cell",
        colour="green",
        ncols=100,
        ascii="-#",
    ):
        cell.findNGB(cellList)
        cell.findScaledNormales(cellList)
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
