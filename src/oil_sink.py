import numpy as np
from typing import Optional, Dict, Union

from src.config import Config


def _get_cells_from_mesh(msh) -> list:
    """Extract triangle cells from mesh object."""
    try:
        cells = msh.cells if isinstance(msh.cells, list) else list(msh.cells)
        return [cell for cell in cells if getattr(cell, "type", None) == "triangle"]
    except (AttributeError, TypeError):
        return []


def _calculate_distance(cell_midpoint, position) -> float:
    """Calculate Euclidean distance between cell midpoint and position."""
    return np.linalg.norm(np.array(cell_midpoint[:2]) - np.array(position))


def _gaussian_coefficient(distance: float, sigma: float) -> float:
    """Compute Gaussian distribution coefficient."""
    return (1.0 / (2.0 * np.pi * sigma**2)) * np.exp(-distance**2 / (2.0 * sigma**2))


def _uniform_coefficient(distance: float, radius: float) -> float:
    """Compute uniform distribution coefficient."""
    return 1.0 if distance <= radius else 0.0


def _linear_coefficient(distance: float, radius: float) -> float:
    """Compute linear distribution coefficient."""
    if distance <= radius:
        return 1.0 - (distance / radius)
    return 0.0


def _get_distribution_coefficient(distance: float, mode: str, radius: float, sigma: float) -> float:
    """Get distribution coefficient based on mode."""
    if mode == "gaussian":
        return _gaussian_coefficient(distance, sigma)
    elif mode == "uniform":
        return _uniform_coefficient(distance, radius)
    elif mode == "linear":
        return _linear_coefficient(distance, radius)
    else:
        return 0.0


def compute_ship_sink(msh, ship_pos, radius=0.1, sigma=1.0, strength=1.0, mode="gaussian") -> Dict:
    """
    Precompute oil removal coefficients for cells near the ship.
    
    Parameters:
        msh: Mesh object containing cells
        ship_pos: [x, y] position of the ship
        radius: Maximum distance for oil removal (default 0.1)
        sigma: Standard deviation for Gaussian distribution (default 1.0)
        strength: Multiplier for removal strength (default 1.0)
        mode: Distribution type ('gaussian', 'uniform', or 'linear')
    
    Returns:
        Dictionary mapping cell_id -> removal coefficient
    """
    sink_coeffs = {}
    cells = _get_cells_from_mesh(msh)
    
    for cell in cells:
        distance = _calculate_distance(cell.midPoint, ship_pos)
        
        if distance <= radius:
            coefficient = _get_distribution_coefficient(distance, mode, radius, sigma)
            sink_coeffs[cell.id] = strength * coefficient
    
    return sink_coeffs


def compute_source(msh, source_pos, radius=0.1, sigma=1.0, strength=1.0, mode="gaussian") -> Dict:
    """
    Precompute oil injection coefficients for cells near the source.
    
    Parameters:
        msh: Mesh object containing cells
        source_pos: [x, y] position of the source
        radius: Maximum distance for oil injection (default 0.1)
        sigma: Standard deviation for Gaussian distribution (default 1.0)
        strength: Multiplier for injection strength (default 1.0)
        mode: Distribution type ('gaussian', 'uniform', or 'linear')
    
    Returns:
        Dictionary mapping cell_id -> injection coefficient
    """
    source_coeffs = {}
    cells = _get_cells_from_mesh(msh)
    
    for cell in cells:
        distance = _calculate_distance(cell.midPoint, source_pos)
        
        if distance <= radius:
            coefficient = _get_distribution_coefficient(distance, mode, radius, sigma)
            source_coeffs[cell.id] = strength * coefficient
    
    return source_coeffs


class OilSinkSource:
    """Class representing an oil sink/source in the simulation."""

    def __init__(self, msh, configuration: Optional[Union[dict, Config]] = None):
        cfg = self._parse_configuration(configuration)
        
        self.msh = msh
        self.position = np.array(cfg.get("position", [0.5, 0.5]))
        self.strength = cfg.get("strength", 1.0)
        self.type = cfg.get("type", "gaussian")
        self.radius = cfg.get("radius", 1.0)
        self.cellInRange = self._find_cells_in_range()

    def _parse_configuration(self, configuration) -> dict:
        """Extract configuration dictionary from various input types."""
        if configuration is None:
            return {}
        elif isinstance(configuration, Config):
            return configuration.other if getattr(configuration, "other", None) is not None else {}
        else:
            return configuration

    def __call__(self, *args, **kwds):
        """Apply oil sink/source effect to all cells in range."""
        for cell, dist_value in self.cellInRange.items():
            cell.oil += dist_value

    def _find_cells_in_range(self) -> Dict:
        """Find all cells within radius and compute their distribution values."""
        cells_in_range = {}
        for cell in self.msh.cells:
            distance = _calculate_distance(cell.midPoint, self.position)
            if distance <= self.radius:
                dist_value = _get_distribution_coefficient(
                    distance, self.type, self.radius, self.strength
                )
                cells_in_range[cell] = dist_value
        
        # DEBUG: Print how many cells were found
        print(f"Oil source: Found {len(cells_in_range)} cells in range")
        return cells_in_range