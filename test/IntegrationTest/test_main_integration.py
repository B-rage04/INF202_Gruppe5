import os
from pathlib import Path
from unittest.mock import MagicMock

import tomllib

from src.Simulation import SimManager


class FakeSim:
    def __init__(self, cfg):
        self.cfg = cfg
        self.called = False

    def run_sim(self, **kwargs):
        self.called = True
        return None


def test_main_find_all_creates_output_and_runs(tmp_path, monkeypatch):
    # Create a temporary config folder and a minimal TOML config
    cfg_folder = tmp_path / "configs"
    cfg_folder.mkdir()

    cfg_path = cfg_folder / "test_config.toml"
    toml_data = {
        "geometry": {"meshName": "dummy.msh"},
        "settings": {"tStart": 0, "tEnd": 0.1, "nSteps": 1},
        "IO": {"writeFrequency": 0},
        "video": {"videoFPS": 5},
    }

    toml_string = (
        "[geometry]\nmeshName = \"dummy.msh\"\n"
        "[settings]\ntStart = 0\ntEnd = 0.1\nnSteps = 1\n"
        "[IO]\nwriteFrequency = 0\n[video]\nvideoFPS = 5\n"
    )

    cfg_path.write_text(toml_string)

    # Replace the Simulation class used by SimManager with our FakeSim factory
    def sim_factory(config):
        return FakeSim(config)

    monkeypatch.setattr(SimManager, "Simulation", sim_factory)

    # Run main in find_all mode pointing at our cfg_folder
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    monkeypatch.setattr("sys.argv", ["prog", "-f", str(cfg_folder), "--find_all"])  # noqa

    # Execute
    SimManager.main()

    # Expect an output folder named after the config (test_config)
    out_dir = Path("Output") / "test_config"
    assert out_dir.exists() and out_dir.is_dir()

    # Clean up created output for idempotent test runs
    # (leave removal to test runner or CI environment if needed)
