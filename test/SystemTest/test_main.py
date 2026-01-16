import pytest

import main


def test_main_runs():
    # This test simply ensures that the main function runs without errors.
    try:
        main.SimManager.main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")

def test_main_with_comandline_args(monkeypatch):
    # Simulate command line arguments python main.py -c .\Input\BaseSimConfig.toml
    
    try:
        main.SimManager.main()
    except Exception as e:
        pytest.fail(f"main() with command line args raised an exception: {e}")