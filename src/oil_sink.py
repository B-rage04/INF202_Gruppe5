from typing import Dict, Optional, Union

import numpy as np

from src.config import Config


def compute_ship_sink(
    msh, ship_pos, radius=0.1, sigma=1.0, strength=1.0, mode="gaussian"
):
    """
    Precompute oil removal coefficients for cells near the ship.

    The ship removes oil using a Gaussian distribution:
    S_i = (1 / (2πσ²)) * exp(-||x_S - x_mid||² / (2σ²))

    Parameters:
        msh: Mesh object containing cells
        ship_pos: [x, y] position of the ship
        radius: Maximum distance for oil removal (default 0.1)
        sigma: Standard deviation for Gaussian distribution (default 1.0)
        strength: Multiplier for removal strength (default 1.0)
        mode: Distribution type ('gaussian' or 'uniform')

    Returns:
        Dictionary mapping cell_id -> removal coefficient
    """
    ship_pos = np.array(ship_pos)
    sink_coeffs = {}

    # Get all triangle cells from the mesh
    try:
        cells = msh.cells if isinstance(msh.cells, list) else list(msh.cells)
    except (AttributeError, TypeError):
        return sink_coeffs

    for cell in cells:
        if getattr(cell, "type", None) != "triangle":
            continue

        midpoint = np.array(cell.midPoint[:2])
        distance = np.linalg.norm(midpoint - ship_pos)

        if distance <= radius:
            if mode == "gaussian":
                # Gaussian formula: S_i = (1/(2πσ²)) * exp(-||x_S - x_mid||² / (2σ²))
                coefficient = (1.0 / (2.0 * np.pi * sigma**2)) * np.exp(
                    -(distance**2) / (2.0 * sigma**2)
                )
            elif mode == "uniform":
                coefficient = 1.0
            else:
                coefficient = 0.0

            # Store positive coefficient for sink (S_i^- > 0)
            sink_coeffs[cell.id] = strength * coefficient

    return sink_coeffs


def compute_source(
    msh, source_pos, radius=0.1, sigma=1.0, strength=1.0, mode="gaussian"
):
    """
    Precompute oil injection coefficients for cells near the source.

    Uses the same Gaussian distribution as the ship sink but with positive values.

    Parameters:
        msh: Mesh object containing cells
        source_pos: [x, y] position of the source
        radius: Maximum distance for oil injection (default 0.1)
        sigma: Standard deviation for Gaussian distribution (default 1.0)
        strength: Multiplier for injection strength (default 1.0)
        mode: Distribution type ('gaussian' or 'uniform')

    Returns:
        Dictionary mapping cell_id -> injection coefficient
    """
    source_pos = np.array(source_pos)
    source_coeffs = {}

    # Get all triangle cells from the mesh
    try:
        cells = msh.cells if isinstance(msh.cells, list) else list(msh.cells)
    except (AttributeError, TypeError):
        return source_coeffs

    for cell in cells:
        if getattr(cell, "type", None) != "triangle":
            continue

        midpoint = np.array(cell.midPoint[:2])
        distance = np.linalg.norm(midpoint - source_pos)

        if distance <= radius:
            if mode == "gaussian":
                # Gaussian formula: S_i = (1/(2πσ²)) * exp(-||x_S - x_mid||² / (2σ²))
                coefficient = (1.0 / (2.0 * np.pi * sigma**2)) * np.exp(
                    -(distance**2) / (2.0 * sigma**2)
                )
            elif mode == "uniform":
                coefficient = 1.0
            else:
                coefficient = 0.0

            # Positive for source (injection)
            source_coeffs[cell.id] = strength * coefficient

    return source_coeffs


class OilSinkSource:
    """
    Class representing an oil sink/source in the simulation.
    """

    def __init__(self, msh, configuration: Optional[Union[dict, Config]] = None):
        if configuration is None:
            cfg = {}
        elif isinstance(configuration, Config):
            cfg = (
                configuration.other
                if getattr(configuration, "other", None) is not None
                else {}
            )
        else:
            cfg = configuration

        self.msh = msh
        self.position = np.array(cfg.get("position", [0.5, 0.5]))
        self.strength = cfg.get("strength", 1.0)
        self.type = cfg.get("type", "gaussian")
        self.radius = cfg.get("radius", 1.0)
        self.cellInRange = self.findCellsInRange(self.msh)

    def __call__(self, *args, **kwds):
        for cell_id, dist_value in self.cellInRange.items():
            cell_id.oil += self.distributions(
                type=self.type,
                distance=dist_value,
                radius=self.radius,
                sigma=self.strength,
            )

    def findCellsInRange(self, msh):
        cells_in_range = {}
        for cell in msh.cells:
            distance = np.linalg.norm(cell.midPoint[:2] - self.position)
            if distance <= self.radius:
                dist_value = self.distributions(
                    self.type, distance, self.radius, self.strength
                )
                cells_in_range[cell.id] = dist_value
        return cells_in_range

    def distributions(
        self, type: str, distance: float, radius: float, sigma: float
    ) -> float:
        """
        Compute the distribution value based on the specified type.

        Parameters:
        type (str): The type of distribution ('gaussian' or 'uniform').
        distance (float): The distance from the sink/source.
        radius (float): The effective radius for uniform distribution.
        sigma (float): The standard deviation for Gaussian distribution.

        Returns:
        float: The computed distribution value.
        """
        if type == "gaussian":
            return np.exp(-0.5 * (distance / sigma) ** 2)

        elif type == "uniform":
            return 1.0 if distance <= radius else 0.0

        elif type == "linear":
            if distance <= radius:
                return 1.0 - (distance / radius)
            else:
                return 0.0

        else:
            raise ValueError(f"Unknown distribution type: {type}")
