id = 1
desc = "single"
id = 1
desc = "single"
id = 1
desc = "single"
import pytest
from pathlib import Path

from src.IO.LoadTOML import LoadTOML


def write_toml(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def toml_config(tmp_path):
    p = tmp_path / "config.toml"
    content = """
[settings]
name = "test"
value = 42
"""
    write_toml(p, content)
    return p


@pytest.fixture
def sim_file_1(tmp_path):
    p = tmp_path / "sim1.toml"
    content = """
[sim]
id = 1
desc = "single"
"""
    write_toml(p, content)
    return p


@pytest.fixture
def sim_dir_1(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    p = d / "sim.toml"
    write_toml(p, "[sim]\nid = 42\n")
    return d


@pytest.fixture
def sim_dir_3(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    for i in range(3):
        p = d / f"sim_{i}.toml"
        write_toml(p, f"[sim]\nid = {i}\n")
    return d


def test_load_toml_file_has_settings(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert "settings" in cfg


def test_load_toml_file_setting_name(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert cfg["settings"]["name"] == "test"


def test_load_toml_file_setting_value(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert cfg["settings"]["value"] == 42


def test_load_sim_configs_file_returns_one(sim_file_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_configs_file_first_id_is_1(sim_file_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 1


def test_load_sim_config_directory_returns_one(sim_dir_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_config_directory_first_id_is_42(sim_dir_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 42


def test_load_sim_configs_directory_returns_three(sim_dir_3):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_3)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 3


def test_load_sim_configs_directory_ids_match(sim_dir_3):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_3)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    ids = {s["sim"]["id"] for s in sims}
    assert ids == {0, 1, 2}
