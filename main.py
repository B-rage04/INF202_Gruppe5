import time

ti_bib = time.time()
from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"), "Exsample/SimConfig/BaseSimConfig.toml")

sim.run_sim(run_number=1)

"""
print(sim.config)
print(sim.time_end)
print(sim.nSteps)
print(sim.dt)
"""
tf = time.time()
#print("Time elapsed bib:", tf - ti_bib)
#print("Time elapsed ngh:", tf - ti_ngh)
