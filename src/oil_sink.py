import numpy as np
from typing import Optional
class OilSinkSource:
    """
    Class representing an oil sink/source in the simulation.
    """

    def __init__(self, msh, configuration: Optional[dict] = None):
        if configuration is None:
            configuration = {}


        self.msh = msh
        self.position = np.array(configuration.get("position", [0.5, 0.5]))
        self.strength = configuration.get("strength", 1.0)
        self.type = configuration.get("type", "gaussian")
        self.radius = configuration.get("radius", 1.0)
        self.cellInRange = self.findCellsInRange(self.msh)

    def __call__(self, *args, **kwds):
        for cell_id, dist_value in self.cellInRange.items():
            cell_id.oil += self.distributions(type=self.type, distance=dist_value, radius=self.radius, sigma=self.strength)

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




    def distributions(type: str, distance: float, radius: float, sigma: float) -> float:
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