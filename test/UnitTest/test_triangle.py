import numpy as np
import numpy.testing as npt
import pytest

from src.Cells.triangle import Triangle

from .test_Shered import cell, mesh, triangle

 
def test_center_point(triangle):
    expected_center = np.array(
        [
            1.0 / 3.0,
            1.0 / 3.0,
            0.0,
        ]
    )

    npt.assert_allclose(triangle.center_point, expected_center)


def test_area(triangle):
    # Area of right triangle with legs 1 and 1 is 0.5
    assert triangle.area == pytest.approx(0.5)
