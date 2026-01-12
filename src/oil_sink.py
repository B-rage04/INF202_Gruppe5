import numpy as np


def compute_ship_sink(mesh, ship_pos, radius: float = 0.1, sigma: float = 1.0, strength: float = 100.0, mode: str = "uniform"):
	if ship_pos is None:
		return {}

	ship_xy = np.array([ship_pos[0], ship_pos[1]])
	s_minus = {}

	for cell in mesh.cells:
		if getattr(cell, "type", None) != "triangle":
			continue

		cell_xy = np.array([cell.midpoint[0], cell.midpoint[1]])
		d = np.linalg.norm(cell_xy - ship_xy)
		if d <= radius:
			if mode == "gaussian":
				weight = np.exp(-(d ** 2) / (2.0 * (sigma ** 2)))
			else:
				weight = 1.0

			s_minus[cell.id] = strength * weight

	return s_minus

def compute_source(mesh, source_pos, radius: float = 0.1, sigma: float = 1.0, strength: float = 100.0, mode: str = "uniform"):
	if source_pos is None:
		return {}

	source_xy = np.array([source_pos[0], source_pos[1]])
	s_plus = {}

	for cell in mesh.cells:
		if getattr(cell, "type", None) != "triangle":
			continue

		cell_xy = np.array([cell.midpoint[0], cell.midpoint[1]])
		d = np.linalg.norm(cell_xy - source_xy)
		if d <= radius:
			if mode == "gaussian":
				weight = np.exp(-(d ** 2) / (2.0 * (sigma ** 2)))
			else:
				weight = 1.0

			s_plus[cell.id] = strength * weight

	return s_plus