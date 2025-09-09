# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from unittest.mock import patch

import io
import numbers
from copy import deepcopy

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextLookup.TextLookup import TextLookup as TL




class TestTextLookup:



    @staticmethod
    @pytest.fixture(scope='module')
    def _kwargs():
        return {
            'update_lexicon': True,
            'skip_numbers': True,
            'auto_split': True,
            'auto_add_to_lexicon': False,
            'auto_delete': False,
            'DELETE_ALWAYS': None,
            'REPLACE_ALWAYS': None,
            'SKIP_ALWAYS': None,
            'SPLIT_ALWAYS': None,
            'remove_empty_rows': False,
            'verbose': False
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _X():
        return [
            ["ACTIVITY", "APPRECIATE", "ANIMAL", "ANTICIPATE", "BEAUTIFUL"],
            ["BENEATH", "BENEFIT", "BRINGING", "BRIGHT", "CAREFUL"],
            ["CARING", "CATCHING", "TEACOMPOST", "CELEBRATE", "CIRCUMSTANCE"],
            ["COMMON", "CREATIVITY", "CURIOUS", "DANGER", "FLOOBASTIC"],
            ["DESTINY", "DESIRE", "DIVINE", "DREAMING", "EDUCATE"],
            ["ELITE", "ENCOURAGE", "EXCITEMENT", "EXPECT", "FAITHFUL"],
            ["FANTASTIC", "FAVORITE", "FRIEND", "FRIENDLY", "QUACKTIVATE"],
            ["GATHERING", "GENEROUS", "GENERATE", "GLORIOUS", "HARMONY"],
            ["HELPFUL", "HOPEFUL", "HONESTY", "HUMANITY", "INFLUENCE"],
            ["INSIGHT", "INTEREST", "INFLUENCER", "JOYFUL", "JUDGEMENT"],
            ["KINDNESS", "KNOWLEDGE", "LEADER", "LEARNING", "LIBERATE"],
            ["LIFE", "LIGHT", "SMORFIC", "MAGNIFICIENT", "MEANING"],
            ["MEMORIES", "MIND", "MOTIVATION", "NATIONAL", "NATURE"],
            ["OPTIMISTIC", "ORDERLY", "OPPORTUNITY", "PATIENCE", "PASSION"],
            ["PEACEFUL", "PERFECT", "PERSISTENT", "PLEASURE", "POSITIVE"],
            ["POWERFUL", "PROGRESS", "PURPOSE", "QUALITY", "QUEST"],
            ["REACHING", "REALITY", "RESPECTFUL", "SINCERE", "SKILLFUL"],
            ["SPIRITUAL", "STRATEGY", "SUCCESS", "SUPPORT", "TALENT"],
            ["THOUGHTFUL", "TREMENDOUS", "UNITY", "USEFUL", "VISION"],
            ["WEALTH", "WISDOM", "WORTHY", "ZENITH", "ZESTFUL"],
            ["ABUNDANT", "ADVENTURE", "AMBITION", "ANCIENT", "ARTIST"],
            ["AWAKEN", "BELIEVE", "BLESSING", "CALM", "CAREER"],
            ["CHALLENGE", "CHARACTER", "CLARITY", "COMMIT", "COURAGE"],
            ["CREATIVE", "CURRENT", "DELIGHT", "DESTROY", "JUMBLYWUMP"],
            ["DREAMER", "ELATION", "EMPATHY", "ENERGY", "ENDEAVOR"],
            ["ENGAGE", "ENLIGHTEN", "EXPLORER", "FOCUS", "FOREVER"],
            ["FRIENDS", "GAIN", "GREATNESS", "HEROIC", "HOPE"],
            ["HORIZON", "IDEAL", "IGNITE", "INSPIRE", "JOY"],
            ["JOURNEY", "JUSTICE", "LEGACY", "LIFELESS", "LOVEABLE"],
            ["MASTER", "MYSTIC", "NOBLE", "OBSERVE", "PEACE"],
            ["PERSIST", "PLEASANT", "PROSPER", "REFLECT", "RELIABLE"],
            ["REMARKABLE", "RESOURCEFUL", "RESTORE", "SHARE", "SIMPLIFY"],
            ["SKILLED", "SOAR", "STRENGTH", "SUBLIME", "TRIUMPH"],
            ["UNITY", "VISIONARY", "WEALTHY", "WISDOM", "YOUTHFUL"],
            ["AMAZIN", "BEAUTIFULL", "CREATING", "DILIGENCE", "BLOOMTRIX"],
            ["EXPECTATION", "EXCITING", "FLEXABILITY", "FREEDOM", "GLOURY"],
            ["HARMONIOUS", "HEROISM", "INSPIRATION", "MINDFUL", "ZIGTROPE"],
            ["PERSISTACE", "PROGRESSIVE", "TRULY", "VALUEABLE", "VICTORY"],
            ["FLAPDOO", "TORTAGLOOM", "STARDUSK", "GLENSHWINK", "ZONKING"],
            ["SNORLUX", "CRUMBLEWAX", "TORTAGLOOM", "GLIMPLER", "SNIRKIFY"]
        ]


    @staticmethod
    @pytest.fixture(scope='module')
    def _exp():
        return [
            ["ACTIVITY", "APPRECIATE", "ANIMAL", "ANTICIPATE", "BEAUTIFUL"],
            ["BENEATH", "BENEFIT", "BRINGING", "BRIGHT", "CAREFUL"],
            ["CARING", "CATCHING", "TEA", "COMPOST", "CELEBRATE", "CIRCUMSTANCE"],
            ["COMMON", "CREATIVITY", "CURIOUS", "DANGER"],
            ["DESTINY", "DESIRE", "DIVINE", "DREAMING", "EDUCATE"],
            ["ELITE", "ENCOURAGE", "EXCITEMENT", "EXPECT", "FAITHFUL"],
            ["FANTASTIC", "FAVORITE", "FRIEND", "FRIENDLY", "QUACKTIVATE"],
            ["GATHERING", "GENEROUS", "GENERATE", "GLORIOUS", "HARMONY"],
            ["HELPFUL", "HOPEFUL", "HONESTY", "HUMANITY", "INFLUENCE"],
            ["INSIGHT", "INTEREST", "INFLUENCER", "JOYFUL", "JUDGEMENT"],
            ["KINDNESS", "KNOWLEDGE", "LEADER", "LEARNING", "LIBERATE"],
            ["LIFE", "LIGHT", "MAGNIFICENT", "MEANING"],
            ["MEMORIES", "MIND", "MOTIVATION", "NATIONAL", "NATURE"],
            ["OPTIMISTIC", "ORDERLY", "OPPORTUNITY", "PATIENCE", "PASSION"],
            ["PEACEFUL", "PERFECT", "PERSISTENT", "PLEASURE", "POSITIVE"],
            ["POWERFUL", "PROGRESS", "PURPOSE", "QUALITY", "QUEST"],
            ["REACHING", "REALITY", "RESPECTFUL", "SINCERE", "SKILLFUL"],
            ["SPIRITUAL", "STRATEGY", "SUCCESS", "SUPPORT", "TALENT"],
            ["THOUGHTFUL", "TREMENDOUS", "UNITY", "USEFUL", "VISION"],
            ["WEALTH", "WISDOM", "WORTHY", "ZENITH", "ZESTFUL"],
            ["ABUNDANT", "ADVENTURE", "AMBITION", "ANCIENT", "ARTIST"],
            ["AWAKEN", "BELIEVE", "BLESSING", "CALM", "CAREER"],
            ["CHALLENGE", "CHARACTER", "CLARITY", "COMMIT", "COURAGE"],
            ["CREATIVE", "CURRENT", "DELIGHT", "DESTROY"],
            ["DREAMER", "ELATION", "EMPATHY", "ENERGY", "ENDEAVOR"],
            ["ENGAGE", "ENLIGHTEN", "EXPLORER", "FOCUS", "FOREVER"],
            ["FRIENDS", "GAIN", "GREATNESS", "HEROIC", "HOPE"],
            ["HORIZON", "IDEAL", "IGNITE", "INSPIRE", "JOY"],
            ["JOURNEY", "JUSTICE", "LEGACY", "LIFELESS", "LOVEABLE"],
            ["MASTER", "MYSTIC", "NOBLE", "OBSERVE", "PEACE"],
            ["PERSIST", "PLEASANT", "PROSPER", "REFLECT", "RELIABLE"],
            ["REMARKABLE", "RESOURCEFUL", "RESTORE", "SHARE", "SIMPLIFY"],
            ["SKILLED", "SOAR", "STRENGTH", "SUBLIME", "TRIUMPH"],
            ["UNITY", "VISIONARY", "WEALTHY", "WISDOM", "YOUTHFUL"],
            ["AMAZING", "BEAUTIFUL", "CREATING", "DILIGENCE", "BLOOM", "TRIX"],
            ["EXPECTATION", "EXCITING", "FLEX", "ABILITY", "FREEDOM", "GLORY"],
            ["HARMONIOUS", "HEROISM", "INSPIRATION", "MINDFUL", "ZIG", "TROPE"],
            ["PERSIST", "ACE", "PROGRESSIVE", "TRULY", "VALUE", "ABLE", "VICTORY"],
            ["STAR", "DUSK"],
            ["SNORLUX", "CRUMBLE", "WAX"]
    ]



    def test_accuracy(self, _kwargs, _X, _exp):

        TestCls = TL(**_kwargs)

        a = f"l\nl\nl\nw\nl\nl\nl\nf\nGLORY\ny\nu\n2\nBLOOM\ny\nTRIX\n"
        b = f"y\ny\na\nf\nBEAUTIFUL\ny\nf\nAMAZING\ny\nl\nf\n"
        c = f"MAGNIFICENT\ny\nl\nw\nl\n"

        user_inputs = a + b + c
        with patch('sys.stdin', io.StringIO(user_inputs)):
            TestCls.partial_fit(_X)

        out = TestCls.transform(_X)

        for r_idx in range(len(_exp)):
            assert np.array_equal(out[r_idx], _exp[r_idx])

        nr_ = TestCls.n_rows_
        assert isinstance(nr_, numbers.Integral)
        assert nr_ == len(_X)
        del nr_

        rs_ = TestCls.row_support_
        assert isinstance(rs_, np.ndarray)
        assert all(map(isinstance, rs_, (np.bool_ for _ in rs_)))
        assert len(rs_) == len(_X)
        assert np.array_equal(rs_, [True] * len(_X))
        del rs_

        assert np.array_equal(
            TestCls.LEXICON_ADDENDUM_,
            ['TRIX']
        )

        assert TestCls.KNOWN_WORDS_[0] == 'TRIX'

        # this proves that the Lexicon singleton class attribute's
        # lexicon_ attribute is not mutated when no deepcopy and adding
        # words to KNOWN_WORDS_ (which is just a shallow copy of lexicon_)
        assert 'TRIX' not in TestCls.get_lexicon()

        assert np.array_equal(
            list(TestCls.SPLIT_ALWAYS_.keys()),
            ['CRUMBLEWAX', 'STARDUSK', 'VALUEABLE', 'PERSISTACE',
             'ZIGTROPE', 'FLEXABILITY', 'BLOOMTRIX', 'TEACOMPOST']
        )

        assert np.array_equal(
            list(TestCls.SPLIT_ALWAYS_.values()),
            [['CRUMBLE', 'WAX'], ['STAR', 'DUSK'], ['VALUE', 'ABLE'],
             ['PERSIST', 'ACE'], ['ZIG', 'TROPE'], ['FLEX', 'ABILITY'],
             ['BLOOM', 'TRIX'], ['TEA', 'COMPOST']]
        )

        assert np.array_equal(
            TestCls.DELETE_ALWAYS_,
            ['SNIRKIFY', 'GLIMPLER', 'TORTAGLOOM', 'ZONKING', 'GLENSHWINK',
             'FLAPDOO', 'JUMBLYWUMP', 'SMORFIC', 'FLOOBASTIC']
        )

        assert np.array_equal(
            list(TestCls.REPLACE_ALWAYS_.keys()),
            ['GLOURY', 'BEAUTIFULL', 'AMAZIN', 'MAGNIFICIENT']
        )

        assert np.array_equal(
            list(TestCls.REPLACE_ALWAYS_.values()),
            ['GLORY', 'BEAUTIFUL', 'AMAZING', 'MAGNIFICENT']
        )

        assert np.array_equal(
            TestCls.SKIP_ALWAYS_,
            ['SNORLUX', 'QUACKTIVATE']
        )


    def test_array_all_str_numbers(self, _kwargs):

        _new_X = np.random.randint(0, 10, (15, ))
        _new_X = np.array(list(map(str, _new_X)))
        _new_X = _new_X.reshape((5, 3))

        # skip_numbers = True
        # this proves that TextLookup does recognize str(numbers) as
        # numbers and 'skip_numbers' works
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['skip_numbers'] = True
        TestCls = TL(**_new_kwargs)
        user_inputs = f"c\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = TestCls.fit_transform(_new_X)
        # should not prompt, should just return original.
        for r_idx in range(len(out)):
            assert np.array_equal(out[r_idx], _new_X[r_idx])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # skip_numbers = False
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['skip_numbers'] = False
        _new_kwargs['update_lexicon'] = False
        TestCls = TL(**_new_kwargs)

        # just ignore all of them. we are just trying to prove out that
        # when not ignored, TextLookup sees them and prompts to handle
        # because they are not in the formal pybear lexicon.
        user_inputs = 15 * f"w\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = TestCls.fit_transform(_new_X)


    def test_multiple_partial_fits_correct_n_rows(self, _kwargs, _X):

        TestCls = TL(**_kwargs)
        TestCls.set_params(update_lexicon=False, auto_delete=True)
        TestCls.partial_fit(_X)
        TestCls.partial_fit(_X)
        assert TestCls.n_rows_ == 2 * len(_X)


    def test_various_1D_input_containers(self, _kwargs):

        _base_text = [
            "Fillet of a fenny snake",
            "In the cauldron boil and bake.",
            "Eye of newt and toe of frog,"
        ]


        TestCls = TL(**_kwargs)


        # python 1D list rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(list(_base_text))

        # python 1D tuple rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(tuple(_base_text))

        # python 1D set rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(set(_base_text))

        # np 1D rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(np.array(_base_text))

        # pd series rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(pd.Series(_base_text))

        # polars series rejected
        with pytest.raises(TypeError):
            TestCls.fit_transform(pl.Series(_base_text))


    def test_various_2D_input_containers(self, _kwargs):

        _base_text = [
            ['FILLET', 'OF', 'A', 'FENNY', 'SNAKE'],
            ['IN', 'THE', 'CAULDRON', 'BOIL', 'AND'],
            ['EYE', 'OF', 'NEWT', 'AND', 'TOE']
        ]

        _exp = [
            ['FILLET', 'OF', 'A', 'FENNY', 'SNAKE'],
            ['IN', 'THE', 'CAULDRON', 'BOIL', 'AND'],
            ['EYE', 'OF', 'NEWT', 'AND', 'TOE']
        ]


        TestCls = TL(**_kwargs)
        TestCls.set_params(update_lexicon=False, auto_delete=True)

        # python 2D list accepted
        out = TestCls.fit_transform(_base_text)
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # python 2D tuple accepted
        out = TestCls.fit_transform(tuple(map(tuple, _base_text)))
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # np 2D accepted
        out = TestCls.fit_transform(np.array(_base_text))
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # pd DataFrame accepted
        out = TestCls.fit_transform(pd.DataFrame(np.array(_base_text)))
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])

        # polars 2D accepted
        out = TestCls.fit_transform(
            pl.from_numpy(np.array(_base_text))
        )
        assert isinstance(out, list)
        for r_idx, row in enumerate(out):
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))
            assert np.array_equal(row, _exp[r_idx])










