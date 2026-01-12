from src.Cells.line import Line
from src.Cells.quad import Quad
from src.Cells.triangle import Triangle


def CellFactory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    cellList = []

    # msh.cells is a list of CellBlock objects
    IDx = 0
    for _, cellBlock in enumerate(msh.cells):
        cellType = cellBlock.type
        cells_array = cellBlock.data
        if cellType == "triangle":
            for cellPoints in cells_array:
                cellList.append(Triangle(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "quad" or cellType == "quadrilateral":
            for cellPoints in cells_array:
                cellList.append(Quad(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "line":
            for cellPoints in cells_array:
                cellList.append(Line(msh, cellPoints, IDx))
                IDx += 1
    # find neighbors
    for cell in cellList:
        cell.find_ngb(cellList)
        cell.find_scaled_normales(cellList)

    return cellList
