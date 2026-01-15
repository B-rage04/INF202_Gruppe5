import time

from tqdm import tqdm

from src.Cells.line import Line
from src.Cells.triangle import Triangle
from src.Cells.vertex import Vertex

from src.config import Config


class CellFactory:
    def __init__(self, msh, config:Config=None):
        # Accept only Config instance or None for new API
        from src.config import Config

        # validate config: require Config instance
        if config is not isinstance(config, Config):
            pass
            #raise TypeError("config must be a Config instance")
        self._config = config

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
        start_time = time.perf_counter()
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
                self.cellList.append(cellCls(self.msh, cell, IDx, self._config))
                IDx += 1
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Processing mesh geometry completed in {elapsed_ms:.2f} ms")

        start_time = time.perf_counter()
        for cell in tqdm(
            self.cellList,
            desc="Computing cell NGB",
            unit="cell",
            colour="green",
            ncols=100,
            ascii="-#",
        ):
            cell.findNGB(self.cellList)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Computing cell NGB completed in {elapsed_ms:.2f} ms")

        start_time = time.perf_counter()
        for cell in tqdm(
            self.cellList,
            desc="Computing cell Normals",
            unit="cell",
            colour="green",
            ncols=100,
            ascii="-#",
        ):
            cell.findScaledNormales(self.cellList)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Computing cell Normals completed in {elapsed_ms:.2f} ms")

        return self.cellList
