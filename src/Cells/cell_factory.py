from src.Cells.line import Line
from src.Cells.triangle import Triangle

def Cell_factory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    cell_list = []
    
    # msh.cells is a list of CellBlock objects
    for cell_block in msh.cells:
        cell_type = cell_block.type
        cells_array = cell_block.data
        if cell_type == "triangle":
            for idx, cell_points in enumerate(cells_array):
                cell_list.append(Triangle(msh, cell_points, idx))
        elif cell_type == "line":
            for idx, cell_points in enumerate(cells_array):
                cell_list.append(Line(msh, cell_points, idx))
    
    # find neighbors
    for cell in cell_list:
        cell.find_ngb(cell_list)
    
    return cell_list
