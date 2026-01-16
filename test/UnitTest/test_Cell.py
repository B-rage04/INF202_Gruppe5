import copy
from test.utilitiesTests.ConfigTest import configTest
from test.utilitiesTests.MeshTest import meshTest

import numpy as np
import pytest

config = configTest()
msh = meshTest()


@pytest.fixture()
def triangle():
    return copy.deepcopy(msh.cells[-1])


def testGetterId(triangle):
    assert triangle.id == triangle._id


def testSetterId(triangle):
    triangle._id = None
    triangle.id = 5
    assert triangle._id == 5


def testGetterCords(triangle):
    assert triangle.cords == triangle._cords


def testGetterMidPoint(triangle):
    assert triangle.midPoint.all() == triangle._midPoint.all()


def testGetterArea(triangle):
    assert triangle.area == triangle._area


def testGetterScaledNormal(triangle):  # TODO: write test
    assert True


def testPointSet(triangle):  # TODO: write test
    pass


def testGetterNGB(triangle):
    assert triangle.ngb == triangle._ngb


def testGetterFlow(triangle):
    assert triangle.flow.all() == triangle._flow.all()


def testGetterFlowNone(triangle):
    triangle._flow = None
    expextedFlow = triangle.findFlow()
    assert triangle.flow.all() == expextedFlow.all()
    

def testGetterFlowNone(triangle):
    triangle._flow = None
    expextedFlow = triangle.findFlow()
    assert triangle.flow.all() == expextedFlow.all()
    

def testSetterFLow(triangle):
    triangle.flow = [12, 2]
    assert triangle.flow.all() == triangle.flow.all()


def testGetterOil(triangle):
    assert triangle.oil == triangle._oil

def testGetterOilNone(triangle):
    triangle._oil = None
    expextedOil = triangle.findOil()
    assert triangle.oil == expextedOil

@pytest.mark.parametrize(
    "value, bool", [(0.5, True), (0.9, True), (2.1, False), (-0.3, False)]
)
def testSetterOil(triangle, value, bool):
    if bool:
        triangle.oil = value
        assert triangle._oil == triangle.oil
    else:
        pytest.raises(AssertionError)


def testFindFlow(triangle):
    cx, cy = triangle.midPoint[0], triangle.midPoint[1]
    expectedFlow = np.array([cy - cx * 0.2, -cx])
    assert triangle.flow.all() == expectedFlow.all()


def testOil(triangle):
    center = triangle.midPoint
    reference = np.array([0.35, 0.45, 0.0])
    expectedOil = np.exp(-(np.linalg.norm(center - reference) ** 2) / 0.01)
    assert triangle.oil == pytest.approx(expectedOil)


def testGetterIsFishing(triangle):
    assert triangle.isFishing == triangle._isFishing

"""
@pytest.mark.parametrize("x, y, bool",
                         [(1, 1, False),
                          (1, 1, True),])
def testFishingCheck(triangle):
    return True
"""