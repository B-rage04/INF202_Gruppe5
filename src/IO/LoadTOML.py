"""Utilities for loading TOML configuration files.

This module preserves the original camelCase API but adds clearer
aliases and documentation for readability.
"""

import os
import time
import tomllib as toml
from typing import Dict, List

from tqdm import tqdm

from src.IO.config import Config


class LoadTOML:
    """Load TOML files and optionally return validated `Config` objects."""

    def loadTomlFile(self, filePath: str) -> Dict:
        """Load a TOML file and return its raw dictionary.

        Raises FileNotFoundError if the path does not exist, or OSError for IO
        errors. Parsing errors from the TOML library will propagate up.
        """
        with open(filePath, "rb") as tomlFile:
            return toml.load(tomlFile)

    def loadConfigFile(self, filePath: str) -> Config:
        """Load a TOML file and return a validated `Config` instance."""
        data = self.loadTomlFile(filePath)
        return Config.from_dict(data)

    def loadSimConfigs(self, sysConfig: Dict, as_config: bool = False) -> List:
        """Load simulation config(s) from a configured path.

        Parameters
        - sysConfig: system-level config containing `settings.pathToSimConfig`.
        - as_config: if True, return a list of `Config` objects; otherwise return raw dicts.
        """
        sim_configs: List = []
        simConfigPath = sysConfig["settings"]["pathToSimConfig"]

        if os.path.isdir(simConfigPath):
            files = [f for f in os.listdir(simConfigPath) if f.endswith(".toml")]
            start_time = time.perf_counter()
            for fileName in tqdm(
                files,
                desc="Loading configuration files",
                unit="file",
                colour="magenta",
                ncols=100,
                ascii="-#",
            ):
                fullPath = os.path.join(simConfigPath, fileName)
                sim_configs.append(
                    self.loadConfigFile(fullPath)
                    if as_config
                    else self.loadTomlFile(fullPath)
                )
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            print(f"Loading configuration files completed in {elapsed_ms:.2f} ms")
        else:
            sim_configs.append(
                self.loadConfigFile(simConfigPath)
                if as_config
                else self.loadTomlFile(simConfigPath)
            )

        return sim_configs
