import logging
import os
from typing import Any, List
from src.config import Config

from src.Cells.cellFactory import CellFactory


class Mesh:
    def __init__(self, file: str, config=None) -> None:
        if not isinstance(file, str):
            raise TypeError("file must be a path string")  # TODO: test this

        # Validate config type if provided
        if config is not None and not isinstance(config, Config):
            raise TypeError("config must be a Config instance or None")

        # Try to read mesh; on failure create a minimal placeholder mesh
        msh_obj = None
        try:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Mesh file not found: {file}")
            msh_obj = self._readMesh(file)
        except Exception:
            raise FileNotFoundError(f"Could not read mesh file: {file}")

        self._msh: Any = msh_obj
        self.config = config if config is not None else None
        self._points: List[Any] = getattr(self._msh, "points", [])
        self._triangles: List[Any] = getattr(self._msh, "cells_dict", {}).get(
            "triangle", []
        )

        self._cellFactory = CellFactory(self._msh, self.config)
        self._cells = self._cellFactory()

    def _readMesh(self, file: str) -> Any:
        try:  # TODO: test this
            import meshio

            msh = meshio.read(file)
            return msh
        except Exception as exc:  # TODO: test this
            raise RuntimeError(f"Could not read mesh file {file}: {exc}") from exc

    @property
    def points(self) -> Any:  # TODO: test this, try set and get
        return self._points

    @property
    def triangles(
        self,
    ) -> List[Any]:  # TODO: not just triangle # TODO: test this, try set and get
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
        # Recreate cell factory and rebuild cells (Config preserved)
        self._cellFactory = CellFactory(self._msh, self.config)
        self._cells = self._cellFactory()
