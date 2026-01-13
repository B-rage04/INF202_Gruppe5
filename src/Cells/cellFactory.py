from src.Cells.line import Line
from src.Cells.quad import Quad
from src.Cells.triangle import Triangle


def CellFactory(msh):  # TODO: test this
    """
    Creates cells with data from the mesh and returns as a list
    """
    cellList = []

    # msh.cells is a list of CellBlock objects
    IDx = 0
    for _, cellBlock in enumerate(msh.cells):
        cellType = cellBlock.type
        cellsArray = cellBlock.data
        if cellType == "triangle":
            for cellPoints in cellsArray:
                cellList.append(Triangle(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "quad" or cellType == "quadrilateral":
            for cellPoints in cellsArray:
                cellList.append(Quad(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "line":
            for cellPoints in cellsArray:
                cellList.append(Line(msh, cellPoints, IDx))
                IDx += 1
    # find neighbors
    for cell in cellList:
        cell.findNGB(cellList)
        cell.findScaledNormales(cellList)

    return cellList
