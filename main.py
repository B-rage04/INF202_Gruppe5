import time

ti_bib = time.time()
from src.mesh import Mesh
from src.simulation import Simulation

sim = Simulation(Mesh("bay.msh"), "Exsample/SimConfig/BaseSimConfig.toml")

print("Running simulation...")
sim.run_sim(
    run_number=2, create_video=True, video_fps=60
)  # TODO vise barre enkelte graffer

"""
print(sim.config)
print(sim.time_end)
print(sim.nSteps)
print(sim.dt)
"""
tf = time.time()
print(f"Total execution time: {tf - ti_bib:.2f} seconds")
