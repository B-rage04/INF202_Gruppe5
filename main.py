from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"))
sim.run_sim()
