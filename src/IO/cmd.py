"""CLI argument utilities for the oil spill simulation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional


def parse_arguments() -> argparse.Namespace:
	"""Parse and return command-line arguments for the simulator CLI."""

	parser = argparse.ArgumentParser(
		prog="oil_spill_simulation",
		description="Oil spill simulation tool with configurable config files",
	)
	parser.add_argument(
		"-c",
		"--config",
		dest="config_file",
		default=None,
		help="Specific config file to read (default: input.toml if --find_all not specified)",
	)
	parser.add_argument(
		"-f",
		"--folder",
		dest="folder",
		default=None,
		help="Folder to search for config files (used with --find_all)",
	)
	parser.add_argument(
		"--find_all",
		dest="find_all",
		action="store_true",
		help="Find and run all config files in the specified or current folder",
	)
	return parser.parse_args()


def resolve_config_path(config_file: Optional[str], folder: Optional[str] = None) -> str:
	"""Resolve the full path to a config file based on arguments."""
	if folder:
		return str(Path(folder) / (config_file or ""))
	if config_file:
		return config_file
	return str(Path("Defaults") / "input.toml")
