# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextLookup._shared._transform. \
    _auto_word_splitter import _auto_word_splitter




class TestAutoWordSplitter:

    # def _auto_word_splitter(
    #     _word_idx: int,
    #     _line: list[str],
    #     _KNOWN_WORDS: list[str],
    #     _verbose: bool
    # ) -> list[str]:


    @pytest.mark.parametrize('_verbose', (True, False))
    def test_accuracy(self, _verbose, capsys):

        # a garbage word - should not find a split
        _word_idx = 1
        _line = ['THE', 'WHEELZEZ', 'ON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']

        out = _auto_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        captured = capsys.readouterr().out

        assert isinstance(out, list)

        assert len(out) == 0

        # in this case, there should be no output no matter what verbose is

        assert len(captured) == 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a compound word, should find a split
        _word_idx = 1
        _line = ['THE', 'WHEELSON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']
        out = _auto_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['WHEELS', 'ON'])

        captured = capsys.readouterr().out

        if _verbose:
            assert len(captured) > 0
        else:
            assert len(captured) == 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a 3-way word, should not find a split
        _word_idx = 6
        _line = ['THE', 'WHEELS', 'ON', 'THE', 'BUS', 'GO', 'ROUNDANDROUND']
        _KNOWN_WORDS = ['THE', 'WHEELS', 'ON', 'BUS', 'GO', 'AND', 'ROUND']

        out = _auto_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        captured = capsys.readouterr().out

        assert isinstance(out, list)

        assert len(out) == 0

        # in this case, there should be no output no matter what verbose is

        assert len(captured) == 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # could be multiple splits, should only split on the first
        _word_idx = 1
        _line = ['THE', 'WHEELSON', 'THE', 'BUS', 'GO', 'ROUND', 'AND', 'ROUND']
        _KNOWN_WORDS = [
            'THE', 'WHEEL', 'WHEELS', 'SON', 'ON', 'BUS', 'GO', 'AND', 'ROUND'
        ]
        out = _auto_word_splitter(_word_idx, _line, _KNOWN_WORDS, _verbose)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['WHEEL', 'SON'])

        captured = capsys.readouterr().out

        if _verbose:
            assert len(captured) > 0
        else:
            assert len(captured) == 0


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --






