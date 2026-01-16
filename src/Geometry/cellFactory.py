import time

from tqdm import tqdm

from src.Geometry.line import Line
from src.Geometry.triangle import Triangle
from src.Geometry.vertex import Vertex


class CellFactory:
    """
    A factory class for creating and initializing cells from a mesh

    This class parses mesh data and assigns corresponding cell types (vertex, line, triangle)
    and handles initial calculations of neighbors and normals

    Attributes:
        CellList (List): List of cell objects
        msh (mesh): mesh object
    """
    def __init__(self, msh, config=None):
        """
        Initializes Cellfactory using a mesh and configuration

        :param msh: meshobject (from Meshio)
        :param config: dict containing infromation about the mesh and simulation overall
        """
        # Accept plain dict or Config instance for backwards compatibility
        from src.IO.config import Config as _Config

        if isinstance(config, dict):
            config = _Config.from_dict(config)
        elif not isinstance(config, _Config) and config is not None:
            raise TypeError("config must be a Config instance or dict")

        self._config = config

        # store mesh and initialize type registry + cell list
        self.msh = msh
        self.cellTypes = {
            "triangle": Triangle,
            "line": Line,
            "vertex": Vertex,
        }
        self.cellList = []

    @property
    def config(self):
        """ Returns the configuration dictionary from the factory"""
        return self._config


    def __call__(self):
        """
        Processes the mesh with the provided configuration to initialize all cells

        1. Creates cells based on mesh \n
        2. runs neghborcheck for every cell
        3. runs findScaledNormals for every cell

        Returns: a list of all cell objects with their initialized values
        """

        IDx = 0
        for cellblock in self.msh.cells:
            cellType = cellblock.type
            cellCls = self.cellTypes.get(cellType)
            if cellCls is None:
                raise ValueError(f"Unsupported cell type: {cellType}")

            for cell in cellblock.data:
                self.cellList.append(cellCls(self.msh, cell, IDx, self._config))
                IDx += 1

        for cell in self.cellList:
            cell.findNGB(self.cellList)
            cell.findScaledNormales(self.cellList)

        return self.cellList
