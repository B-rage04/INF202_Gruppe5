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

import argparse as argparse
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


def _validate_sim_config(config: Dict[str, Any], config_path: str) -> None:
    """Validate that simulation config has required structure and entries."""
    required_sections = ["settings", "geometry", "IO", "video"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section '[{section}]' in {config_path}")
    
    # Validate settings section
    required_settings = ["nSteps", "tStart", "tEnd"]
    for key in required_settings:
        if key not in config["settings"]:
            raise ValueError(f"Missing required key '{key}' in [settings] section of {config_path}")
    
    # Validate geometry section
    if "meshName" not in config["geometry"]:
        raise ValueError(f"Missing required key 'meshName' in [geometry] section of {config_path}")
    
    # Validate IO section - logName is optional, defaults to "logfile"
    if "writeFrequency" not in config["IO"]:
        raise ValueError(f"Missing required key 'writeFrequency' in [IO] section of {config_path}")
    
    # Validate video section
    required_video = ["videoFPS"]
    for key in required_video:
        if key not in config["video"]:
            raise ValueError(f"Missing required key '{key}' in [video] section of {config_path}")


def _get_config_files(folder: str) -> List[str]:
    """Get all TOML files in the specified folder."""
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"Folder '{folder}' does not exist or is not a directory")
    
    config_files = sorted(folder_path.glob("*.toml"))
    if not config_files:
        raise ValueError(f"No TOML config files found in '{folder}'")
    
    return [str(f) for f in config_files]


def _is_result_folder(folder_path: Path) -> bool:
    """Check if a folder looks like a result folder (contains images/videos)."""
    return (folder_path / "images").exists() or (folder_path / "videos").exists()


def _create_result_folder(base_name: str, output_dir: str = "Output") -> str:
    """
    Create a result folder named after config file, avoiding overwrites of non-result folders.
    Returns the path to the output folder.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    folder_path = output_path / base_name
    
    # If folder exists and is NOT a result folder, don't overwrite it
    if folder_path.exists() and not _is_result_folder(folder_path):
        raise ValueError(
            f"Cannot create output folder '{folder_path}'. "
            f"A non-result folder with this name already exists."
        )
    
    folder_path.mkdir(parents=True, exist_ok=True)
    return str(folder_path)


def main(**kwargs: Any) -> None:
    """Load config and run simulations."""

    p = argparse.ArgumentParser(
        prog="oil_spill_simulation",
        description="Oil spill simulation tool with configurable config files"
    )
    p.add_argument(
        "-c", "--config",
        dest="config_file",
        default=None,
        help="Specific config file to read (default: input.toml if --find all not specified)"
    )
    p.add_argument(
        "-f", "--folder",
        dest="folder",
        default=None,
        help="Folder to search for config files (used with --find all)"
    )
    p.add_argument(
        "--find_all",
        dest="find_all",
        action="store_true",
        help="Find and run all config files in the specified or current folder"
    )

    args = p.parse_args()

    logging.info("Running...")

    config_loader = LoadTOML()
    videoPaths: List[str] = []

    try:
        if args.find_all:
            # Find and run all config files in folder
            search_folder = args.folder if args.folder else "."
            config_files = _get_config_files(search_folder)
            
            for config_path in config_files:
                try:
                    config = config_loader.loadTomlFile(config_path)
                    _validate_sim_config(config, config_path)
                    
                    # Set defaults for optional parameters
                    if "logName" not in config.get("IO", {}):
                        if "IO" not in config:
                            config["IO"] = {}
                        config["IO"]["logName"] = "logfile"
                    
                    # Create result folder based on config file name
                    config_name = Path(config_path).stem
                    result_folder = _create_result_folder(config_name)
                    
                    # Update config with output folder
                    if "IO" not in config:
                        config["IO"] = {}
                    config["IO"]["imagesDir"] = f"{result_folder}/images/"
                    config["IO"]["videosDir"] = f"{result_folder}/videos/"
                    
                    # Get next run number for this result folder
                    run_number = _next_run_number(f"{result_folder}/images/")
                    
                    sim = Simulation(config)
                    print(f"\nRunning simulation from {config_name}...")
                    path = sim.run_sim(runNumber=run_number, **kwargs)
                    
                    if path is not None:
                        print(f"Video created at: {path}")
                        videoPaths.append(path)
                    
                    print(f"Simulation from {config_name} complete.")
                    
                except (ValueError, FileNotFoundError) as e:
                    print(f"Error processing {config_path}: {e}")
                    continue
        
        else:
            # Run single config file
            config_file = args.config_file if args.config_file else "input.toml"
            
            # Determine config file path
            if args.folder:
                # If folder is specified, look for config file there
                config_path = str(Path(args.folder) / config_file)
            elif args.config_file:
                # If a specific config file was requested, look in current folder
                config_path = config_file
            else:
                # Default: no config file or folder specified, use Defaults/input.toml
                config_path = str(Path("Defaults") / config_file)
            
            config = config_loader.loadTomlFile(config_path)
            _validate_sim_config(config, config_path)
            
            # Set defaults for optional parameters
            if "logName" not in config.get("IO", {}):
                if "IO" not in config:
                    config["IO"] = {}
                config["IO"]["logName"] = "logfile"
            
            # Get output directory from config or use default
            images_dir = config.get("IO", {}).get("imagesDir", "Output/images/")
            
            # Get next run number
            run_number = _next_run_number(images_dir)
            
            sim = Simulation(config)
            print(f"\nRunning simulation from {config_path}...")
            path = sim.run_sim(runNumber=run_number, **kwargs)
            
            if path is not None:
                print(f"Video created at: {path}")
                videoPaths.append(path)
            
            print(f"Simulation complete.")

    except FileNotFoundError as e:
        print(f"Error: Config file not found - {e}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    if videoPaths:
        print("\n=== All videos created ===")
        for path in videoPaths:
            print(f"{path}")


if __name__ == "__main__":
    main()

