# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextSplitter._regexp_core import _regexp_core



class TestStrCore:



    @staticmethod
    @pytest.fixture(scope='module')
    def _text():
        return [
            "Double, double toil and trouble;",
            "Fire burn, and cauldron bubble.",
            "Fillet of a fenny snake",
            "In the cauldron boil and bake.",
            "Eye of newt and toe of frog,",
            "Wool of bat and tongue of dog,",
            "Adder’s fork and blindworm’s sting,",
            "Lizard’s leg and howlet’s wing,",
            "For a charm of powerful trouble,",
            "Like a hell-broth boil and bubble.",
            "Double, double toil and trouble;",
            "Fire burn, and cauldron bubble."
        ]



    # no validation

    # sep must always be None, re.compile, or list[None, re.compile]
    # because of _param_condition


    def test_sep_is_none(self, _text):

        # maxsplit is default (all)
        out = _regexp_core(_text[:2], None, None)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double, double toil and trouble;"],
            ["Fire burn, and cauldron bubble."]]
        ))

        # -- -- -- --

        # maxsplit is -1
        out = _regexp_core(_text[:2], None, -1)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double, double toil and trouble;"],
            ["Fire burn, and cauldron bubble."]]
        ))

        # END sep is None -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_sep_is_compile(self, _text):

        # maxsplit is default (all)
        out = _regexp_core(_text[:2], re.compile('[, ;]'), None)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double", "", "double", "toil", "and", "trouble", ""],
            ["Fire", "burn", "", "and", "cauldron", "bubble."]]
        ))

        # -- -- -- -- -- -- -- -- -- --

        # maxsplit is 2
        out = _regexp_core(_text[:2], re.compile(r'[\s,]'), 2)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double", "", "double toil and trouble;"],
            ["Fire", "burn", " and cauldron bubble."]]
        ))

        # -- -- -- -- -- -- -- -- -- --

        # flags is re.I
        out = _regexp_core(_text[:2], re.compile('[d]', re.I), 2)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["", "ouble, ", "ouble toil and trouble;"],
            ["Fire burn, an", " caul", "ron bubble."]]
        ))
        # END sep is re.compile -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_sep_is_tuple(self, _text):

        # maxsplit is default (all)
        out = _regexp_core(
            _text[:2],
            (re.compile(', '), re.compile('t')),
            None
        )

        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double", "double ", "oil and ", "rouble;"],
            ["Fire burn", "and cauldron bubble."]]
        ))

        # -- -- -- -- -- -- -- -- -- --

        # maxsplit is 2
        out = _regexp_core(
            _text[:2],
            (re.compile(', '), re.compile('b')),
            2
        )

        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Dou", "le", "double toil and trouble;"],
            ["Fire ", "urn", "and cauldron bubble."]]
        ))

        # -- -- -- -- -- -- -- -- -- --

        # flags is re.I
        out = _regexp_core(
            _text[:2],
            (re.compile('b', re.I), re.compile('d', re.I)),
            2
        )
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["", "ou", "le, double toil and trouble;"],
            ["Fire ", "urn, an", " cauldron bubble."]]
        ))
        # END sep is tuple -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_sep_is_list(self, _text):

        # also tests Nones apply correctly

        _seps = [None, None, re.compile(r'\s'), re.compile('[bl]')]

        # maxsplit is default (all)

        out = _regexp_core(_text[:4], _seps, None)

        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double, double toil and trouble;"],
            ["Fire burn, and cauldron bubble."],
            ["Fillet", "of", "a", "fenny", "snake"],
            ["In the cau", "dron ", "oi", " and ", "ake."]]
        ))


        # maxsplit is 2
        out = _regexp_core(_text[:4], _seps, 2)
        assert isinstance(out, list)
        for __ in out:
            assert all(map(isinstance, __, (str for _ in __)))

        assert all(map(np.array_equal, out,
            [["Double, double toil and trouble;"],
            ["Fire burn, and cauldron bubble."],
            ["Fillet", "of", "a fenny snake"],
            ["In the cau", "dron ", "oil and bake."]]
        ))
        # END sep is list -- -- -- -- -- -- -- -- -- -- -- -- -- -- --




    @pytest.mark.parametrize('sep_format', ('none', 'compile', 'tuple', 'list'))
    @pytest.mark.parametrize('_maxsplit', (-1, 0, 1))
    def test_maxsplit(self, _text, sep_format, _maxsplit):

        # test maxsplit behavior mimics re.split
        # negative anything means no splits
        # 0 means split all
        # a positive number means that many splits

        # ["Double, double toil and trouble;",
        #  "Fire burn, and cauldron bubble."]

        if sep_format == 'none':
            _sep = None
        elif sep_format == 'compile':
            _sep = re.compile(r'\s')
        elif sep_format == 'tuple':
            _sep = (re.compile(r'\s'), re.compile(r'\.'))
        elif sep_format == 'list':
            _sep = [re.compile(r'\s'), (re.compile(r'\s'), re.compile(r'\.'))]
        else:
            raise Exception


        out = _regexp_core(_text[:2], _sep, _maxsplit=_maxsplit)


        if _maxsplit < 0:
            # never splits
            assert all(map(np.array_equal, out, [[_text[0]], [_text[1]]]))
        elif _maxsplit == 0:
            if sep_format == 'none':
                # _sep = None
                assert np.array_equal(out, [[_text[0]], [_text[1]]])
            elif sep_format == 'compile':
                # _sep = re.compile(r'\s')
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double", "toil", "and", "trouble;"],
                    ["Fire", "burn,", "and", "cauldron", "bubble."]]
                ))
            elif sep_format == 'tuple':
                # _sep = (re.compile(r'\s'), re.compile(r'\.'))
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double", "toil", "and", "trouble;"],
                    ["Fire", "burn,", "and", "cauldron", "bubble", ""]]
                ))
            elif sep_format == 'list':
                # _sep = [re.compile(r'\s'), (re.compile(r'\s'), re.compile(r'\.'))]
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double", "toil", "and", "trouble;"],
                    ["Fire", "burn,", "and", "cauldron", "bubble", ""]]
                ))
        elif _maxsplit > 0:
            if sep_format == 'none':
                assert np.array_equal(out, [[_text[0]], [_text[1]]])
            elif sep_format == 'compile':
                # _sep = re.compile(r'\s')
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double toil and trouble;"],
                     ["Fire", "burn, and cauldron bubble."]]
                ))
            elif sep_format == 'tuple':
                # _sep = (re.compile(r'\s'), re.compile(r'\.'))
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double toil and trouble;"],
                    ["Fire", "burn, and cauldron bubble."]]
                ))
            elif sep_format == 'list':
                # _sep = [re.compile(r'\s'), (re.compile(r'\s'), re.compile(r'\.'))]
                assert all(map(
                    np.array_equal,
                    out,
                    [["Double,", "double toil and trouble;"],
                     ["Fire", "burn, and cauldron bubble."]]
                ))








