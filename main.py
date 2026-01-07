from src.simulation import Simulation
from src.mesh import Mesh

sim = Simulation(Mesh("bay.msh"))
sim.run_sim()