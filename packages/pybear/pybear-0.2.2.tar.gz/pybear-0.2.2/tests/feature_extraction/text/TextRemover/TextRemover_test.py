# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextRemover.TextRemover import TextRemover



class TestTextRemover:


    @staticmethod
    @pytest.fixture(scope='module')
    def _words():
        return list('edcba')

    # -- -- -- -- -- -- -- -- -- -- -- --


    def test_empty_X(self):

        # 1D
        TestCls = TextRemover(remove=',')

        out = TestCls.transform([])

        assert isinstance(out, list)
        assert len(out) == 0

        # 2D -- returns empty 2D
        TestCls = TextRemover(remove=re.compile('[n-z]'))

        out = TestCls.transform([[]])

        assert isinstance(out, list)
        assert len(out) == 1
        assert len(out[0]) == 0


    def test_empty_init_does_no_op(self):

        TestCls = TextRemover()

        X = [['', ' ', 'a'], [';', ' '], ['.', ' ', ',']]

        # 2D
        out = TestCls.transform(X, copy=True)
        assert all(map(np.array_equal, out, X))

        # 1D
        out = TestCls.transform(X[0], copy=True)
        assert np.array_equal(out, X[0])


    def test_str_remove_1(self, _words):

        TestCls = TextRemover(remove=('a', "c"))

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, list('edb'))


    def test_str_remove_2(self, _words):

        TestCls = TextRemover(remove=['e', None, 'c', None, None])

        out = TestCls.transform(list(map(list, _words)), copy=True)
        assert isinstance(out, list)
        for _ in out:
            assert isinstance(_, list)
            assert all(map(isinstance, _, (str for i in _)))

        assert all(map(
            np.array_equal,
            out,
            [[], ['d'], [], ['b'], ['a']]
        ))


    def test_re_remove_1(self, _words):

        TestCls = TextRemover(remove=re.compile("[a-c]+"), flags=re.X)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for i in out)))

        assert np.array_equal(out, list('ed'))


    def test_re_remove_2(self, _words):

        TestCls = TextRemover(
            remove=[None, re.compile("D"), None, re.compile("B"), None],
            flags=[0, re.I, 0, re.I, 0]
        )

        out = TestCls.transform(list(map(list, _words)), copy=True)
        assert isinstance(out, list)
        for _ in out:
            assert isinstance(_, list)
            assert all(map(isinstance, _, (str for i in _)))

        assert all(map(
            np.array_equal,
            out,
            [['e'], [], ['c'], [], ['a']]
        ))


    @pytest.mark.parametrize('dim', (1, 2))
    @pytest.mark.parametrize('rer', (True, False))
    def test_remove_empty_rows_works(self, _words, dim, rer):

        TestCls = TextRemover(
            remove=('b', 'e'),
            remove_empty_rows=rer
        )

        if dim == 1:
            _X = list(_words)
        elif dim == 2:
            _X = list(map(list, _words))
        else:
            raise Exception

        out = TestCls.transform(_X, copy=True)

        if dim == 1 or rer is True:
            assert len(out) == len(_X) - 2
            assert np.array_equal(
                TestCls.row_support_,
                [False, True, True, False, True]
            )
        else:   # dim == 2 and rer = False
            assert len(out) == len(_X)
            assert np.array_equal(
                TestCls.row_support_,
                [True, True, True, True, True]
            )


    def test_escapes_literal_strings(self):

        TestCls = TextRemover(remove='\n\s\t')

        out = TestCls.transform(['a', '\n\s\t', 'c', 'd'], copy=True)
        assert np.array_equal(out, ['a', 'c', 'd'])


    def test_various_input_containers(self, _words):

        TestCls = TextRemover(remove="e")


        # python list accepted
        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('dcba'))

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('dcba'))

        # python 1D set accepted
        out = TestCls.transform(set(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(sorted(out), sorted(list('abcd')))

        # np 1D accepted
        out = TestCls.transform(np.array(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('dcba'))

        # pd series accepted
        out = TestCls.transform(pd.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('dcba'))

        # polars series accepted
        out = TestCls.transform(pl.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('dcba'))

        # np 2D accepted
        out = TestCls.transform(
            np.array(_words).reshape((len(_words), -1)),
            copy=True
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [[], ['d'], ['c'], ['b'], ['a']]
        ))

        # pd DataFrame accepted
        TestCls.transform(
            pd.DataFrame(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [[], ['d'], ['c'], ['b'], ['a']]
        ))

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [[], ['d'], ['c'], ['b'], ['a']]
        ))









