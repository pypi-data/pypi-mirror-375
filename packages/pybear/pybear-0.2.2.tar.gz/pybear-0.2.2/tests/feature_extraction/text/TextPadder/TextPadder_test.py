# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# takes any y
# set_output
# fit_transform
# set_params
# get_params
# transform data is longer than fitted data
# test accepts 2D array-like


import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextPadder.TextPadder import TextPadder as TP



class TestTextPadder:


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

        TestCls = TP()

        TestCls.partial_fit(_text, y)

        TestCls.fit(_text, y)

        TestCls.fit_transform(_text, y)

        TestCls.score(_text, y)


    @pytest.mark.parametrize('output', (None, 'default', 'pandas', 'polars'))
    def test_set_output(self, _text, output):

        TestCls = TP()

        out = TestCls.fit_transform(_text)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (list for _ in out)))

        TestCls.set_output(transform='default')
        assert TestCls._output_transform == 'default'
        out = TestCls.fit_transform(_text)
        assert isinstance(out, np.ndarray)
        assert TestCls._output_transform == 'default'

        TestCls.set_output(transform='pandas')
        assert TestCls._output_transform == 'pandas'
        out = TestCls.fit_transform(_text)
        assert isinstance(out, pd.DataFrame)
        assert TestCls._output_transform == 'pandas'

        TestCls.set_output(transform='polars')
        assert TestCls._output_transform == 'polars'
        out = TestCls.fit_transform(_text)
        assert isinstance(out, pl.DataFrame)
        assert TestCls._output_transform == 'polars'

        TestCls.set_output(transform=None)
        assert TestCls._output_transform is None
        out = TestCls.fit_transform(_text)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (list for _ in out)))
        assert TestCls._output_transform is None


    @pytest.mark.parametrize('deep', (True, False))
    def test_get_params(self, deep):

        TestCls = TP(fill='q', n_features=10)

        out = TestCls.get_params(deep)

        assert isinstance(out, dict)
        assert 'fill' in out
        assert out['fill'] == 'q'
        assert 'n_features' in out
        assert out['n_features'] == 10


    def test_set_params(self):

        TestCls = TP(fill='q', n_features=10)

        assert isinstance(TestCls.set_params(), TP)

        TestCls.set_params(**{'fill': 'no', 'n_features': 20})

        assert TestCls.fill == 'no'
        assert TestCls.n_features == 20

        out = TestCls.get_params()

        assert isinstance(out, dict)
        assert 'fill' in out
        assert out['fill'] == 'no'
        assert 'n_features' in out
        assert out['n_features'] == 20



    def test_longer_transform_data(self, _text):

        # transform data is longer than n_features and the longest
        # example seen during fit

        # longer than longest fitted
        _new_text = [
            ['Once', 'upon', 'a', 'time,'],
            ['in', 'a', 'land', 'far,', 'far,', 'away']
        ]


        TestCls = TP(fill='', n_features=None)

        TestCls.fit(_text)

        # prove out on original data
        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)
        assert all(map(np.array_equal, out, _text))

        with pytest.raises(ValueError):
            TestCls.transform(_new_text)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # longer than n_features setting
        TestCls = TP(fill='', n_features=5)

        TestCls.fit(_text)

        # prove out on original data
        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)

        exp = [
            ['Happy', 'birthday', 'to', 'you', ''],
            ['Happy', 'birthday', 'to', 'you', ''],
            ['Happy', 'birthday,', 'dear', 'pybear', ''],
            ['Happy', 'birthday', 'to', 'you', '']
        ]

        assert all(map(np.array_equal, out, exp))

        with pytest.raises(ValueError):
            TestCls.transform(_new_text)


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # changing n_features after fitting should be OK
        TestCls = TP(fill='', n_features=None)

        TestCls.fit(_text)

        # prove out on original data
        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)
        assert all(map(np.array_equal, out, _text))


        # set new n_features
        TestCls.set_params(n_features=6)

        out = TestCls.transform(_new_text)

        exp = [
            ['Once', 'upon', 'a', 'time,', '', ''],
            ['in', 'a', 'land', 'far,', 'far,', 'away']
        ]

        assert all(map(np.array_equal, out, exp))


    def test_takes_2D_array_like(self):

        TestCls = TP(fill='-', n_features=5)

        _base_X = [list('abc'), list('abcd')]
        _ndarray = np.array([list('abcd'), list('abcd')])

        # python lists
        out = TestCls.fit_transform(_base_X)
        assert isinstance(out, list)
        for row in out:
            assert isinstance(out, list)
            assert all(map(isinstance, row, (str for _ in row)))

        # tuples of tuples
        out = TestCls.fit_transform(tuple(map(tuple, _base_X)))
        assert isinstance(out, list)
        for row in out:
            assert isinstance(out, list)
            assert all(map(isinstance, row, (str for _ in row)))

        # ndarray
        out = TestCls.fit_transform(_ndarray)
        assert isinstance(out, list)
        for row in out:
            assert isinstance(out, list)
            assert all(map(isinstance, row, (str for _ in row)))

        # pd dataframe
        out = TestCls.fit_transform(pd.DataFrame(_ndarray))
        assert isinstance(out, list)
        for row in out:
            assert isinstance(out, list)
            assert all(map(isinstance, row, (str for _ in row)))

        # polars dataframe
        out = TestCls.fit_transform(pl.from_numpy(_ndarray))
        assert isinstance(out, list)
        for row in out:
            assert isinstance(out, list)
            assert all(map(isinstance, row, (str for _ in row)))







