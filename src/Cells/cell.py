import time
from abc import ABC, abstractmethod

import numpy as np
from tqdm import tqdm
from src.config import Config


class Cell(ABC):
    """
    General parent class for all cell types

    stores all values each cell needs

    with the exception of oil and newOil all values are fixed
    """

    def __init__(self, msh, cell_points, cell_id, config: Config = None, *, flow_fn=None, oil_fn=None):
        # identity
        self._id = cell_id
        # keep reference to mesh only for contextual use (no direct internal caching of mesh maps)
        self._msh = msh

        # validate config once
        if not isinstance(config, Config):
            raise TypeError("config must be a Config instance")
        self._config = config

        # private geometry storage; freeze public access via property
        self._points = tuple(msh.points[i] for i in cell_points)

        # cached geometric/physical values (explicitly computed or invalidated)
        self._midpoint = None
        self._area = None
        self._point_set = None
        self._scaled_normals = None  # list of normals to neighbors

        # neighbors are stored as IDs only; discovery is explicit
        self._neighbors = tuple()

        # physics values and their provider functions (extensible)
        self._flow = None
        self._oil = None
        self._flow_fn = flow_fn or self._default_flow
        self._oil_fn = oil_fn or self._default_oil

        # computed flags
        self.compute_flow()  # compute initial flow
        self.compute_oil()  # compute initial oil

        # domain-specific flag (keeps original behaviour but uses config safely)
        self._is_fishing = self._compute_is_fishing()

    # ---------- ID ----------
    @property
    def id(self) -> int:
        return self._id

    # allow id assignment if necessary, but keep explicit
    @id.setter
    def id(self, val: int):
        self._id = int(val)

    # ---------- geometry ----------
    @property
    def points(self):
        """
        Returnerer cellehjørner som en tuple av tuples (read-only).
        """
        return tuple(tuple(p) for p in self._points)

    @property
    def midpoint(self):
        if self._midpoint is None:
            self._midpoint = self._compute_midpoint()
        return np.array(self._midpoint)

    def _compute_midpoint(self):
        return np.mean(self._points, axis=0)

    @property
    def area(self):
        if self._area is None:
            self._area = self.findArea()
        return float(self._area)

    @property
    def point_set(self):
        if self._point_set is None:
            self._point_set = frozenset(tuple(p) for p in self._points)
        return self._point_set

    # ---------- neighbors (IDs) ----------
    @property
    def neighbors(self):
        """Returnerer nabocelle-IDer som en tuple (read-only).

        Beregning av naboer skjer eksternt og injiseres via compute_neighbors_from_maps.
        """
        return self._neighbors

    def compute_neighbors_from_maps(self, point_to_cells: dict, id_to_cell: dict):
        """Beregn naboskap basert på eksterne kart.

        point_to_cells: mapping fra punkt -> liste av celle-IDer
        id_to_cell: mapping fra id -> celleobjekt (kun for symmetrisk oppdatering)
        """
        counts = {}
        for p in self._points:
            for cid in point_to_cells.get(tuple(p), []):
                if cid == self._id:
                    continue
                counts[cid] = counts.get(cid, 0) + 1

        neigh = [cid for cid, shared in counts.items() if shared >= 2]
        self._neighbors = tuple(sorted(neigh))

        # symmetrisk oppdatering på eksternt cell-objekt dersom tilgjengelig
        for cid in self._neighbors:
            other = id_to_cell.get(cid)
            if other is not None:
                # ensure other has this cell as neighbor without mutating its internals directly
                if self._id not in other._neighbors:
                    other._neighbors = tuple(sorted(other._neighbors + (self._id,)))

    # ---------- scaled normals (explicit compute) ----------
    @property
    def scaled_normals(self):
        """Returnerer cached scaled normals eller None hvis ikke beregnet."""
        return self._scaled_normals

    def compute_scaled_normals(self, id_to_cell: dict, *, disable_tqdm_threshold: int = 10):
        """Beregner og cacher skalert normalvektor mot hver nabo.

        id_to_cell: mapping fra id -> cell objekt for å lese nabo-geometri.
        """
        if not self._neighbors:
            self._scaled_normals = []
            return self._scaled_normals

        self_points = self.point_set
        scaled = []
        disable = len(self._neighbors) < disable_tqdm_threshold
        start = time.perf_counter()
        for nid in tqdm(self._neighbors, desc=f"Triangle {self.id:04d} normals", unit="ngb", leave=False, disable=disable):
            ngb = id_to_cell.get(nid)
            if ngb is None:
                continue
            shared = self_points & ngb.point_set
            if len(shared) < 2:
                continue
            shared_iter = sorted(shared)
            A = np.array(shared_iter[0])
            B = np.array(shared_iter[1])
            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midpoint[0] - A[0], self.midpoint[1] - A[1]])
            if np.dot(n, v) > 0:
                n = -n
            scaled.append(n)
        if not disable:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"Triangle {self.id:04d} normals completed in {elapsed_ms:.2f} ms")
        self._scaled_normals = scaled
        return self._scaled_normals

    # ---------- physics (flow, oil) ----------
    def _default_flow(self):
        # preserve original numeric result
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

    def compute_flow(self, flow_fn=None):
        """Beregn eller oppdater strømmen for cellen.

        Kan ta en alternativ `flow_fn` som tar `cell` og returnerer en numpy-array.
        """
        fn = flow_fn or self._flow_fn
        # Attempt to call both zero-arg and single-arg styles to support bound/unbound callables.
        if not callable(fn):
            raise TypeError("flow_fn must be callable")
        try:
            val = fn()
        except TypeError:
            val = fn(self)
        self._flow = np.array(val)
        return self._flow

    @property
    def flow(self):
        return np.array(self._flow)

    def _default_oil(self):
        return np.exp(-(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01)

    def compute_oil(self, oil_fn=None):
        """Beregn eller oppdater oljeinnhold for cellen.

        Klamping gjøres eksakt her for å sentralisere validering.
        """
        fn = oil_fn or self._oil_fn
        if not callable(fn):
            raise TypeError("oil_fn must be callable")
        try:
            val = fn()
        except TypeError:
            val = fn(self)
        self._oil = self._clamp_oil(float(val))
        return self._oil

    @staticmethod
    def _clamp_oil(v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v

    @property
    def oil(self) -> float:
        return float(self._oil)

    def set_oil(self, value):
        """Eksplisitt oppdatering av oljeinnhold (valideres og klampes)."""
        self._oil = self._clamp_oil(float(value))

    # ---------- abstract area calculation ----------
    @abstractmethod
    def findArea(self):
        """Beregn areal — implementeres i underklasser."""
        raise NotImplementedError

    # ---------- helper for fishing region (keeps previous semantics) ----------
    def _compute_is_fishing(self):
        geo = self._config.geometry
        fishxmin = geo["borders"][0][0]
        fishxmax = geo["borders"][0][1]
        fishymin = geo["borders"][1][0]
        fishymax = geo["borders"][1][1]
        x, y = self.midpoint[0], self.midpoint[1]
        return fishxmin < x < fishxmax and fishymin < y < fishymax

    @property
    def isFishing(self):
        return bool(self._is_fishing)

