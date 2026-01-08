from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"))
#sim.run_sim()
print(sim.cells[-5].ngb)
print(sim.cells[-5].cords)
print(sim.cells[3437].cords)