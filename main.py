import time

ti_bib = time.time()

from src.LoadTOML import LoadTOML
from src.simulation import Simulation

ConfigLoader = LoadTOML()

globalConfigPath = "Exsample/Globalcofig/SysConfig.toml"

globalConfig = ConfigLoader.load_toml_file(globalConfigPath)
simConfig = ConfigLoader.load_sim_configs(globalConfig)

sim = Simulation(simConfig[0])  # TODO velge riktig sim config hvis flere

print("Running simulation...")
sim.run_sim(
    run_number=2, create_video=True, video_fps=60
)  # TODO vise barre enkelte graffer
print("Simulation complete.")
