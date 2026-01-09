import time
ti_bib = time.time()
from src.mesh import Mesh
from src.simulation import Simulation
import numpy as np

ti_ngh = time.time()

sim = Simulation(Mesh("bay.msh"))

sim.run_sim()
print(sim.cells[-5].id)
print(sim.cells[-5].ngb)
print(sim.cells[-5].scaled_normal)
print(sim.cells[3615].id)
print(sim.cells[3615].ngb)
print(sim.cells[3615].scaled_normal)

tf = time.time()
print("Time elapsed bib:", tf - ti_bib)
print("Time elapsed ngh:", tf - ti_ngh)