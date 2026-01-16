import logging
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "Output" / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "sim.log"

print("Logging to:", LOG_FILE)

logging.basicConfig(
    filename="Output/log/sim.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

import os
from typing import Any, List

from src.IO.config import Config
from src.IO.LoadTOML import LoadTOML
from src.IO import cmd
from src.Simulation.simulation import Simulation


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


def _get_config_files(folder: str) -> List[str]:
    """Get all TOML files in the specified folder."""
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"Folder '{folder}' does not exist or is not a directory")
    
    config_files = sorted(
                            f for f in folder_path.glob("*.toml") 
                            if f.name != "pyproject.toml"
                            )

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

    if folder_path.exists() and not _is_result_folder(folder_path):
        raise ValueError(
            f"Cannot create output folder '{folder_path}'. "
            f"A non-result folder with this name already exists."
        )

    folder_path.mkdir(parents=True, exist_ok=True)
    return str(folder_path)


def _resolve_config_path(config_file: str, folder: str = None) -> str:
    return cmd.resolve_config_path(config_file, folder)


def _setup_config_output(config: Config, config_name: str) -> str:
    """Create output folder and update config IO paths. Returns result folder path."""
    result_folder = _create_result_folder(config_name)
    config.IO["imagesDir"] = f"{result_folder}/images/"
    config.IO["videosDir"] = f"{result_folder}/videos/"
    return result_folder


def _run_single_simulation(config: Config, config_path: str, **kwargs: Any) -> str:
    """Execute a single simulation and return video path if created."""
    sim = Simulation(config)
    print(f"\nRunning simulation from {config_path}...")
    path = sim.run_sim(runNumber=_next_run_number(config.images_dir()), **kwargs)

    if path is not None:
        print(f"Video created at: {path}")

    return path


def _process_single_config(
    config_loader: LoadTOML, config_path: str, **kwargs: Any
) -> str:
    """Load, setup, and run a single config file. Returns video path or None."""
    config: Config = config_loader.loadConfigFile(config_path)
    config.IO.setdefault("logName", "logfile")

    config_name = Path(config_path).stem
    _setup_config_output(config, config_name)

    return _run_single_simulation(config, config_path, **kwargs)


def _process_all_configs(
    config_loader: LoadTOML, search_folder: str, **kwargs: Any
) -> List[str]:
    """Find and run all configs in folder. Returns list of video paths."""
    video_paths = []
    config_files = _get_config_files(search_folder)

    for config_path in config_files:
        try:
            video_path = _process_single_config(config_loader, config_path, **kwargs)
            if video_path:
                video_paths.append(video_path)

            config_name = Path(config_path).stem
            print(f"Simulation from {config_name} complete.")
        except (ValueError, FileNotFoundError) as e:
            print(f"Error processing {config_path}: {e}")
            continue

    return video_paths


def _run_find_all_mode(
    config_loader: LoadTOML, args: argparse.Namespace, **kwargs: Any
) -> List[str]:
    """Run all configs in specified or current folder."""
    search_folder = args.folder if args.folder else "."
    return _process_all_configs(config_loader, search_folder, **kwargs)


def _run_single_file_mode(
    config_loader: LoadTOML, args: argparse.Namespace, **kwargs: Any
) -> List[str]:
    """Run a single config file."""
    config_file = args.config_file if args.config_file else "input.toml"
    config_path = _resolve_config_path(config_file, args.folder)

    video_path = _process_single_config(config_loader, config_path, **kwargs)
    print(f"Simulation complete.")

    return [video_path] if video_path else []


def _print_video_summary(video_paths: List[str]) -> None:
    """Print summary of all created videos."""
    if video_paths:
        print("\n=== All videos created ===")
        for path in video_paths:
            print(f"{path}")


def main(**kwargs: Any) -> None:
    """Main entry point: parse args and run simulations."""
    logging.info("Running...")

    try:
        args = cmd.parse_arguments()
        config_loader = LoadTOML()

        if args.find_all:
            video_paths = _run_find_all_mode(config_loader, args, **kwargs)
        else:
            video_paths = _run_single_file_mode(config_loader, args, **kwargs)

        _print_video_summary(video_paths)

    except FileNotFoundError as e:
        print(f"Error: Config file not found - {e}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
