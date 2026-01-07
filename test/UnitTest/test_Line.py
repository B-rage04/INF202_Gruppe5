import pytest

from src.Cells.line import Line
from src.Cells.cell import Cell


def test_line_is_subclass():
    assert issubclass(Line, Cell)
