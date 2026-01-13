import os
import tomllib

import pytest

from src.LoadTOML import LoadTOML


def write_toml(path, content: str):
    path.write_bytes(content.encode("utf-8"))


def test_load_toml_file(
    tmp_path,
):  # TODO: test shood be short and only test/asert one thing each
    toml_path = tmp_path / "config.toml"
    toml_content = """
[settings]
name = "test"
value = 42
"""
    write_toml(toml_path, toml_content)

    cfg = LoadTOML().loadTomlFile(str(toml_path))
    assert "settings" in cfg
    assert cfg["settings"]["name"] == "test"
    assert cfg["settings"]["value"] == 42


def test_load_sim_configs_with_file(
    tmp_path,
):  # TODO: test shood be short and only test/asert one thing each
    # create a single sim config file
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
    assert sims[0]["sim"]["id"] == 1


def test_load_sim_config_with_directory(
    tmp_path,
):  # TODO: test shood be short and only test/asert one thing each
    # create a directory with multiple toml files
    d = tmp_path / "sims"
    d.mkdir()

    p = d / f"sim.toml"
    write_toml(p, "[sim]\nid = 42\n")

    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)

    assert isinstance(sims, list) and len(sims) == 1
    assert sims[0]["sim"]["id"] == 42


def test_load_sim_configs_with_directory(
    tmp_path,
):  # TODO: test shood be short and only test/asert one thing each
    # create a directory with multiple toml files
    d = tmp_path / "sims"
    d.mkdir()
    for i in range(3):
        p = d / f"sim_{i}.toml"
        write_toml(p, f"[sim]\nid = {i}\n")

    sysConfig = {"settings": {"pathToSimConfig": str(d)}}
    sims = LoadTOML().loadSimConfigs(sysConfig)
    # should have 3 configs (ordering of os.listdir is filesystem-dependent)
    assert isinstance(sims, list) and len(sims) == 3
    ids = {s["sim"]["id"] for s in sims}
    assert ids == {0, 1, 2}
