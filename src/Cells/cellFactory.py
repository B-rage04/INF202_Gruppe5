from tqdm import tqdm

from src.Cells.line import Line
from src.Cells.triangle import Triangle
from src.Cells.vertex import Vertex


class CellFactory:
    def __init__(self, msh):
        self.msh = msh
        self.cellTypes = {
            "triangle": Triangle,
            "line": Line,
            "vertex": Vertex,
        }
        self.cellList = []
    
    def register(self, key, ctype):
        if key not in self.cellTypes:
            self.cellTypes[key] = ctype

    def __call__(self):
        IDx = 0
        for cellblock in tqdm(
            self.msh.cells,
            desc="Processing mesh geometry",
            unit="block",
            colour="yellow",
            ncols=100,
            ascii="-#",
        ):
            cellType = cellblock.type
            cellCls = self.cellTypes.get(cellType)
            if cellCls is None:
                raise ValueError(f"Unsupported cell type: {cellType}")

            for cell in tqdm(
                cellblock.data,
                desc=f"Creating {cellType} cells",
                leave=False,
                ascii="-#",
            ):
                self.cellList.append(cellCls(self.msh, cell, IDx))
                IDx += 1

        for cell in tqdm(
            self.cellList,
            desc="Computing cell NGB",
            unit="cell",
            colour="green",
            ncols=100,
            ascii="-#",
        ):
            cell.findNGB(self.cellList)

        for cell in tqdm(
            self.cellList,
            desc="Computing cell Normals",
            unit="cell",
            colour="green",
            ncols=100,
            ascii="-#",
        ):
            cell.findScaledNormales(self.cellList)

        return self.cellList
