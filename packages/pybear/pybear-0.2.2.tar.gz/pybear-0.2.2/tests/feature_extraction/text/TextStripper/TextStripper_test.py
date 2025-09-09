# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextStripper.TextStripper import \
    TextStripper




class TestTextStripper:


    @staticmethod
    @pytest.fixture(scope='module')
    def _words():
        return ['    AbCdE ']



    def test_empty_X(self):

        # 1D
        TestCls = TextStripper()

        out = TestCls.transform([])

        assert isinstance(out, list)
        assert len(out) == 0

        # 2D
        TestCls = TextStripper()

        out = TestCls.transform([[]])

        assert isinstance(out, list)
        assert len(out) == 1
        assert len(out[0]) == 0


    def test_accuracy(self, _words):

        TestCls = TextStripper()

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, ['AbCdE'])


    def test_various_input_containers(self, _words):

        TestCls = TextStripper()

        # python list accepted
        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])

        # python 1D set accepted
        out = TestCls.transform(set(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])

        # np 1D accepted
        out = TestCls.transform(np.array(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])

        # pd series accepted
        out = TestCls.transform(pd.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])

        # polars series accepted
        out = TestCls.transform(pl.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, ['AbCdE'])


        # py 2D accepted
        out = TestCls.transform(
            [list(_words)],
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['AbCdE']])

        # np 2D accepted
        out = TestCls.transform(
            np.array(list(_words)).reshape((len(_words), -1)),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['AbCdE']])

        # pd DataFrame accepted
        TestCls.transform(
            pd.DataFrame(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['AbCdE']])

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )

        assert isinstance(out, list)
        assert np.array_equal(out, [['AbCdE']])







