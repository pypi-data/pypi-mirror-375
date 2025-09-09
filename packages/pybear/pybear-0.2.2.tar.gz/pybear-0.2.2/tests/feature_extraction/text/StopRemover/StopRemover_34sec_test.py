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
# test accepts 1D & 2D array-like


import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._StopRemover.StopRemover import \
    StopRemover as SR



class TestStopRemover:


    @staticmethod
    @pytest.fixture(scope='function')
    def _kwargs():
        return {
            'match_callable': lambda x, y: x.upper() == y.upper(),
            'remove_empty_rows': True,
            'exempt': ['DOWN'],
            'supplemental': ['BOTH'],
            'n_jobs': 1
        }


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return [
            ['Two', 'roads', 'diverged', 'in', 'a', 'yellow', 'wood'],
            ['And', 'sorry', 'I', 'could', 'not', 'travel', 'both'],
            ['And', 'be', 'one', 'traveler,', 'long', 'I', 'stood'],
            ['And', 'looked', 'down', 'one', 'as', 'far', 'as', 'I', 'could'],
            ['To', 'where', 'it', 'bent', 'in', 'the', 'undergrowth;']
        ]


    @pytest.mark.parametrize('y', ([1,2], None, {1,2}, 'junk'))
    def test_takes_any_y(self, _kwargs, _text, y):

        TestCls = SR(**_kwargs)

        TestCls.partial_fit(_text, y)

        TestCls.fit(_text, y)

        TestCls.fit_transform(_text, y)

        TestCls.score(_text, y)


    @pytest.mark.parametrize('deep', (True, False))
    def test_get_params(self, _kwargs, deep):

        TestCls = SR(**_kwargs)

        out = TestCls.get_params(deep)

        assert isinstance(out, dict)
        assert 'remove_empty_rows' in out
        assert out['remove_empty_rows'] is True


    def test_set_params(self, _kwargs):

        TestCls = SR(**_kwargs)

        assert isinstance(TestCls.set_params(**{'remove_empty_rows': False}), SR)

        assert TestCls.remove_empty_rows is False

        out = TestCls.get_params()

        assert isinstance(out, dict)
        assert 'remove_empty_rows' in out
        assert out['remove_empty_rows'] is False


    def test_accuracy(self, _kwargs, _text):

        TestCls = SR(**_kwargs)

        exp = [
            ['roads', 'diverged', 'yellow', 'wood'],
            ['sorry', 'travel'],
            ['traveler,', 'stood'],
            ['looked', 'down'],
            ['bent', 'undergrowth;']
        ]

        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, exp[r_idx])


    def test_various_2D_input_containers(self, _kwargs):

        _base_text = [
            ["Fillet", "of", "a", "fenny", "snake"],
            ["In", "the", "cauldron", "boil", "and"],
            ["Eye", "of", "newt", "and", "toe"]
        ]

        _exp = [
            ["Fillet", "fenny", "snake"],
            ["cauldron", "boil"],
            ["Eye", "newt", "toe"]
        ]

        TestCls = SR(**_kwargs)


        # python 2D list accepted
        out = TestCls.transform(_base_text)
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # python 2D tuple accepted
        out = TestCls.transform(tuple(map(tuple, _base_text)))
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # np 2D accepted
        out = TestCls.transform(np.array(_base_text))
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # pd DataFrame accepted
        out = TestCls.transform(
            pd.DataFrame(np.array(_base_text))
        )
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_base_text))
        )
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])












