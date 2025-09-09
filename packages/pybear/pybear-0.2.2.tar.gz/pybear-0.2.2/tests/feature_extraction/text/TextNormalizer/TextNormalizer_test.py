# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextNormalizer.TextNormalizer import \
    TextNormalizer



class TestTextNormalizer:


    @staticmethod
    @pytest.fixture(scope='module')
    def _words():
        return list('AbCdE')



    def test_empty_X(self):

        # 1D
        TestCls = TextNormalizer()

        out = TestCls.transform([])

        assert isinstance(out, list)
        assert len(out) == 0

        # 2D
        TestCls = TextNormalizer()

        out = TestCls.transform([[]])

        assert isinstance(out, list)
        assert len(out) == 1
        assert len(out[0]) == 0


    def test_no_op(self, _words):

        TestCls = TextNormalizer(upper=None)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, list('AbCdE'))


    def test_upper(self, _words):

        TestCls = TextNormalizer(upper=True)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, list('ABCDE'))


    def test_lower(self, _words):

        TestCls = TextNormalizer(upper=False)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)

        assert np.array_equal(out, list('abcde'))


    def test_various_input_containers(self, _words):

        TestCls = TextNormalizer(upper=True)


        # python list accepted
        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('ABCDE'))

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('ABCDE'))

        # python 1D set accepted
        out = TestCls.transform(set(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(sorted(out), sorted(list('ABCDE')))

        # np 1D accepted
        out = TestCls.transform(np.array(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('ABCDE'))

        # pd series accepted
        out = TestCls.transform(pd.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('ABCDE'))

        # polars series accepted
        out = TestCls.transform(pl.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('ABCDE'))

        # np 2D accepted
        out = TestCls.transform(
            np.array(_words).reshape((len(_words), -1)),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['A'], ['B'], ['C'], ['D'], ['E']])

        # pd DataFrame accepted
        TestCls.transform(
            pd.DataFrame(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['A'], ['B'], ['C'], ['D'], ['E']])

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_words).reshape((len(_words), -1)),),
            copy=True
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [['A'], ['B'], ['C'], ['D'], ['E']]
        ))








