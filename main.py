import time
ti_bib = time.time()
from src.mesh import Mesh
from src.simulation import Simulation
import numpy as np

ti_ngh = time.time()

sim = Simulation(Mesh("bay.msh"), "Exsample/SimConfig/BaseSimConfig.toml")
sim.run_sim()
print(sim.config)
print(sim.time_end)
print(sim.nSteps)
print(sim.dt)
tf = time.time()
print("Time elapsed bib:", tf - ti_bib)
print("Time elapsed ngh:", tf - ti_ngh)