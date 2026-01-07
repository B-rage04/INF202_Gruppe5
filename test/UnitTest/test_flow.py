import math
import numpy as np
import numpy.testing as npt
import pytest

from src.flow import Flow


def test_u0_center():
    f = Flow()
    val = f.u0(f.x_star, f.y_star)
    assert val == pytest.approx(1.0)


def test_u0_far():
    f = Flow()
    val = f.u0(f.x_star + 10.0, f.y_star + 10.0)
    assert val < 1e-10


def test_v_vector():
    f = Flow()
    x, y = 0.5, 0.2
    vx, vy = f.v(x, y)
    expected_vx = y - 0.2 * x
    expected_vy = -x
    assert vx == pytest.approx(expected_vx)
    assert vy == pytest.approx(expected_vy)
