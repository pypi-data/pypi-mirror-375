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

from pybear.new_numpy.random._random_ import Sparse

from pybear.utilities._array_sparsity import array_sparsity as arsp



@pytest.fixture
def good_shape():
    return (py_rand.choice(range(3, 10)), py_rand.choice(range(3, 10)))

@pytest.fixture
def allowed_engines():
    return ['choice', 'filter', 'serialized', 'iterative', 'default']

@pytest.fixture
def engine():
    return 'default'

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
class Validation:


    # min -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_min', ('junk', [], None, {'a':1}))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_non_numeric(self, _min, good_shape, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(_min, 5, good_shape, 50, engine, _dtype)


    def test_rejects_float_if_int_dtype(self, good_shape, engine):
        with pytest.raises(ValueError):
            Sparse(np.pi, 5, good_shape, 50, engine, np.int8)


    def test_accepts_float_if_float_dtype(self, good_shape, engine):
        Sparse(np.pi, 5, good_shape, 50, engine, np.float64)

    @pytest.mark.parametrize('_min', (float('-inf'), float('inf')))
    def test_rejects_infinity(self, _min, good_shape, engine):
        with pytest.raises(ValueError):
            Sparse(_min, 5, good_shape, 50, engine, np.float64)
    # END min -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_max', ('junk', [], None, {'a':1}))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_non_numeric(self, _max, good_shape, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(0, _max, good_shape, 50, engine, _dtype)


    def test_rejects_float_if_int_dtype(self, good_shape, engine):
        with pytest.raises(ValueError):
            Sparse(0, np.pi, good_shape, 50, engine, np.int8)


    def test_accepts_float_if_float_dtype(self, good_shape, engine):
        Sparse(0, np.pi, good_shape, 50, engine, np.float64)


    @pytest.mark.parametrize('_max', (float('-inf'), float('inf')))
    def test_rejects_infinity(self, _max, good_shape, engine):
        with pytest.raises(ValueError):
            Sparse(0, _max, good_shape, 50, engine, np.float64)
    # END max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # min vs max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_min', (5, 4))
    def test_when_int_rejects_min_gtoet_max(self, _min, good_shape, engine):
        with pytest.raises(ValueError):
            Sparse(_min, 4, good_shape, 50, engine, np.int8)


    @pytest.mark.parametrize('_min', (5, 4))
    def test_when_float_accepts_min_gtoet_max(self, _min, good_shape, engine):
        Sparse(_min, 4, good_shape, 50, engine, np.float64)
    # END min vs max -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_accepts_integer(self, engine, _dtype):
        Sparse(0, 3, 5, 50, engine, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_float(self, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(0, 3, np.pi, 50, engine, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_accepts_good_shape(self, good_shape, engine, _dtype):
        Sparse(0, 3, good_shape, 50, engine, _dtype)


    @pytest.mark.parametrize('shape', ((np.pi, np.pi), ([], []), ('a',1), [[]]))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_bad_shape_with_type_error(self, shape, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(0, 3, shape, 50, engine, dtype=_dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_rejects_bad_shape_with_value_error(self, engine, _dtype):
        with pytest.raises(ValueError):
            Sparse(0, 3, (-1,-1), 50, engine, dtype=_dtype)
    # END shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # sparsity -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_sparsity', ('junk', [], None, {'a':1}, ()))
    def test_rejects_non_numeric(self, _sparsity, good_shape, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(0, 3, good_shape, _sparsity, engine, _dtype)


    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    @pytest.mark.parametrize('_sparsity', (-10, 110))
    def test_rejects_lt_zero_gt_100(self, _sparsity, good_shape, engine, _dtype):
        with pytest.raises(ValueError):
            Sparse(0, 3, good_shape, _sparsity, engine, _dtype)


    def test_accepts_int_min0_max1_sparsity100(self, good_shape, engine):
        Sparse(0, 1, good_shape, 100, engine, dtype=np.int8)


    def test_accepts_float_min0_max0_sparsity100(self, good_shape, engine):
        Sparse(0, 0, good_shape, 100, engine, dtype=np.float64)


    @pytest.mark.parametrize('_sparsity', (0, 50, 99))
    def test_rejects_impossible_conditions(self, good_shape, _sparsity, engine):
        with pytest.raises(ValueError):
            Sparse(0, 1, good_shape, _sparsity, engine, dtype=np.int8)

        with pytest.raises(ValueError):
            Sparse(0, 0, good_shape, _sparsity, engine, dtype=np.float64)
    # END sparsity -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # engine -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_engine', (0, np.pi, None, True, [], {'a', 1}))
    def test_rejects_non_string(self, good_shape, _engine):
        with pytest.raises(TypeError):
            Sparse(0, 10, good_shape, 50, engine=_engine, dtype=np.uint8)


    @pytest.mark.parametrize('_engine', ('junk', 'diesel', 'otto', 'sterling'))
    def test_rejects_disallowed_strings(self, good_shape, _engine):
        with pytest.raises(ValueError):
            Sparse(0, 10, good_shape, 50, engine=_engine, dtype=np.uint8)


    def test_accepts_allowed_strings_case_insensitive(
        self, good_shape, allowed_engines
    ):
        for _engine in allowed_engines:
            Sparse(0, 10, good_shape, 50, engine=_engine, dtype=np.uint8)

        for _engine in allowed_engines:
            Sparse(0, 10, good_shape, 50, engine=_engine.upper(),dtype=np.uint8)
    # END engine -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def test_accepts_valid_dtypes(self, good_shape, engine, valid_dtypes):
        for valid_dtype in valid_dtypes:
            Sparse(0, 5, good_shape, 50, engine, valid_dtype)


    @pytest.mark.parametrize('_dtype', (0, 'junk', [], None, {'a':1}))
    def test_rejects_invalid_dtypes(self, good_shape, engine, _dtype):
        with pytest.raises(TypeError):
            Sparse(0, 5, good_shape, 50, engine, _dtype)
    # END dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

# END DATA VALIDATION TESTS ** * ** * ** * ** * ** * ** * ** * ** * ** *


# START RESULT ACCURACY TESTS ** * ** * ** * ** * ** * ** * ** * ** * **

class TestReturnsNDArray:

    @pytest.mark.parametrize('engine',
        ('choice', 'filter', 'serialized', 'iterative', 'default')
    )
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_access_SPARSE_ARRAY(self, good_shape, engine, _dtype):

        sparse_instance = Sparse(0, 10, good_shape, 50, engine, _dtype)

        assert isinstance(sparse_instance.sparse_array_, np.ndarray)


class TestReturnsCorrectDtypes:

    @pytest.mark.parametrize('engine',
        ('choice', 'filter', 'serialized', 'iterative', 'default')
    )
    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    def test_dtypes(self, good_shape, sparsity, engine, valid_dtypes):

        for _dtype in valid_dtypes:
            output_array = Sparse(
                0, 10, good_shape, sparsity, engine=engine, dtype=_dtype
            ).sparse_array_

            assert output_array.dtype == _dtype


class TestReturnsCorrectShapes_NonNull:

    @pytest.mark.parametrize('engine',
        ('choice', 'filter', 'serialized', 'iterative', 'default')
    )
    @pytest.mark.parametrize('shape',
        (
             1, 3, 100,
             (1,), (3,), (3, 3), (2, 3, 5), (2, 2, 3, 3)
        )
    )
    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    def test_non_null_vs_np(self, engine, shape, sparsity, dtype):
        output_array = Sparse(
            0, 10, shape, sparsity, engine=engine, dtype=dtype
        ).sparse_array_

        try:
            tuple(shape)
            assert output_array.shape == shape
        except:
            assert output_array.shape == (shape, )


# WHEN PASSED NULL SHAPES, RETURNS SAME OBJECT AS NUMPY
class TestNullShapesReturnsMatchNumpy:

    # Notes about None 24_04_13_13_06_00: For all Nullish shape inputs
    # except None, numpy returns an ndarray, but for None returns just a
    # number. Sparse returns an ndarray for all Nullish inputs. Reconciling
    # this is bigger than it is worth.

    @pytest.mark.parametrize('engine',
        ('choice', 'filter', 'serialized', 'iterative', 'default')
    )
    @pytest.mark.parametrize('shape',
        (
            pytest.param(None, marks=pytest.mark.xfail(reason='known divergence from numpy')),
            0, (1, 0), (1, 0, 1), (), (()), []
        )
    )
    @pytest.mark.parametrize('sparsity', (0, 50, 100))
    @pytest.mark.parametrize('dtype', (np.int8, np.float64))
    def test_null(self, engine, shape, sparsity, dtype):

        if 'INT' in str(dtype).upper():
            np_output = np.random.randint(0, 10, shape, dtype)
        elif 'FLOAT' in str(dtype).upper():
            np_output = np.random.uniform(0, 10, shape).astype(dtype)
        else:
            raise ValueError(f'logic managing dtype failed')

        output = Sparse(
            0, 10, shape, sparsity, engine=engine, dtype=dtype
        ).sparse_array_

        assert output.shape == np_output.shape
        assert output.dtype == np_output.dtype


@pytest.mark.parametrize('engine',
    ('choice', 'filter', 'serialized', 'iterative', 'default')
)
@pytest.mark.parametrize('shape', ((2,2), (2,2,2), (100,), (100,100), (10, 10, 10)))
@pytest.mark.parametrize('sparsity', (0, 100))
@pytest.mark.parametrize('dtype', (np.int8, np.float64))
@pytest.mark.parametrize('_min,_max', ((0,10),(5,10)))
class TestReturnsCorrectSparsity_0_100_AlwaysExact:


    def test_sparsity(self, _min, _max, shape, sparsity, engine, dtype):
        output_array = Sparse(
            _min, _max, shape, sparsity, engine=engine, dtype=dtype
        ).sparse_array_

        assert arsp(output_array) == sparsity


@pytest.mark.parametrize('shape', ((100,), (10,10), (10, 10, 10)))
@pytest.mark.parametrize('sparsity', (25, 50 ,75))
@pytest.mark.parametrize('dtype', (np.int8, np.float64))
@pytest.mark.parametrize('_min,_max', ((0, 10),(5,10)))
class TestReturnsCorrectSparsity_SerializedIterativeAlwaysExact:

    def test_serialized(self, _min, _max, shape, sparsity, dtype):
        output_array = Sparse(
            _min, _max, shape, sparsity, engine='serialized', dtype=dtype
        ).sparse_array_

        assert arsp(output_array) == sparsity


    def test_iterative(self, _min, _max, shape, sparsity, dtype):
        output_array = Sparse(
            _min, _max, shape, sparsity, engine='iterative', dtype=dtype
        ).sparse_array_

        assert arsp(output_array) == sparsity


@pytest.mark.parametrize('shape', ((1000,1000), (100, 100, 100)))
@pytest.mark.parametrize('sparsity', (25, 50 ,75))
@pytest.mark.parametrize('dtype', (np.int8, np.float64))
@pytest.mark.parametrize('_min,_max', ((0,10),(5,10)))
class TestReturnsCorrectSparsity_ChoiceFilterClose:

    def test_choice(self, _min, _max, shape, sparsity, dtype):
        output_array = Sparse(
            _min, _max, shape, sparsity, engine='choice', dtype=dtype
        ).sparse_array_

        assert sparsity - 0.2 <= arsp(output_array) <= sparsity + 0.2


    def test_filter(self, _min, _max, shape, sparsity, dtype):
        output_array = Sparse(
            _min, _max, shape, sparsity, engine='filter', dtype=dtype
        ).sparse_array_

        assert sparsity - 0.2 <= arsp(output_array) <= sparsity + 0.2


class TestDefaultReturnsCorrectResultsForBothSizeRegimes:

    # DTYPE
    @pytest.mark.parametrize('shape', ((10,10), (1100,1100)))
    def test_dtype(self, shape, valid_dtypes):
        for _dtype in valid_dtypes:
            output_array = Sparse(
                0, 10, shape, 50, engine='default', dtype=_dtype
            ).sparse_array_

            assert output_array.dtype == _dtype


    # SHAPE NON-NULL
    @pytest.mark.parametrize('shape', (100, (10, 10), (1100, 1100)))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_shape_non_null(self, shape, _dtype):
        output_array = Sparse(
            0, 10, shape, 50, engine='default', dtype=_dtype
        ).sparse_array_

        try:
            tuple(shape)
            assert output_array.shape == shape
        except:
            assert output_array.shape == (shape,)


    # CORRECT SPARSITY
    @pytest.mark.parametrize('shape', ((100, 100), (1100,1100)))
    @pytest.mark.parametrize('sparsity', (0, 100))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_sparsity_0_100_always_exact(self, shape, sparsity, _dtype):
        output_array = Sparse(
            0, 10, shape, sparsity, engine='default', dtype=_dtype
        ).sparse_array_

        assert arsp(output_array) == sparsity


    @pytest.mark.parametrize('sparsity', (25, 75))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_sparsity_iterative_always_exact(self, sparsity, _dtype):
        output_array = Sparse(
            0, 10, (100, 100), sparsity, engine='default', dtype=_dtype
        ).sparse_array_

        assert arsp(output_array) == sparsity


    @pytest.mark.parametrize('sparsity', (25, 75))
    @pytest.mark.parametrize('_dtype', (np.int8, np.float64))
    def test_sparsity_filter_close(self, sparsity, _dtype):
        output_array = Sparse(
            0, 10, (1100, 1100), sparsity, engine='default', dtype=_dtype
        ).sparse_array_

        assert sparsity - 0.2 <= arsp(output_array) <= sparsity + 0.2





