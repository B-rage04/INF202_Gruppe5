"""Factory for building 'Cell' objects from mesh blocks.

The 'CellFactory' maps mesh cell blocks (e.g. triangles, lines, vertices)
to concrete 'Cell' subclasses and constructs 'Cell' instances with
incrementing IDs. It accepts a 'Config' instance
"""

import time

from tqdm import tqdm

from src.Geometry.line import Line
from src.Geometry.triangle import Triangle
from src.Geometry.vertex import Vertex


class CellFactory:
    def __init__(self, msh, config=None):
        # Accept plain dict or Config instance for backwards compatibility
        from src.IO.config import Config as _Config

        # If user provided a plain dict, construct a Config instance
        if isinstance(config, dict):
            config = _Config.from_dict(config)

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
        """Return the validated 'Config' used by the factory.

        Returns the 'Config' instance (or None).
        """

        return self._config


    def __call__(self):
        """Build and return a list of 'Cell' objects for the mesh.

        The factory iterates over mesh cell blocks, initss the
        right 'Cell' subclass for each cell, assigns a sequential
        integer ID, and then calls '_update_geometry' on each cell so
        derived properties (midpoint, area, neighbors, normals) are
        precomputed.

        Returns:
            list: list of constructed 'Cell' instances.
        """

        IDx = 0
        for cellblock in self.msh.cells:
            cellType = cellblock.type
            cellCls = self.cellTypes.get(cellType)
            if cellCls is None:
                raise ValueError(f"Unsupported cell type: {cellType}")

            for cell in cellblock.data:
                # Create the concrete cell instance
                self.cellList.append(cellCls(self.msh, cell, IDx, self._config))
                IDx += 1

       
        # code can rely on caches being populated
        for cell in self.cellList:
            cell._update_geometry(cellList=self.cellList)

        return self.cellList
