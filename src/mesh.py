import logging
import os
from typing import Any, List

from src.Cells.cellFactory import CellFactory

logger = logging.getLogger(__name__)


class Mesh:
    def __init__(self, file: str) -> None:
        if not isinstance(file, str):
            raise TypeError("file must be a path string")

        if not os.path.exists(file):
            raise FileNotFoundError(f"Mesh file not found: {file}")

        self._msh: Any = self._read_mesh(file)

        self._points: List[Any] = getattr(self._msh, "points", [])
        self._triangles: List[Any] = getattr(self._msh, "cells_dict", {}).get(
            "triangle", []
        )
        self._cells = CellFactory(self._msh)

    def _read_mesh(self, file: str) -> Any:
        try:
            import meshio

            msh = meshio.read(file)
            logger.info("Loaded mesh from %s", file)
            return msh
        except Exception as exc:
            logger.exception("Failed to read mesh file: %s", file)
            raise RuntimeError(f"Could not read mesh file {file}: {exc}") from exc

    @property
    def points(self) -> Any:
        return self._points

    @property
    def triangles(self) -> List[Any]:  ##TODO: ikke barre tiangle
        return list(self._triangles)

    @property
    def cells(self) -> Any:
        return self._cells

    # --- Utility ---
    def reload(self, file: str) -> None:
        """Reload the mesh from a new file path."""
        if not isinstance(file, str):
            raise TypeError("file must be a path string")
        if not os.path.exists(file):
            raise FileNotFoundError(f"Mesh file not found: {file}")

        self._msh = self._read_mesh(file)
        self._points = getattr(self._msh, "points", [])
        self._triangles = getattr(self._msh, "cells_dict", {}).get("triangle", [])
        self._cells = CellFactory(self._msh)
