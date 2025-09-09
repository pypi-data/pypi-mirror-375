# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# takes any y
# fit_transform
# set_params
# get_params
# transform data is longer than fitted data
# test accepts 2D array-like


import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextJoiner.TextJoiner import TextJoiner as TJ



class TestTextJoiner:


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return [
            ['Happy', 'birthday', 'to', 'you'],
            ['Happy', 'birthday', 'to', 'you'],
            ['Happy', 'birthday,', 'dear', 'pybear'],
            ['Happy', 'birthday', 'to', 'you']
        ]


    @pytest.mark.parametrize('y', ([1,2], None, {1,2}, 'junk'))
    def test_takes_any_y(self, _text, y):

        TestCls = TJ()

        TestCls.partial_fit(_text, y)

        TestCls.fit(_text, y)

        TestCls.fit_transform(_text, y)

        TestCls.score(_text, y)


    @pytest.mark.parametrize('deep', (True, False))
    def test_get_params(self, deep):

        TestCls = TJ(sep='q')

        out = TestCls.get_params(deep)

        assert isinstance(out, dict)
        assert 'sep' in out
        assert out['sep'] == 'q'


    def test_set_params(self):

        TestCls = TJ(sep='q')

        assert isinstance(TestCls.set_params(**{'sep': 'no'}), TJ)

        assert TestCls.sep == 'no'

        out = TestCls.get_params()

        assert isinstance(out, dict)
        assert 'sep' in out
        assert out['sep'] == 'no'


    def test_empty(self):

        TestCls = TJ()

        assert np.array_equal(TestCls.fit_transform([]), [])

        assert np.array_equal(TestCls.fit_transform([[]]), [''])


    def test_accuracy(self, _text):

        TestCls = TJ(sep='_')

        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        exp = [
            'Happy_birthday_to_you',
            'Happy_birthday_to_you',
            'Happy_birthday,_dear_pybear',
            'Happy_birthday_to_you'
        ]

        assert all(map(np.array_equal, out, exp))


    def test_takes_2D_array_like(self):

        TestCls = TJ(sep='-')

        _base_X = [list('abc'), list('abcd')]
        _ndarray_ragged = np.array([list('abc'), list('abcd')], dtype = object)
        _ndarray = np.array([list('abcd'), list('abcd')])

        # python lists
        TestCls.fit_transform(_base_X)

        # tuples of tuples
        TestCls.fit_transform(tuple(map(tuple, _base_X)))

        # ndarray ragged
        # after ver0.2.1 overhaul of _map_X_to_list, it now raises a
        # error via numpy in for inhomogenous shape
        with pytest.raises(Exception):
            TestCls.fit_transform(_ndarray_ragged)

        # ndarray
        TestCls.fit_transform(_ndarray)

        # pd dataframe
        TestCls.fit_transform(pd.DataFrame(_ndarray))

        # polars dataframe
        TestCls.fit_transform(pl.from_numpy(_ndarray))






