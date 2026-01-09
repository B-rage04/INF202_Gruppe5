from src.mesh import Mesh
from src.simulation import Simulation
import time

ti = time.time()
sim = Simulation(Mesh("bay.msh"))
# sim.run_sim()
print(sim.cells[3707].id)
print(sim.cells[3707].ngb)
print(sim.cells[3615].id)
print(sim.cells[3615].ngb)
tf = time.time()

print(tf-ti)