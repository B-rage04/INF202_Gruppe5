import copy
from test.utilitiesTests.ConfigTest import configTest
from test.utilitiesTests.MeshTest import meshTest

import numpy as np
import pytest

config = configTest()
msh = meshTest()


@pytest.fixture
def triangle():
    return copy.deepcopy(msh.cells[-1])

@pytest.fixture
def triangles():
    t0 = msh.cells[8]
    t1 = msh.cells[10]
    cells = [t0, t1]
    for cell in cells:
        cell.findNGB()
    return t0, t1



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
    pass


def testGetterPointSet(triangle):
    assert triangle.pointSet == triangle._pointSet

def testGetterPointSetNone(triangle):
    triangle._pointSet = None
    assert triangle.pointSet == triangle._pointSet


def testGetterNGB(triangle):
    assert triangle.ngb == triangle._ngb


def testGetterFlow(triangle):
    assert triangle.flow.all() == triangle._flow.all()



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


@pytest.mark.parametrize("midPoint, bool",
                         [([0.0, 0.0], True),
                          ([5.0, 0.0], False),
                          ([None, 0], False),
                          ([0, None], False)
                          ])

def testFishingCheck(triangle, midPoint, bool):
    triangle._midPoint = midPoint
    assert triangle.isFishingCheck() == bool


def test_triangle_t1_neighbor_to_t0(triangles):
    t0, t1 = triangles

    assert t1.id in t0.ngb


def test_triangle_t0_neighbor_to_t1(triangles):
    t0, t1 = triangles

    assert t0.id in t1.ngb


def test_triangle_t1_neighbor_to_t0_with_ID(triangles):
    t0, t1 = triangles

    assert t1.ngb.count(t0.id) == 1


def test_triangle_t0_neighbor_to_t1_with_ID(triangles):
    t0, t1 = triangles

    assert t0.ngb.count(t1.id) == 1
