# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

import numbers

# there have been problems in the past with name conflicts with the built-in
# random. this verifies built-in random can be imported
import random as py_rand

import numpy as np

from pybear.new_numpy.random._random_ import choice as pb_choice



@pytest.fixture
def good_a():
    return np.arange(int(1e5), dtype=np.int32)



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


class Validation:

    # a -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('a',
        ({'a': 1, 'b': 2}, 'junk string', np.pi, 3, None, False)
    )
    def test_non_array_like(self, a):
        with pytest.raises(TypeError):
            pb_choice(a, (100,), replace=True)

    def test_bad_shape_empty(self):
        with pytest.raises(ValueError):
            pb_choice(np.array([]), (0,), replace=True)

    def test_bad_shape_2D(self):

        with pytest.raises(ValueError):
            pb_choice(
                np.arange(int(1e5), dtype=np.int32).reshape((-1, 100)),
                (100,),
                replace=True
            )

    def test_bad_shape_3D(self):
        with pytest.raises(ValueError):
            pb_choice(
                np.arange(int(1e5), dtype=np.int32).reshape((-1, 100, 100)),
                (100,),
                replace=True
            )

    def test_good_shape(self, good_a):
        assert pb_choice(good_a, (100,), replace=True).shape == (100,)
    # END a -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('shape', (np.pi, {'a':1, 'b':2}, None, False))
    def reject_not_int_or_tuple(self, shape, good_a):
        with pytest.raises(TypeError):
            pb_choice(good_a, shape, replace=True)

    @pytest.mark.parametrize('shape', ((100,), 100))
    def accepts_int_or_tuple(self, shape, good_a):
        if isinstance(shape, tuple):
            assert pb_choice(good_a, shape, replace=True).shape == shape
        elif isinstance(shape, numbers.Integral):
            assert pb_choice(good_a, shape, replace=True).shape == (shape,)
        else:
            raise Exception
    # END shape -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # replace -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('replace', ('q', np.pi, 3, []))
    def test_rejects_non_bool(self, replace, good_a):
        with pytest.raises(TypeError):
            pb_choice(good_a, (100,), replace=replace)

    @pytest.mark.parametrize('replace', (True, False))
    def test_accepts_bool(self, replace, good_a):
        pb_choice(good_a, (100,), replace=replace)
    # END replace -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # n_jobs -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def test_accepts_int(self, good_a):
        pb_choice(good_a, (100,), replace=True, n_jobs=1)

    def test_accepts_none(self, good_a):
        pb_choice(good_a, (100,), replace=True, n_jobs=None)

    def test_rejects_float(self, good_a):
        with pytest.raises(ValueError):
            pb_choice(good_a, (100,), replace=True, n_jobs=np.pi)

    @pytest.mark.parametrize('n_jobs', (0, -2, min))
    def test_rejects_bad_ints(self, good_a, n_jobs):
        with pytest.raises((TypeError, ValueError)):
            pb_choice(good_a, (100,), replace=True, n_jobs=n_jobs)

    @pytest.mark.parametrize('n_jobs', ('junk', [], {'a':1}))
    def test_rejects_non_numerics(self, good_a, n_jobs):
        with pytest.raises(TypeError):
            pb_choice(good_a, (100,), replace=True, n_jobs=n_jobs)
    # END n_jobs -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


class TestAccuracy:

    def reject_pick_too_big_when_replace_equals_false(self):
        with pytest.raises(ValueError):
            pb_choice([1, 2, 3], (10,), replace=False)


    @pytest.mark.parametrize('shape', ((100, 100), (2, 5000), (10000,)))
    @pytest.mark.parametrize('replace', (True, False))
    def test_accuracy_num(self, good_a, shape, replace):
        PULL = pb_choice(good_a, shape, replace=replace)

        assert PULL.shape == shape

        assert np.max(PULL) <= np.max(good_a)

        assert np.min(PULL) >= np.min(good_a)

        if not replace:
            assert np.max(np.unique(PULL, return_counts=True)[1]) == 1


    @pytest.mark.parametrize('shape', ((3, 3), (2, 5), (9,)))
    @pytest.mark.parametrize('replace', (True, False))
    def test_accuracy_str(self, shape, replace):

        good_str_a = np.array(list('abcdefghijlmnop'), dtype=object)

        PULL = pb_choice(good_str_a, shape, replace=replace)

        assert PULL.shape == shape

        if not replace:
            assert np.max(np.unique(PULL, return_counts=True)[1]) == 1

        for item in PULL.ravel():
            assert item in good_str_a





