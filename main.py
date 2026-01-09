import time

ti_bib = time.time()
from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"), "Exsample/SimConfig/BaseSimConfig.toml")

sim.run_sim(run_number=1)  # TODO vise barre enkelte graffer

"""
print(sim.config)
print(sim.time_end)
print(sim.nSteps)
print(sim.dt)
"""
tf = time.time()
