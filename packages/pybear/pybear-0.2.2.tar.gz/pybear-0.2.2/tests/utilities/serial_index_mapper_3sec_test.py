# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

import numpy as np

from pybear.utilities._serial_index_mapper import serial_index_mapper as sim



@pytest.fixture
def good_shape():
    return (3,3,3)


@pytest.fixture
def good_positions():
    return [1,5,11,19,25]



class TestShape:


    def test_accepts_good_shape(self, good_shape, good_positions):
        sim(good_shape, good_positions)


    @pytest.mark.parametrize('shape', (None, np.pi, {'a': 1}, 1, 'junk'))
    def test_rejects_non_tuple_non_int_shape(self, shape, good_positions):
        with pytest.raises(TypeError):
            sim(shape, good_positions)


    def test_rejects_empty_array(self, good_positions):
        with pytest.raises(ValueError):
            sim([], good_positions)


    def test_rejects_bad_shape(self, good_positions):
        with pytest.raises(ValueError):
            sim([[1,2,3]], good_positions)


    def test_rejects_floats(self, good_positions):
        with pytest.raises(ValueError):
            sim([1.2, 2.3, 3.4], good_positions)


    def test_rejects_negative(self, good_positions):
        with pytest.raises(ValueError):
            sim([-1, -2, -3,], good_positions)



class TestPositions:


    def test_test_accepts_good_positions(self, good_shape, good_positions):
        sim(good_shape, good_positions)


    @pytest.mark.parametrize('positions', (None, np.pi, {'a': 1}, 1, 'junk'))
    def test_rejects_non_tuple_non_int_positions(self, good_shape, positions):
        with pytest.raises(TypeError):
            sim(good_shape, positions)


    def test_rejects_empty_array(self, good_shape):
        with pytest.raises(ValueError):
            sim(good_shape, [])


    def test_rejects_bad_shape(self, good_shape):
        with pytest.raises(ValueError):
            sim(good_shape, [[1,2,3]])


    def test_rejects_floats(self, good_shape):
        with pytest.raises(ValueError):
            sim(good_shape, [1.2, 2.3, 3.4])


    def test_rejects_out_of_bounds_positions(self, good_shape):
        with pytest.raises(ValueError):
            sim(good_shape, [8_102_317])


    def test_rejects_negative(self, good_shape):
        with pytest.raises(ValueError):
            sim(good_shape, [-10, -15, -21])


class TestDimensionsAndAccuracy:


    def test_1D(self):
        coordinates = sim([9], [1,4,7])
        assert coordinates == [(1,), (4,), (7,)]


    def test_2D(self):
        coordinates = sim([3,3], [0, 1,2,4,8])
        assert coordinates == [(0,0), (0,1), (0,2), (1,1), (2,2)]


    def test_3D(self):
        coordinates = sim([2,2,2], [0,3,5,7])
        assert coordinates == [(0,0,0), (0,1,1), (1,0,1), (1,1,1)]


    def test_4d(self):
        coordinates = sim([2,2,2,2], [0,5,11,15])
        assert coordinates == [(0,0,0,0), (0,1,0,1), (1,0,1,1), (1,1,1,1)]






