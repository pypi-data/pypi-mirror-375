# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._Lexicon._methods._check_order import \
    _check_order



class TestCheckOrder:


    @pytest.mark.parametrize('junk_lexicon',
        (-2.7, -1, 0, 1, 2.7, True, None, 'rubbish', (1,), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_blocks_junk_lexicon(self, junk_lexicon):

        with pytest.raises(AssertionError):
            _check_order(junk_lexicon)


    def test_accuracy(self):

        # good lexicon should return empty list -- -- -- --

        lexicon_ = ['a', 'an', 'as', 'at', 'ax']

        out = _check_order(lexicon_)
        assert isinstance(out, list)
        assert len(out) == 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        # duplicates should return empty list -- -- -- -- -- --

        lexicon_ = ['an', 'an', 'an', 'at', 'ax']

        out = _check_order(lexicon_)
        assert isinstance(out, list)
        assert len(out) == 0

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # out of order should populate list -- -- -- -- -- -- --

        lexicon_ = ['a', 'at', 'an', 'as', 'ax']

        out = _check_order(lexicon_)
        assert isinstance(out, list)
        assert len(out) == 3
        assert np.array_equal(out, ['at', 'an', 'as'])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --











