from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"))


import random

cellIDToTest = random.randint(0, len(sim.cells)-1)
print("Testing cell ID:", cellIDToTest)
print(f"ngb of cell {cellIDToTest}:", sim.cells[cellIDToTest].ngb)
ngbID = sim.cells[cellIDToTest].ngb[0]
print(f"ngb of cell {ngbID}:", sim.cells[ngbID].ngb)
if not cellIDToTest in sim.cells[ngbID].ngb:
    print("Error: Neighbor relationship")
else:
    print("Neighbor relationship OK")