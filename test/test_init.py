import pytest

import src.flow as flow


def test_Init():
    f = flow.Flow()
    f.u0(0.5, 0.5)
    assert True
