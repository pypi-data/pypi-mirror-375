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

from pybear.feature_extraction.text._AutoTextCleaner.AutoTextCleaner import \
    AutoTextCleaner as ATC



class TestAutoTextCleaner:


    @staticmethod
    @pytest.fixture(scope='module')
    def _words():
        return list('edcba')



    def test_empty_X(self):

        # 1D
        TestCls = ATC(remove=',')

        out = TestCls.transform([])

        assert isinstance(out, list)
        assert len(out) == 0

        # 2D -- returns empty 2D
        TestCls = ATC(replace=(re.compile('[n-z]'), ''))

        out = TestCls.transform([[]])

        assert isinstance(out, list)
        assert len(out) == 1
        assert len(out[0]) == 0


    def test_empty_init_does_no_op(self):

        TestCls = ATC()

        X = [['', ' ', 'a'], [';', ' '], ['.', ' ', ',']]

        # 2D
        out = TestCls.transform(X, copy=True)
        assert all(map(np.array_equal, out, X))

        # 1D
        out = TestCls.transform(X[0], copy=True)
        assert np.array_equal(out, X[0])


    def test_str_remove_1(self, _words):

        TestCls = ATC(remove=('a', "c"))

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, list('edb'))


    def test_str_remove_2(self, _words):

        TestCls = ATC(remove=('e', 'c'))

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

        TestCls = ATC(remove=re.compile("[a-c]+"), global_flags=re.X)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for i in out)))

        assert np.array_equal(out, list('ed'))


    def test_re_remove_2(self, _words):

        TestCls = ATC(
            remove=(re.compile("D"), re.compile("B")),
            global_flags=re.I
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

        TestCls = ATC(
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

        TestCls = ATC(remove="\n\s\t")

        out = TestCls.transform(['a', "\n\s\t", 'c', 'd'], copy=True)
        assert np.array_equal(out, ['a', 'c', 'd'])


    @pytest.mark.parametrize('justify', (None, 99))
    def test_justify_removes_row_support(self, justify):

        if justify is None:
            TestCls = ATC(normalize=True, justify=justify)
        elif justify is not None:
            with pytest.warns():
                TestCls = ATC(normalize=True, justify=justify)

        _text = [
            "We're off to see the Wizard",
            "The Wonderful Wizard of Oz",
            "We hear he is a Whiz of a Wiz",
            "If ever a Wiz there was",
            "If ever oh ever a Wiz there was",
            "The Wizard of Oz is one because",
            "Because because because because because",
            "Because of the wonderful things he does",
            "We're off to see the wizard",
            "The Wonderful Wizard of Oz"
        ]

        if justify is None:
            out = TestCls.fit_transform(_text)
            assert isinstance(out, list)
            assert isinstance(TestCls.row_support_, np.ndarray)
        elif justify is not None:
            with pytest.warns():
                out = TestCls.fit_transform(_text)
            assert isinstance(out, list)
            with pytest.raises(AttributeError):
                getattr(TestCls, 'row_support_')


    @pytest.mark.parametrize('in_dim', (1, 2))
    @pytest.mark.parametrize('out_dim', (None, 1, 2))
    def test_input_output_dim(self, _words, in_dim, out_dim):

        TestCls = ATC(
            global_flags=re.I, strip=True, normalize=True,
            ngram_merge={'ngrams':(('B', 'A'),), 'wrap':True},
            remove_empty_rows=True, return_dim=out_dim
        )

        if in_dim == 1:
            _X = [f' {char} ' for char in _words]
            # should look like [' e ', ' d ', ... ]
        elif in_dim == 2:
            _X = [[f' {char} '] for char in _words]
            # should look like [[' e '], [' d '], ... ]
        else:
            raise Exception

        _exp_1D_X = list(map(str.upper, map(str.strip, _words)))
        # do the ngram merge
        _exp_1D_X = _exp_1D_X[:-2] + ['B_A']
        # should look like ['E', 'D', 'C', 'B_A']

        _exp_2D_X = list(map(list, map(str.upper, _words)))
        _exp_2D_X = _exp_2D_X[:-2] + [['B_A']]
        # should look like [['E'], ['D'], ['C'], ['B_A']]

        out = TestCls.transform(_X)

        if in_dim == 1:
            if out_dim is None:
                assert np.array_equal(out, _exp_1D_X)
            elif out_dim == 1:
                assert np.array_equal(out, _exp_1D_X)
            elif out_dim == 2:
                assert np.array_equal(out, _exp_2D_X)
            else:
                raise Exception
        elif in_dim == 2:
            if out_dim is None:
                assert np.array_equal(out, _exp_2D_X)
            elif out_dim == 1:
                assert np.array_equal(out, _exp_1D_X)
            elif out_dim == 2:
                assert np.array_equal(out, _exp_2D_X)
            else:
                raise Exception


    def test_various_input_containers(self, _words):

        TestCls = ATC(remove="e")


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









