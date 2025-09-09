# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

# there have been problems in the past with name conflicts with the built-in
# random. this verifies built-in random can be imported
import random as py_rand

import numpy as np

from pybear.new_numpy.random._random_ import sparse

from pybear.utilities._array_sparsity import array_sparsity as arsp



@pytest.fixture
def good_shape():
    return (3,3)


@pytest.fixture
def valid_dtypes():
    return [
        np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16,
        np.uint32, np.uint64, np.float16, np.float32, np.float64, int, float
    ]


class TestImports:

    # test built-in random works
    def test_builtin_random(self):

        out = py_rand.choice(list('abcdefghijklmn'))

        assert isinstance(out, str)
        assert len(out) == 1

    # test numpy random works
    def test_numpy_random(self):

        out = np.random.choice(list('abcdefghijklmn'))

        assert isinstance(out, str)
        assert len(out) == 1


# START DATA VALIDATION TESTS ** * ** * ** * ** * ** * ** * ** * ** * **
class TestValidation:

    # dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def test_accepts_valid_dtypes(self, good_shape, valid_dtypes):
        for valid_dtype in valid_dtypes:
            sparse(0, 5, good_shape, 50, valid_dtype)


    @pytest.mark.parametrize('_dtype', (0, 'junk', [], None, {'a':1}))
    def test_rejects_invalid_dtypes(self, good_shape, _dtype):
        with pytest.raises(TypeError):
            sparse(0, 5, good_shape, 50, _dtype)
    # END dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # min  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_min', ('junk', [], None, {'a':1}))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_non_numeric(self, _min, good_shape, _dtype):
        with pytest.raises(TypeError):
            sparse(_min, 5, good_shape, 50, _dtype)


    def test_rejects_float_if_int_dtype(self, good_shape):
        with pytest.raises(ValueError):
            sparse(np.pi, 5, good_shape, 50, np.int8)


    def test_accepts_float_if_float_dtype(self, good_shape):
        sparse(np.pi, 5, good_shape, 50, np.float64)


    @pytest.mark.parametrize('_min', (float('-inf'), float('inf')))
    def test_rejects_infinity(self, _min, good_shape):
        with pytest.raises(ValueError):
            sparse(_min, 5, good_shape, 50, np.float64)
    # END min  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # max  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_max', ('junk', [], None, {'a':1}))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_non_numeric(self, _max, good_shape, _dtype):
        with pytest.raises(TypeError):
            sparse(0, _max, good_shape, 50, _dtype)


    def test_rejects_float_if_int_dtype(self, good_shape):
        with pytest.raises(ValueError):
            sparse(0, np.pi, good_shape, 50, np.int8)


    def test_accepts_float_if_float_dtype(self, good_shape):
        sparse(0, np.pi, good_shape, 50, np.float64)


    @pytest.mark.parametrize('_max', (float('-inf'), float('inf')))
    def test_rejects_infinity(self, _max, good_shape):
        with pytest.raises(ValueError):
            sparse(0, _max, good_shape, 50, np.float64)
    # END max  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # min vs max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_min', (5, 4))
    def test_when_int_rejects_min_gtoet_max(self, _min, good_shape):
        with pytest.raises(ValueError):
            sparse(_min, 4, good_shape, 50, np.int8)


    @pytest.mark.parametrize('_min', (5, 4))
    def test_when_float_accepts_min_gtoet_max(self, _min, good_shape):
        sparse(_min, 4, good_shape, 50, np.float64)
    # END min vs max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_accepts_integer(self, _dtype):
        sparse(0, 3, 5, 50, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_float(self, _dtype):
        with pytest.raises(TypeError):
            sparse(0, 3, np.pi, 50, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_accepts_good_shape(self, good_shape, _dtype):
        sparse(0, 3, good_shape, 50, _dtype)


    @pytest.mark.parametrize('shape', ((np.pi, np.pi), ([], []), ('a',1), [[]]))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_bad_shape_with_type_error(self, shape, _dtype):
        with pytest.raises(TypeError):
            sparse(0, 3, shape, 50, dtype=_dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_bad_shape_with_value_error(self, _dtype):
        with pytest.raises(ValueError):
            sparse(0, 3, (-1,-1), 50, dtype=_dtype)
    # END shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # sparsity -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_sparsity', ('junk', [], None, {'a':1}, ()))
    def test_rejects_non_numeric(self, _sparsity, good_shape, _dtype):
        with pytest.raises(TypeError):
            sparse(0, 3, good_shape, _sparsity, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_sparsity', (-10, 110))
    def test_rejects_lt_zero_gt_100(self, _sparsity, good_shape, _dtype):
        with pytest.raises(ValueError):
            sparse(0, 3, good_shape, _sparsity, _dtype)


    def test_accepts_int_min0_max1_sparsity100(self, good_shape):
        sparse(0, 1, good_shape, 100, dtype=np.int8)


    def test_accepts_float_min0_max0_sparsity100(self, good_shape):
        sparse(0, 0, good_shape, 100, dtype=np.float64)


    @pytest.mark.parametrize('_sparsity', (0, 50, 99))
    def test_rejects_impossible_conditions(self, good_shape, _sparsity):
        with pytest.raises(ValueError):
            sparse(0, 1, good_shape, _sparsity, dtype=np.int8)

        with pytest.raises(ValueError):
            sparse(0, 0, good_shape, _sparsity, dtype=np.float64)
    # END sparsity -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

# END DATA VALIDATION TESTS ** * ** * ** * ** * ** * ** * ** * ** * ** *


# START RESULT ACCURACY TESTS ** * ** * ** * ** * ** * ** * ** * ** * **

class TestAccuracy:

    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    def test_dtypes(self, good_shape, sparsity, valid_dtypes):
        for _dtype in valid_dtypes:
            output_array = sparse(0, 10, good_shape, sparsity, dtype=_dtype)

            assert output_array.dtype == _dtype


    @pytest.mark.parametrize('shape',
        (1, 3, 100, (1,), (3,), (3,3), (2, 3, 5), (2,2,3,3))
    )
    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    def test_shape(self, shape, sparsity, dtype):
        output_array = sparse(0, 10, shape, sparsity, dtype=dtype)

        try:
            tuple(shape)
            assert output_array.shape == shape
        except:
            assert output_array.shape == (shape, )


    # WHEN PASSED NULL SHAPES, RETURNS SAME OBJECT AS NUMPY
    @pytest.mark.parametrize('shape',
        (
            pytest.param(
                None,
                marks=pytest.mark.xfail(reason='known divergence from numpy')
            ),
            0, (1,0), (1,0,1), (), (()), []
        )
    )
    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    def test_null_shapes(self, shape, sparsity, dtype):
        # Notes about None 24_04_13_13_06_00: For all Nullish shape inputs except
        # None, numpy returns an ndarray, but for None returns just a number.
        # sparse returns an ndarray for all Nullish inputs. Reconciling this is
        # bigger than it is worth.
        if 'INT' in str(dtype).upper():
            np_output = np.random.randint(0, 10, shape, dtype)
        elif 'FLOAT' in str(dtype).upper():
            try:
                np_output = np.random.uniform(0, 10, shape).astype(dtype)
            except:
                np_output = dtype(np.random.uniform(0, 10, shape))
        else:
            raise ValueError(f'logic managing dtype failed')

        output = sparse(0, 10, shape, sparsity, dtype=dtype)

        if isinstance(np_output, np.ndarray):
            assert output.shape == np_output.shape
            assert output.dtype == np_output.dtype
        elif any([_ in str(type(np_output)).upper() for _ in ['INT', 'FLOAT']]):
            assert type(output) == type(np_output)
        else:
            raise ValueError(
                f'logic managing np_output type ({type(np_output)}) failed'
            )


    @pytest.mark.parametrize('shape',
        ((2,2), (2,2,2), (100,), (100,100), (10, 10, 10))
    )
    @pytest.mark.parametrize('sparsity', (0, 100))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_min,_max', ((0,10),(5,10)))
    def test_sparsity_1(self, _min, _max, shape, sparsity, dtype):

        output_array = sparse(_min, _max, shape, sparsity, dtype=dtype)

        assert arsp(output_array) == sparsity


    @pytest.mark.parametrize('shape', ((1000,1000), (100, 100, 100)))
    @pytest.mark.parametrize('sparsity', (25, 50 ,75))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_min,_max', ((0,10),(5,10)))
    def test_sparsity_2(self, _min, _max, shape, sparsity, dtype):

        output_array = sparse(_min, _max, shape, sparsity, dtype=dtype)

        assert sparsity - 0.2 <= arsp(output_array) <= sparsity + 0.2




