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

from pybear.feature_extraction.text._TextJustifier.TextJustifier import \
    TextJustifier as TJ



class TestTextJustifier_Regex:


    @staticmethod
    @pytest.fixture(scope='function')
    def _kwargs():
        return {
            'n_chars': 20,
            'sep': re.compile(' '),
            'sep_flags': None,
            'line_break': re.compile(r'\.'),
            'line_break_flags': None,
            'backfill_sep': ' ',
            'join_2D': ' '
        }


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return [
            "Round about the cauldron go;",
            "In the poisoned entrails throw.",
            "Toad, that under cold stone",
            "Days and nights has thirty-one",
            "Sweltered venom sleeping got,",
            "Boil thou first i’ th’ charmèd pot."
        ]

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('y', ([1,2], None, {1,2}, 'junk'))
    def test_takes_any_y(self, _kwargs, _text, y):

        TestCls = TJ(**_kwargs)

        TestCls.partial_fit(_text, y)

        TestCls.fit(_text, y)

        TestCls.fit_transform(_text, y)

        TestCls.score(_text, y)


    @pytest.mark.parametrize('deep', (True, False))
    def test_get_params(self, _kwargs, deep):

        TestCls = TJ(**_kwargs)

        out = TestCls.get_params(deep)

        assert isinstance(out, dict)
        assert 'sep' in out
        assert out['sep'] == re.compile(' ')


    def test_set_params(self, _kwargs):

        TestCls = TJ(**_kwargs)

        assert isinstance(TestCls.set_params(**{'sep': re.compile(',')}), TJ)

        assert TestCls.sep == re.compile(',')

        out = TestCls.get_params()

        assert isinstance(out, dict)
        assert 'sep' in out
        assert out['sep'] == re.compile(',')


    def test_empty(self, _kwargs):

        TestCls = TJ(**_kwargs)

        assert np.array_equal(TestCls.fit_transform([]), [])

        assert np.array_equal(TestCls.fit_transform([[]]), [[]])


    def test_flags_trumps_case_sensitive(self, _kwargs, _text):

        # most of the 't's in _text are lower case. set to match against
        # 'T' but set re.I flag over case_sensitive=True. Should become
        # case-insensitive and wrap on the 't's.

        TestCls = TJ(**_kwargs)
        TestCls.set_params(
            case_sensitive=True, sep=re.compile('T'), sep_flags=re.I
        )

        _exp = [
            "Round about t",
            "he cauldron go; In t",
            "he poisoned ent",
            "rails throw.",
            "Toad, that",
            " under cold stone",
            "Days and night",
            "s has thirty-one",
            "Swelt",
            "ered venom sleeping got",
            ", Boil thou first",
            " i’ th’ charmèd pot."
        ]

        out = TestCls.fit_transform(_text)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)


    def test_does_not_crash_on_duplicate_seps_or_lbs(self, _text):

        # it shouldnt crash even with the validation for strings because
        # set() is done on Sequence sep & lb before the validation

        TestCls = TJ(
            n_chars=40,
            sep=(re.compile(' '), re.compile(','), re.compile(' '), re.compile(',')),
            line_break=(re.compile(r'\.'), re.compile(r'\.')),
            case_sensitive=True
        )

        out = TestCls.fit_transform(_text)

        _exp = [
            "Round about the cauldron go; In the ",
            "poisoned entrails throw.",
            "Toad, that under cold stone Days and ",
            "nights has thirty-one Sweltered venom ",
            "sleeping got,Boil thou first i’ th’ ",
            "charmèd pot."
        ]

        assert all(map(np.array_equal, out, _exp))


    def test_no_seps_line_breaks_returns_original(self, _text):

        # need to set small enough n_chars or TJ will backfill because
        # there are no seps/linebreaks

        TestCls = TJ(
            n_chars = 30, sep=re.compile('QXY891'),
            line_break=re.compile('MVD237')
        )

        out = TestCls.transform(_text, copy=True)

        for r_idx, line in enumerate(out):
            assert np.array_equal(line, _text[r_idx])


    def test_blocks_mixed_types(self, _text):

        _search = ['some', re.compile('thing')]

        TestCls = TJ(sep=_search)
        with pytest.raises(TypeError):
            TestCls.fit_transform(_text)


        TestCls = TJ(line_break=_search)
        with pytest.raises(TypeError):
            TestCls.fit_transform(_text)


        TestCls = TJ(sep=' ', line_break=re.compile(r'\.'))
        with pytest.raises(TypeError):
            TestCls.fit_transform(_text)


        TestCls = TJ(sep=re.compile(' '), line_break='.')
        with pytest.raises(TypeError):
            TestCls.fit_transform(_text)


    def test_accuracy(self, _kwargs, _text):

        TestCls = TJ(**_kwargs)

        out = TestCls.transform(_text, copy=True)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        exp = [
            "Round about the ",
            "cauldron go; In the ",
            "poisoned entrails ",
            "throw.",
            "Toad, that under ",
            "cold stone Days and ",
            "nights has ",
            "thirty-one",
            "Sweltered venom ",
            "sleeping got, Boil ",
            "thou first i’ th’ ",
            "charmèd pot."
        ]

        assert np.array_equal(out, exp)


    def test_various_1D_input_containers(self, _kwargs):

        _base_text = [
            "Fillet of a fenny snake",
            "In the cauldron boil and bake.",
            "Eye of newt and toe of frog,"
        ]

        _exp = [
            "Fillet of a fenny ",
            "snake In the ",
            "cauldron boil and ",
            "bake.",
            "Eye of newt and toe ",
            "of frog,"
        ]

        TestCls = TJ(**_kwargs)


        # python list accepted
        out = TestCls.transform(list(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)

        # python 1D tuple accepted
        out = TestCls.transform(tuple(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)

        # python 1D set accepted
        out = TestCls.transform(set(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        # dont bother checking for accuracy

        # np 1D accepted
        out = TestCls.transform(np.array(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)

        # pd series accepted
        out = TestCls.transform(pd.Series(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)

        # polars series accepted
        out = TestCls.transform(pl.Series(_base_text))
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, _exp)


    def test_various_2D_input_containers(self, _kwargs):

        _base_text = [
            ["Fillet", "of", "a", "fenny", "snake"],
            ["In", "the", "cauldron", "boil", "and"],
            ["Eye", "of", "newt", "and", "toe"]
        ]

        _exp = [
            ["Fillet", "of", "a", "fenny"],
            ["snake", "In", "the"],
            ["cauldron", "boil", "and"],
            ["Eye", "of", "newt", "and", "toe"]
        ]

        TestCls = TJ(**_kwargs)

        # python 2D list accepted
        out = TestCls.transform(list(map(list, _base_text)))
        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], list)
            assert all(map(isinstance, out[r_idx], (str for _ in out[r_idx])))
            assert np.array_equal(out[r_idx], _exp[r_idx])

        # python 2D tuple accepted
        out = TestCls.transform(tuple(map(tuple, _base_text)))
        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], list)
            assert all(map(isinstance, out[r_idx], (str for _ in out[r_idx])))
            assert np.array_equal(out[r_idx], _exp[r_idx])

        # np 2D accepted
        out = TestCls.transform(np.array(_base_text))
        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], list)
            assert all(map(isinstance, out[r_idx], (str for _ in out[r_idx])))
            assert np.array_equal(out[r_idx], _exp[r_idx])

        # pd DataFrame accepted
        out = TestCls.transform(
            pd.DataFrame(np.array(_base_text))
        )
        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], list)
            assert all(map(isinstance, out[r_idx], (str for _ in out[r_idx])))
            assert np.array_equal(out[r_idx], _exp[r_idx])

        # polars 2D accepted
        out = TestCls.transform(
            pl.from_numpy(np.array(_base_text))
        )
        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], list)
            assert all(map(isinstance, out[r_idx], (str for _ in out[r_idx])))
            assert np.array_equal(out[r_idx], _exp[r_idx])





