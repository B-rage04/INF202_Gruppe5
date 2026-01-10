from src.Cells.line import Line
from src.Cells.quad import Quad
from src.Cells.triangle import Triangle


def Cell_factory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    cell_list = []

    # msh.cells is a list of CellBlock objects
    IDx = 0
    for _, cell_block in enumerate(msh.cells):
        cell_type = cell_block.type
        cells_array = cell_block.data
        if cell_type == "triangle":
            for cell_points in cells_array:
                cell_list.append(Triangle(msh, cell_points, IDx))
                IDx += 1
        elif cell_type == "quad" or cell_type == "quadrilateral":
            for cell_points in cells_array:
                cell_list.append(Quad(msh, cell_points, IDx))
                IDx += 1
        elif cell_type == "line":
            for cell_points in cells_array:
                cell_list.append(Line(msh, cell_points, IDx))
                IDx += 1
    # find neighbors
    for cell in cell_list:
        cell.find_ngb(cell_list)
        cell.find_scaled_normales(cell_list)

    return cell_list
