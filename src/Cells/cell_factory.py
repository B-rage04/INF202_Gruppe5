from tqdm import tqdm

from src.Cells.line import Line
from src.Cells.triangle import Triangle


class Cell_factory:
    def __init__(self):
        self.cell_types = {"triangle": Triangle, "line": Line}

    def register(self, key, ctype):
        if key not in self.cell_types:
            self.cell_types[key] = ctype

    def __call__(self, cell):
        key = cell.type
        return self.cell_types


def Cell_factory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    cell_list = []

    # msh.cells is a list of CellBlock objects
    IDx = 0
    for _, cell_block in tqdm(
        enumerate(msh.cells),
        desc="Processing mesh geometry",
        total=len(msh.cells),
        unit="block",
        colour="yellow",
        ncols=100,
        ascii="-#",
    ):
        cell_type = cell_block.type
        cells_array = cell_block.data
        if cell_type == "triangle":
            for cell_points in tqdm(
                cells_array,
                desc=f"Creating {cell_type} cells",
                leave=False,
                ascii="-#",
            ):
                cell_list.append(Triangle(msh, cell_points, IDx))
                IDx += 1
        elif cell_type == "quad" or cell_type == "quadrilateral":
            for cell_points in tqdm(
                cells_array,
                desc=f"Creating {cell_type} cells",
                leave=False,
                ascii="-#",
            ):
                cell_list.append(Quad(msh, cell_points, IDx))
                IDx += 1
        elif cell_type == "line":
            for cell_points in tqdm(
                cells_array,
                desc=f"Creating {cell_type} cells",
                leave=False,
                ascii="-#",
            ):
                cell_list.append(Line(msh, cell_points, IDx))
                IDx += 1
    # find neighbors
    for cell in tqdm(
        cell_list,
        desc="Computing cell topology",
        unit="cell",
        colour="green",
        ncols=100,
        ascii="-#",
    ):
        cell.find_ngb(cell_list)
        cell.find_scaled_normales(cell_list)

    return cell_list
