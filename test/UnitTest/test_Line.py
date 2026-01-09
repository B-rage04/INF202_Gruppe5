import pytest

from src.Cells.cell import Cell
from src.Cells.line import Line

 
def test_line_is_subclass():
    assert issubclass(Line, Cell)
