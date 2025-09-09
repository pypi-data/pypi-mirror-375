# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from unittest.mock import patch

import io

import numpy as np

from pybear.feature_extraction.text._TextLookup._shared._transform. \
    _manual_word_splitter import _manual_word_splitter




class TestManualWordSplitter:

    # def _manual_word_splitter(
    #     _word_idx: int,
    #     _line: list[str],
    #     _KNOWN_WORDS: list[str],
    #     _verbose: bool
    # ) -> list[str]:


    @pytest.mark.parametrize('_verbose', (True, False))
    def test_accuracy(self, _verbose, capsys):

        # a garbage word - the user should have used replace, but there is a way out
        _word_idx = 1
        _line = ['THE', 'WHEELZEZ', 'ON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']

        user_inputs = "1\nWHEELS\nY\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = _manual_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        captured = capsys.readouterr().out

        assert len(captured) > 0

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['WHEELS'])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a 2-way compound word
        _word_idx = 1
        _line = ['THE', 'WHEELSON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']

        user_inputs = "2\nWHEELS\nY\nON\nY\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = _manual_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        captured = capsys.readouterr().out

        assert len(captured) > 0

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['WHEELS', 'ON'])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a 3-way compound word
        _word_idx = 6
        _line = ['THE', 'WHEELS', 'ON', 'THE', 'BUS', 'GO', 'ROUNDANDROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']

        user_inputs = "3\nROUND\nY\nAND\nY\nROUND\nY\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = _manual_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        captured = capsys.readouterr().out

        assert len(captured) > 0

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['ROUND', 'AND', 'ROUND'])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # could be multiple splits, should only split on the first
        _word_idx = 1
        _line = ['THE', 'WHEELSON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = [
            'THE', 'WHEEL', 'WHEELS', 'SON', 'ON', 'BUS', 'GO', 'AND', 'ROUND'
        ]

        user_inputs = "2\nWHEEL\nY\nSON\nY\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = _manual_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['WHEEL', 'SON'])

        captured = capsys.readouterr().out

        assert len(captured) > 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



