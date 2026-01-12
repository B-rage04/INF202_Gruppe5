import numpy as np


def compute_ship_sink(mesh, ship_pos, radius: float = 0.1, sigma: float = 1.0, strength: float = 100.0, mode: str = "uniform"):
	"""
	Compute per-cell sink coefficients for an oil collection ship.

	Parameters
	- mesh: Mesh instance providing cells with midpoints and ids
	- ship_pos: [x, y] list/tuple indicating ship position
	- radius: influence radius around ship position
	- sigma: standard deviation parameter (used for gaussian mode)
	- strength: base sink strength (1/time units), scales removal magnitude
	- mode: "uniform" (constant within radius) or "gaussian" (distance-weighted)

	Returns
	- dict mapping triangle cell id -> S_minus coefficient
	"""
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
	"""
	Compute per-cell source coefficients for oil injection.

	Parameters
	- mesh: Mesh instance providing cells with midpoints and ids
	- source_pos: [x, y] list/tuple indicating source position
	- radius: influence radius around source position
	- sigma: standard deviation parameter (used for gaussian mode)
	- strength: base source strength (1/time units), scales injection magnitude
	- mode: "uniform" (constant within radius) or "gaussian" (distance-weighted)

	Returns
	- dict mapping triangle cell id -> S_plus coefficient
	"""
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