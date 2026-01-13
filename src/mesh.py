import logging
import os
from typing import Any, List

from src.Cells.cellFactory import CellFactory

logger = logging.getLogger(__name__)


class Mesh:
    def __init__(self, file: str) -> None:
        if not isinstance(file, str):
            raise TypeError("file must be a path string")  # TODO: test this

        if not os.path.exists(file):
            raise FileNotFoundError(f"Mesh file not found: {file}")  # TODO: test this

        self._msh: Any = self._readMesh(file)

        self._points: List[Any] = getattr(
            self._msh, "points", []
        )  # TODO: test try to call
        self._triangles: List[Any] = getattr(self._msh, "cells_dict", {}).get(
            "triangle", []
        )

        self._cellFactory = CellFactory(self._msh)  # TODO: test try to call
        self._cells = self._cellFactory() # TODO: test try to call
    def _readMesh(self, file: str) -> Any:
        try:  # TODO: test this
            import meshio

            msh = meshio.read(file)
            logger.info("Loaded mesh from %s", file)
            return msh
        except Exception as exc:  # TODO: test this
            logger.exception("Failed to read mesh file: %s", file)
            raise RuntimeError(f"Could not read mesh file {file}: {exc}") from exc

    @property
    def points(self) -> Any:  # TODO: test this, try set and get
        return self._points

    @property
    def triangles(
        self,
    ) -> List[Any]:  ##TODO: ikke barre tiangle # TODO: test this, try set and get
        return list(self._triangles)

    @property
    def cells(self) -> Any:  # TODO: test this, try set and get
        return self._cells

    # --- Utility ---
    def reload(
        self, file: str
    ) -> (
        None
    ):  # TODO: test this, with valid and invalid paths, With same path, different path
        """Reload the mesh from a new file path."""
        if not isinstance(file, str):
            raise TypeError("file must be a path string")
        if not os.path.exists(file):
            raise FileNotFoundError(f"Mesh file not found: {file}")

        self._msh = self._readMesh(file)
        self._points = getattr(self._msh, "points", [])
        self._triangles = getattr(self._msh, "cells_dict", {}).get("triangle", [])
        self._cells = CellFactory(self._msh)
