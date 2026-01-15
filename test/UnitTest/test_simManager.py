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