import sys
import pytest

import main


@pytest.mark.parametrize(
    "argv",
    [
        ["main.py"],
        ["main.py", "-c", "Defaults/input.toml"],
        ["main.py", "-c", "Input/NoVidSimConfig.toml"],
        ["main.py", "--find_all", "-f", "Input"],
    ],
)
def test_main_parametrized_runs(monkeypatch, argv):
    """Run `SimManager.main()` for several CLI permutations.

    To keep the system tests fast and independent of optional
    dependencies (OpenCV) we monkeypatch `Simulation` used by
    `SimManager` with a light-weight stub. The test asserts that
    `main()` completes without raising exceptions for each argv.
    """

    # Fast simulation stub used to avoid long runs and video creation
    class _FastSim:
        def __init__(self, config):
            self._config = config

        def run_sim(self, runNumber=None, **kwargs):
            # emulate a completed run quickly
            return None

    # Apply monkeypatches: replace Simulation in SimManager with stub
    monkeypatch.setattr(main.SimManager, "Simulation", _FastSim)

    # Ensure sys.argv is what the CLI parser expects
    monkeypatch.setattr(sys, "argv", argv)

    try:
        main.SimManager.main()
    except Exception as e:
        pytest.fail(f"SimManager.main() raised an exception for argv={argv}: {e}")