from typing import Any, Dict, List

from src.LoadTOML import LoadTOML
from src.simulation import Simulation


def main(
    globalConfigPath: str = "Example/Globalcofig/SysConfig.toml", **kwargs: Any
) -> None:
    """Load global config and run simulations defined by it."""
    config_loader = LoadTOML()

    globalConfig: Dict[str, Any] = config_loader.loadTomlFile(globalConfigPath)
    simConfigs: List[Dict[str, Any]] = config_loader.loadSimConfigs(globalConfig)

    videoPaths: List[str] = []

    for idx, simCFG in enumerate(simConfigs):
        sim = Simulation(simCFG)

        print(f"Running simulation {idx}...")
        path = sim.run_sim(runNumber=idx, **kwargs)

        if path is not None:
            print(f"Video created at: {path}")
            videoPaths.append(path)

        print(f"Simulation {idx} complete.")

    for path in videoPaths:
        print(f"Video created at: {path}")


if __name__ == "__main__":
    main()
