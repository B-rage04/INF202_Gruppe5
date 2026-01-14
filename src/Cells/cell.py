from abc import ABC, abstractmethod

import numpy as np
from tqdm import tqdm


class Cell(ABC):
    """
    General parent class for all cell types

    stores all values each cell needs

    with the exception of oil and newOil all values are fixed
    """

    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self._id = cell_id
        # keep reference to mesh so we can compute geometry against all cells
        self._msh = msh
        # set backing fields directly to avoid invoking property setters
        self._cords = [msh.points[i] for i in cell_points]
        self._midPoint = self.findMidPoint()
        self._area = self.findArea()
        self._scaledNormal = None
        self._pointSet = None
        self._ngb = []
        self._flow = np.array(self.findFlow())
        self._oil = self.findOil()
        self.newOil = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def cords(self):
        return self._cords

    @cords.setter
    def cords(self, value):
        self._cords = list(value)
        self._midPoint = self.findMidPoint()
        self._area = self.findArea()
        self._scaledNormal = self.findScaledNormales()
        self._pointSet = None
        self._flow = self.findFlow()
        self._oil = self.findOil()

    @property
    def midPoint(self):
        return self._midPoint

    @property
    def area(self):
        return self._area

    @property  # TODO Brage: test getters and setters
    def scaledNormal(self):
        if self._scaledNormal is None:
            # try to compute scaled normals with access to all cells when available
            if getattr(self, "_msh", None) is not None:
                val = self.findScaledNormales(self._msh.cells)
            else:
                val = self.findScaledNormales()
            # ensure numpy array
            self._scaledNormal = np.array(val) if val is not None else np.zeros(3)
        return self._scaledNormal

    @property  # TODO Brage: test getters and setters
    def pointSet(self):
        if self._pointSet is None:
            self._pointSet = set(tuple(p) for p in self._cords)
        return self._pointSet

    @property
    def ngb(self):
        return self._ngb

    @property
    def flow(self):
        if self._flow is None:
            self._flow = np.array(self.findFlow())
        return self._flow

    @flow.setter
    def flow(self, value):
        self._flow = np.array(value)

    @property
    def oil(self):
        if self._oil is None:
            self._oil = self.findOil()
        return self._oil

    @oil.setter  # TODO : dette kan hene er feil løsning men jeg fikk feilmed at oljen ble setet negatift
    def oil(self, value):
        try:
            v = float(value)
        except Exception:
            raise TypeError("oil value must be numeric")

        if v < 0.0:
            print(f"Clamping oil for cell {self.id} from {v} to 0.0")
            v = 0.0
        elif v > 1.0:
            print(f"Clamping oil for cell {self.id} from {v} to 1.0")
            v = 1.0

        self._oil = v

    @abstractmethod
    def findArea(self):
        """
        See child class for individual claculations
        """
        pass

    def findMidPoint(self):  # TODO Brage: test this
        return np.mean(self.cords, axis=0)

    def findScaledNormales(self, allCells=None):
        if not allCells or not self.ngb:
            self._scaledNormal = []
            return self._scaledNormal

        msh = getattr(self, "_msh", None)

        # Reuse mesh-level id map if available to avoid rebuilding per cell
        if msh is not None and hasattr(msh, "_id_to_cell"):
            cellsDict = msh._id_to_cell
        else:
            cellsDict = {cell.id: cell for cell in allCells}

        # cache point sets
        selfPoints = getattr(self, "_pointSet", None)
        if selfPoints is None:
            selfPoints = set(tuple(p) for p in self.cords)
            self._pointSet = selfPoints

        scaledNormals = []
        disable_ngb_tqdm = len(self.ngb) < 10

        for ngbId in tqdm(
            self.ngb,
            desc=f"Triangle {self.id:04d} normals",
            unit="ngb",
            leave=False,
            colour="cyan",
            ascii="-#",
            disable=disable_ngb_tqdm,
        ):
            ngbCell = cellsDict.get(ngbId)
            if ngbCell is None:
                continue

            ngbPoints = getattr(ngbCell, "_pointSet", None)
            if ngbPoints is None:
                ngbPoints = set(tuple(p) for p in ngbCell.cords)
                ngbCell._pointSet = ngbPoints

            # find up to two shared points without creating intermediate lists
            shared = selfPoints & ngbPoints
            if len(shared) < 2:
                continue
            # deterministic ordering: sort for reproducibility
            shared_iter = sorted(shared)
            A = np.array(shared_iter[0])
            B = np.array(shared_iter[1])

            d = np.array([B[0] - A[0], B[1] - A[1]])
            n = np.array([d[1], -d[0]])
            v = np.array([self.midPoint[0] - A[0], self.midPoint[1] - A[1]])
            if np.dot(n, v) > 0:
                n = -n
            scaledNormals.append(n)

        self._scaledNormal = scaledNormals
        return self._scaledNormal

        # TODO Brage: else calculate it and set and return it

    def findNGB(self, allCells):
        Localmsh = getattr(
            self, "_msh", None
        )  # er et lokalt msh får cellen får å lagre ref til naboer. dette er får at neste cellen barre kan se på data og ikke kalkulere den

        # Build or reuse a mapping from point (tuple) -> list of cell ids
        if Localmsh is not None:
            if not hasattr(Localmsh, "_point_to_cells"):
                # lager en tabe som gir alle cellers id som deler et punkt
                pt_map = {}
                for c in allCells:
                    for p in c.cords:
                        key = tuple(p)
                        pt_map.setdefault(key, []).append(c.id)
                Localmsh._point_to_cells = pt_map
            pt_map = Localmsh._point_to_cells

            if not hasattr(Localmsh, "_id_to_cell"):
                # lager en tabel som git en id gir celle objectet
                id_map = {c.id: c for c in allCells}
                Localmsh._id_to_cell = id_map
            id_map = Localmsh._id_to_cell
        else:
            pt_map = {}
            id_map = {c.id: c for c in allCells}
            for c in allCells:
                for p in c.cords:
                    key = tuple(p)
                    pt_map.setdefault(key, []).append(c.id)

        # Finner ID til naboceller som har delte punkter
        counts = {}
        for p in self.cords:
            for cid in pt_map.get(tuple(p), []):
                if cid == self.id:
                    continue
                counts[cid] = counts.get(cid, 0) + 1

        # Any cell sharing two or more points is a neighbor
        for cid, cnt in counts.items():
            if cnt >= 2:
                other = id_map.get(cid)
                if other is None:
                    continue
                if cid not in self._ngb:
                    self._ngb.append(cid)
                if self.id not in other._ngb:
                    other._ngb.append(self.id)

    def findFlow(self):  # TODO Brage: add ability to set flow function
        return np.array(
            [self.midPoint[1] - self.midPoint[0] * 0.2, -self.midPoint[0]]
        )  # TODO Brage: test this

        # TODO Brage: if has attribute return it
        # TODO Brage: else calculate it and set and return it

    def findOil(self):  # TODO Brage: add ability to set oil function
        return np.exp(
            -(np.linalg.norm(self.midPoint - np.array([0.35, 0.45, 0])) ** 2) / 0.01
        )  # TODO Brage: test this
