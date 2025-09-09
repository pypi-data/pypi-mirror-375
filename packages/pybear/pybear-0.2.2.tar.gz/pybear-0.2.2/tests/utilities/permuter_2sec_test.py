# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause


import pytest

from pybear.utilities._permuter import permuter



@pytest.fixture
def fixture_a():
    return [('a','b','c'),('d','e')]

@pytest.fixture
def fixture_b():
    return [('a','b'),('c')]

@pytest.fixture
def fixture_c():
    return [('a'), ('b')]

@pytest.fixture
def fixture_d():
    return [('a'), ()]



def test_rejects_empty(fixture_d):
    with pytest.raises(ValueError):
        permuter(fixture_d)


class TestPermuter:

    def test_case_a(self, fixture_a):
        assert permuter(fixture_a) == [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)]

    def test_case_b(self, fixture_b):
        assert permuter(fixture_b) == [(0,0), (1,0)]

    def test_case_c(self, fixture_c):
        assert permuter(fixture_c) == [(0,0)]













