import pytest
from pathlib import Path

import src.SimManager as Manager


def test_next_run_number_nonexistent_directory():
    """When directory doesn't exist, should return 0."""
    assert Manager._next_run_number("nonexistent/path") == 0


def test_next_run_number_empty_directory(tmp_path):
    """When directory exists but has no run folders, should return 0."""
    assert Manager._next_run_number(str(tmp_path)) == 0


def test_next_run_number_with_existing_runs(tmp_path):
    """Should return max run number + 1."""
    (tmp_path / "run0").mkdir()
    (tmp_path / "run1").mkdir()
    (tmp_path / "run2").mkdir()
    assert Manager._next_run_number(str(tmp_path)) == 3


def test_next_run_number_non_sequential(tmp_path):
    """Should handle gaps in run numbers."""
    (tmp_path / "run0").mkdir()
    (tmp_path / "run5").mkdir()
    (tmp_path / "run3").mkdir()
    assert Manager._next_run_number(str(tmp_path)) == 6


def test_next_run_number_ignores_non_run_folders(tmp_path):
    """Should ignore folders that don't match run pattern."""
    (tmp_path / "run0").mkdir()
    (tmp_path / "other_folder").mkdir()
    (tmp_path / "run_old").mkdir()
    (tmp_path / "runX").mkdir()
    assert Manager._next_run_number(str(tmp_path)) == 1


def test_get_config_files_no_config_files_found_in_folder(tmp_path):
    """Should raise ValueError when no TOML files found."""
    with pytest.raises(ValueError):
        Manager._get_config_files(str(tmp_path))


def test_get_config_files_invalid_directory():
    """Should raise ValueError when given an invalid directory path."""
    with pytest.raises(ValueError):
        Manager._get_config_files("this/doenst/exist/lol")


def test_get_config_files_correct_read_toml():
    """Should return sorted list of TOML files from Defaults folder."""
    result = Manager._get_config_files("test/utilitiesTests/ConfigTest.toml")
    assert result == ["test\\utilitiesTests\\ConfigTest.toml"] 


def test_is_result_folder_positive(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "videos").mkdir()
    assert Manager._is_result_folder(tmp_path) is True

def test_is_result_folder_negative(tmp_path):
    assert Manager._is_result_folder(tmp_path) is False

def test_create_result_folder_value_error(tmp_path):
    with pytest.raises(ValueError):
        Manager._create_result_folder(tmp_path)

        
def test_create_result_folder_creates_subfolder(tmp_path):
    """Should create a subfolder inside output_dir."""
    result = Manager._create_result_folder("test_config", str(tmp_path))
    assert result == str(tmp_path / "test_config")


def test_create_result_folder_subfolder_exists(tmp_path):
    """Should actually create the folder on disk."""
    Manager._create_result_folder("test_config", str(tmp_path))
    assert (tmp_path / "test_config").exists()


def test_create_result_folder_prevents_overwrite_non_result(tmp_path):
    """Should raise ValueError if folder exists but isn't a result folder."""
    # Create a non-result folder (no images/videos subdirs)
    config_folder = tmp_path / "test_config"
    config_folder.mkdir()
    (config_folder / "some_file.txt").write_text("data")
    
    with pytest.raises(ValueError):
        Manager._create_result_folder("test_config", str(tmp_path))


def test_create_result_folder_allows_overwrite_result(tmp_path):
    """Should allow reusing existing result folders."""
    config_folder = tmp_path / "test_config"
    config_folder.mkdir()
    (config_folder / "images").mkdir()
    
    result = Manager._create_result_folder("test_config", str(tmp_path))
    assert result == str(config_folder)