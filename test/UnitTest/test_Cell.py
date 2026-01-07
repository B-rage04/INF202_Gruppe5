import numpy as np
import numpy.testing as npt
import pytest

from .test_Shered import cell, mesh


def test_flow(cell):
    cx, cy = cell.center_point[0], cell.center_point[1]
    expected_flow = np.array(
        [
            cy - cx * 0.2,
            -cx,
        ]
    )

    npt.assert_allclose(cell.flow, expected_flow)


def test_oil(cell):
    center = cell.center_point
    reference = np.array([0.35, 0.45, 0.0])

    expected_oil = np.exp(-(np.linalg.norm(center - reference) ** 2) / 0.01)

    assert cell.oil == pytest.approx(expected_oil)
