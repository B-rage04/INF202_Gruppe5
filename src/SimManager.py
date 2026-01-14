import re
import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "Output" / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "sim.log"

print("Logging to:", LOG_FILE)

logging.basicConfig(
    filename="Output/log/sim.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from tqdm import tqdm
from typing import Any, Dict, List
from src.LoadTOML import LoadTOML
from src.simulation import Simulation

import os


def _next_run_number(images_dir: str = "Output/images") -> int:
    """Compute the next run index based on existing run folders in the images dir."""
    base = Path(images_dir)
    if not base.exists():
        return 0

    run_pattern = re.compile(r"run(\d+)$")
    existing = []
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        match = run_pattern.match(entry.name)
        if match:
            try:
                existing.append(int(match.group(1)))
            except ValueError:
                continue

    if not existing:
        return 0
    return max(existing) + 1


def main(
    globalConfigPath: str = "Example/Globalcofig/SysConfig.toml", **kwargs: Any
) -> None:
    """Load global config and run simulations defined by it."""

    logging.info("Running...")

    config_loader = LoadTOML()

    globalConfig: Dict[str, Any] = config_loader.loadTomlFile(globalConfigPath)
    
    logging.info(f"Loading sim configurations from: {globalConfig['settings']['pathToSimConfig']}")

    simConfigs: List[Dict[str, Any]] = config_loader.loadSimConfigs(globalConfig)

    

    videoPaths: List[str] = []

    for idx, simCFG in tqdm(
        enumerate(simConfigs),
        desc="Running oil spill simulations",
        total=len(simConfigs),
        unit="sim",
        colour="blue",
        ncols=100,
        ascii="-#",
    ):
        # Ensure imagesDir is set and consistent across pipeline
        images_dir = simCFG.get("IO", {}).get("imagesDir", "Output/images/")
        if "IO" not in simCFG:
            simCFG["IO"] = {}
        if "imagesDir" not in simCFG["IO"]:
            simCFG["IO"]["imagesDir"] = images_dir

        # Pick the next free run number based on current contents of the image directory
        run_number = _next_run_number(images_dir)

        sim = Simulation(simCFG)

        print(f"\nRunning simulation {run_number}...")
        path = sim.run_sim(runNumber=run_number, **kwargs)

        if path is not None:
            print(f"Video created at: {path}")
            videoPaths.append(path)

        print(f"Simulation {run_number} complete.")

    print("\n=== All videos created ===")
    for path in videoPaths:
        print(f"{path}")


if __name__ == "__main__":
    main()
