# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers
from copy import deepcopy

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._NGramMerger.NGramMerger import \
    NGramMerger as NGM



class TestNGramMerger:



    @staticmethod
    @pytest.fixture(scope='module')
    def _kwargs():
        return {
            'ngrams': None,   # set this later
            'ngcallable': None,
            'sep': None,
            'wrap': False,
            'remove_empty_rows': False
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _X():
        return [
            ['I', 'ALREADY', 'TOLD', 'YA', 'I', 'GOT', 'A', 'MAN'],
            ["WHAT'S", 'YOUR', 'MAN', 'GOT', 'TO', 'DO', 'WITH', 'ME'],
            ['I', 'GOT', 'A', 'MAN'],
            ["I'M", 'NOT', "TRYIN'", 'TO', 'HEAR', 'THAT', 'SEE'],
            ['I', 'GOT', 'A', 'MAN'],
            ["WHAT'S", 'YOUR', 'MAN', 'GOT', 'TO', 'DO', 'WITH', 'ME'],
            ['I', 'GOT', 'A', 'MAN'],
            ["I'M", 'NOT', "TRYIN'", 'TO', 'HEAR', 'THAT']
        ]


    @staticmethod
    @pytest.fixture(scope='module')
    def exp():
        return [
            ['I', 'ALREADY', 'TOLD', 'YA', 'I_GOT_A_MAN'],
            ["WHAT'S_YOUR_MAN_GOT_TO_DO_WITH_ME"],
            ['I_GOT_A_MAN'],
            ["I'M_NOT_TRYIN'_TO_HEAR_THAT", 'SEE'],
            ['I_GOT_A_MAN'],
            ["WHAT'S_YOUR_MAN_GOT_TO_DO_WITH_ME"],
            ['I_GOT_A_MAN'],
            ["I'M_NOT_TRYIN'_TO_HEAR_THAT"]
    ]

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_no_op(self, _X):

        TestCls = NGM()

        out = TestCls.fit_transform(_X)

        assert all(map(
            np.array_equal,
            out,
            _X
        ))


    @pytest.mark.parametrize('_ngrams',
        ([('rAnDoM', 'TrAsH'), ('junk', 'rubbish')], None)
    )
    @pytest.mark.parametrize('_wrap', (True, False))
    @pytest.mark.parametrize('_remove_empty_rows', (True, False))
    def test_deletes_lines_given_empty(
        self, _kwargs, _X, _ngrams, _wrap, _remove_empty_rows
    ):

        # test always deletes empty lines in given data when r.e.r. is True,
        # even when ngrams is None

        _wip_X = deepcopy(_X)
        _wip_X[0] = []

        TestCls = NGM(**_kwargs)
        TestCls.set_params(remove_empty_rows=True)

        out = TestCls.fit_transform(_wip_X)

        if _remove_empty_rows:
            assert len(out) == len(_wip_X) - 1


    def test_accuracy(self, _kwargs, _X, exp):

        TestCls = NGM(**_kwargs)
        TestCls.set_params(ngrams= \
            (('I', 'GOT', 'A', 'MAN'),
            ("I'M", 'NOT', "TRYIN'", 'TO', 'HEAR', 'THAT'),
            ("WHAT'S", 'YOUR', 'MAN', 'GOT', 'TO', 'DO', 'WITH', 'ME'))
        )


        out = TestCls.transform(_X)

        for r_idx in range(len(exp)):
            assert np.array_equal(out[r_idx], exp[r_idx])

        nr_ = TestCls.n_rows_
        assert isinstance(nr_, numbers.Integral)
        assert nr_ == len(_X)

        rs_ = TestCls.row_support_
        assert isinstance(rs_, np.ndarray)
        assert all(map(isinstance, rs_, (np.bool_ for _ in rs_)))
        assert len(rs_) == len(_X)
        assert np.array_equal(rs_, [True] * len(_X))


    def test_escapes_literal_strings(self, _kwargs):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['ngrams'] = (('^123$', r'\s\t\n'),)
        _new_kwargs['sep'] = '_@_'

        out = NGM(**_new_kwargs).transform([['ONE', '^123$', r'\s\t\n']])

        assert np.array_equal(out, [['ONE', r'^123$_@_\s\t\n']])


    def test_various_1D_input_containers(self, _kwargs):

        _base_text = [
            "Fillet of a fenny snake",
            "In the cauldron boil and bake.",
            "Eye of newt and toe of frog,"
        ]


        TestCls = NGM(**_kwargs)
        TestCls.set_params(ngrams=[['I', 'AM', 'THE', 'WALRUS', 'COOCOOCACHOO']])

        # python 1D list rejected
        with pytest.raises(TypeError):
            TestCls.transform(list(_base_text))

        # python 1D tuple rejected
        with pytest.raises(TypeError):
            TestCls.transform(tuple(_base_text))

        # python 1D set rejected
        with pytest.raises(TypeError):
            TestCls.transform(set(_base_text))

        # np 1D rejected
        with pytest.raises(TypeError):
            TestCls.transform(np.array(_base_text))

        # pd series rejected
        with pytest.raises(TypeError):
            TestCls.transform(pd.Series(_base_text))

        # polars series rejected
        with pytest.raises(TypeError):
            TestCls.transform(pl.Series(_base_text))


    def test_various_2D_input_containers(self, _kwargs):

        _base_text = [
            ["Fillet", "of", "a", "fenny", "snake"],
            ["In", "the", "cauldron", "boil", "and"],
            ["Eye", "of", "newt", "and", "toe"]
        ]

        _exp = [
            ["Fillet", "of", "a", "fenny", "snake"],
            ["In", "the", "cauldron", "boil", "and"],
            ["Eye", "of", "newt", "and", "toe"]
        ]


        TestCls = NGM(**_kwargs)
        TestCls.set_params(ngrams=[['DRINK', 'YOUR', 'OVALTINE']])

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
        out = TestCls.transform(pd.DataFrame(np.array(_base_text)))
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






