from tqdm import tqdm
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
    for _, cellBlock in tqdm(enumerate(msh.cells), desc="Processing cell blocks", total=len(msh.cells)):
        cellType = cellBlock.type
        cellsArray = cellBlock.data
        if cellType == "triangle":
            for cellPoints in tqdm(cellsArray, desc=f"Creating {cellType} cells", leave=False):
                cellList.append(Triangle(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "quad" or cellType == "quadrilateral":
            for cellPoints in tqdm(cellsArray, desc=f"Creating {cellType} cells", leave=False):
                cellList.append(Quad(msh, cellPoints, IDx))
                IDx += 1
        elif cellType == "line":
            for cellPoints in tqdm(cellsArray, desc=f"Creating {cellType} cells", leave=False):
                cellList.append(Line(msh, cellPoints, IDx))
                IDx += 1
    # find neighbors
    for cell in tqdm(cellList, desc="Finding cell neighbors", unit="cells"):
        cell.findNGB(cellList)
        cell.findScaledNormales(cellList)

    return cellList
