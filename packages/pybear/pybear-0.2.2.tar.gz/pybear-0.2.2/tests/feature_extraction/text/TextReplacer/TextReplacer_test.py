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

from pybear.feature_extraction.text._TextReplacer.TextReplacer import TextReplacer




class TestTextReplacer:


    @staticmethod
    @pytest.fixture(scope='module')
    def _words():
        return list('abcde')


    def test_no_op(self):

        # 1D
        X = list('abcde')
        TestCls = TextReplacer()
        out = TestCls.fit_transform(X)
        assert np.array_equal(out, X)

        # 2D
        X = list(map(list, 'abcde'))
        TestCls = TextReplacer()
        out = TestCls.fit_transform(X)
        assert all(map(np.array_equal, out, X))


    def test_empty_X(self):

        # 1D
        TestCls = TextReplacer(replace=(',', '.'))

        out = TestCls.transform([])

        assert isinstance(out, list)
        assert len(out) == 0

        # 2D -- returns empty 1D
        TestCls = TextReplacer(replace=(re.compile('[n-z]'), ''))

        out = TestCls.transform([[]])

        assert isinstance(out, list)
        assert len(out) == 1


    def test_flags_trump_case_sensitive(self):

        X = list('abcde')

        # literal
        TestCls = TextReplacer(
            replace=(('B', '!@#'), ('D', '^&*')),
            case_sensitive=False,
            flags=re.I
        )
        out = TestCls.fit_transform(X)
        assert np.array_equal(out, ['a', '!@#', 'c', '^&*', 'e'])

        # regex
        TestCls = TextReplacer(
            replace=((re.compile('A'), '!@#'), (re.compile('E'), '^&*')),
            case_sensitive=False,
            flags=re.I
        )
        out = TestCls.fit_transform(X)
        assert np.array_equal(out, ['!@#', 'b', 'c', 'd', '^&*'])


    def test_str_str_callable_works(self, _words):


        def crazy_callable(_str: str) -> str:

            return 'abcdefghijklmno'.find(_str.lower()) * _str


        TestCls = TextReplacer(
            replace=(re.compile('.'), crazy_callable)
        )

        out = TestCls.fit_transform(_words)

        assert np.array_equal(out, ['', 'b', 'cc', 'ddd', 'eeee'])





    def test_str_replace_1(self, _words):

        TestCls = TextReplacer(replace=('A', 'C'), case_sensitive=False)

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        assert np.array_equal(out, list('Cbcde'))


    def test_str_replace_2(self):

        _words = [['ab'], ['cd'], ['ef'], ['gh'], ['ij']]

        TestCls = TextReplacer(
            replace=[(('A', ','), ('B', '.')), None, None, None, None],
            case_sensitive=False
        )

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        for _ in out:
            assert isinstance(_, list)
            assert all(map(isinstance, _, (str for i in _)))

        assert all(map(
            np.array_equal,
            out,
            [[',.'], ['cd'], ['ef'], ['gh'], ['ij']]
        ))


    def test_re_replace_1(self, _words):

        TestCls = TextReplacer(
            replace=(re.compile("[A-C]+"), ""),
            flags=re.I
        )

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for i in out)))

        assert np.array_equal(out, ['', '', '', 'd', 'e'])


    def test_re_replace_2(self):

        _words = [['AB'], ['CD'], ['EF'], ['GH'], ['IJ']]

        TestCls = TextReplacer(
            replace=[
                None,
                ((re.compile("c"), "!@#"), (re.compile("d"), "$%^")),
                None,
                None,
                None
            ],
            flags=re.I
        )

        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        for _ in out:
            assert isinstance(_, list)
            assert all(map(isinstance, _, (str for i in _)))

        assert all(map(
            np.array_equal,
            out,
            [['AB'], ['!@#$%^'], ['EF'], ['GH'], ['IJ']]
        ))


    def test_order_of_replacement(self):

        _words = ['be', 'sure', 'to', 'drink', 'your', 'ovaltine']

        TestCls = TextReplacer(
            replace=(('rin', 'Q.Q'), ('.Q', 'c'), ('Q', 'i'))
        )

        out = TestCls.fit_transform(_words)

        assert np.array_equal(
            out,
            ['be', 'sure', 'to', 'dick', 'your', 'ovaltine']
        )


    def test_various_input_containers(self, _words):

        TestCls = TextReplacer(replace=("e", ""))


        # python list accepted
        out = TestCls.transform(_words, copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcd') + [''])

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcd') + [''])

        # python 1D set accepted
        out = TestCls.transform(set(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(sorted(out), sorted(list('abcd') + ['']))

        # np 1D accepted
        out = TestCls.transform(np.array(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcd') + [''])

        # pd series accepted
        out = TestCls.transform(pd.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcd') + [''])

        # polars series accepted
        out = TestCls.transform(pl.Series(_words), copy=True)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcd') + [''])

        # py 2D accepted
        out = TestCls.transform(
            list(map(list, _words)),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['a'], ['b'], ['c'], ['d'], ['']])

        # np 2D accepted
        out = TestCls.transform(
            np.array(_words).reshape((len(_words), -1)),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['a'], ['b'], ['c'], ['d'], ['']])

        # pd DataFrame accepted
        TestCls.transform(
            pd.DataFrame(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['a'], ['b'], ['c'], ['d'], ['']])

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_words).reshape((len(_words), -1))),
            copy=True
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [['a'], ['b'], ['c'], ['d'], ['']]
        ))








