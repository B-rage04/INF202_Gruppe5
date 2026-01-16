import os
import tomllib

import pytest

from src.IO.LoadTOML import LoadTOML


def write_toml(path, content: str):
    path.write_bytes(content.encode("utf-8"))


@pytest.fixture
def toml_config(tmp_path):
    path = tmp_path / "config.toml"
    content = """
[settings]
name = "test"
value = 42
"""
    write_toml(path, content)
    return path


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


def write_toml(path, content: str):
    path.write_bytes(content.encode("utf-8"))


def test_load_toml_file_has_settings(tmp_path):
    toml_path = tmp_path / "config.toml"
    toml_content = """
[settings]
name = "test"
value = 42
"""
    write_toml(toml_path, toml_content)
    cfg = LoadTOML().loadTomlFile(str(toml_path))
    assert "settings" in cfg


def test_load_toml_file_has_settings(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert "settings" in cfg


def test_load_toml_file_setting_name(tmp_path):
    toml_path = tmp_path / "config.toml"
    toml_content = """
[settings]
name = "test"
value = 42
"""
    write_toml(toml_path, toml_content)
    cfg = LoadTOML().loadTomlFile(str(toml_path))
    assert cfg["settings"]["name"] == "test"


def test_load_toml_file_setting_name(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert cfg["settings"]["name"] == "test"


def test_load_toml_file_setting_value(tmp_path):
    toml_path = tmp_path / "config.toml"
    toml_content = """
[settings]
name = "test"
value = 42
"""
    write_toml(toml_path, toml_content)
    cfg = LoadTOML().loadTomlFile(str(toml_path))
    assert cfg["settings"]["value"] == 42


def test_load_toml_file_setting_value(toml_config):
    cfg = LoadTOML().loadTomlFile(str(toml_config))
    assert cfg["settings"]["value"] == 42


def test_load_sim_configs_with_file_0(
    tmp_path,
):

    sim_file = tmp_path / "sim1.toml"
    sim_content = """
[sim]
id = 1
desc = "single"
"""
    write_toml(sim_file, sim_content)

    sysConfig = {"settings": {"pathToSimConfig": str(sim_file)}}

    assert LoadTOML().loadSimConfigs(sysConfig) is not None


def test_load_sim_configs_file_returns_one_1(tmp_path):
    sim_file = tmp_path / "sim1.toml"
    sim_content = """
[sim]
id = 1
desc = "single"
"""
    write_toml(sim_file, sim_content)
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_configs_file_returns_one_2(sim_file_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_configs_file_first_id_is_1_1(tmp_path):
    sim_file = tmp_path / "sim1.toml"
    sim_content = """
[sim]
id = 1
desc = "single"
"""
    write_toml(sim_file, sim_content)
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 1


def test_load_sim_configs_file_first_id_is_1_2(sim_file_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_file_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 1


def test_load_sim_config_with_directory(
    tmp_path,
):
    d = tmp_path / "sims"
    d.mkdir()

    p = d / f"sim.toml"
    write_toml(p, "[sim]\nid = 42\n")

    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    assert LoadTOML().loadSimConfigs(sysConfig) is not None


def test_load_sim_config_directory_returns_one_1(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    p = d / f"sim.toml"
    write_toml(p, "[sim]\nid = 42\n")
    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_config_directory_returns_one_2(sim_dir_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 1


def test_load_sim_config_directory_first_id_is_42_1(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    p = d / f"sim.toml"
    write_toml(p, "[sim]\nid = 42\n")
    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 42


def test_load_sim_config_directory_first_id_is_42_2(sim_dir_1):
    sysConfig = {"settings": {"pathToSimConfig": str(sim_dir_1)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert sims[0]["sim"]["id"] == 42


def test_load_sim_configs_with_directory(
    tmp_path,
):
    d = tmp_path / "sims"
    d.mkdir()
    for i in range(3):
        p = d / f"sim_{i}.toml"
        write_toml(p, f"[sim]\nid = {i}\n")


def test_load_sim_configs_directory_returns_three(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    for i in range(3):
        p = d / f"sim_{i}.toml"
        write_toml(p, f"[sim]\nid = {i}\n")

    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    assert isinstance(sims, list) and len(sims) == 3


def test_load_sim_configs_directory_ids_match(tmp_path):
    d = tmp_path / "sims"
    d.mkdir()
    for i in range(3):
        p = d / f"sim_{i}.toml"
        write_toml(p, f"[sim]\nid = {i}\n")
