import pytest
from src.simulation import Simulation

@pytest.fixture
def read_config():
    from src.LoadTOML import LoadTOML
    configloader = LoadTOML()
    config = configloader.load_toml_file("Exsample\SimConfig\BaseSimConfig.toml")
    return config

def test_simulation_config(read_config):
    """
    Checks im the simulation collects the correct settings from the given config file.
    Uses nSteps as an example
    """
    sim = Simulation(read_config)
    assert sim.nSteps == sim.config["settings"]["nSteps"] # The simulation doesnt collect the correct settings from the config file

def test_update_oil(read_config):
    sim = Simulation(read_config)

