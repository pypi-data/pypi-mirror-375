# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._validation._ngrams import \
    _val_ngrams

import re

import pytest




class TestValNGrams:


    @pytest.mark.parametrize('junk_ngrams',
        (-2.7, -1, 0, 1, 2.7, True, [0,1], {1,2}, (1,), {'A':1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_ngrams):

        with pytest.raises(TypeError):
            _val_ngrams(junk_ngrams)


    @pytest.mark.parametrize('empty_outer', ([], (), set()))
    def test_rejects_empty_outer(self, empty_outer):

        with pytest.raises(ValueError):

            _val_ngrams(empty_outer)


    def test_rejects_inner_less_than_2(self):

        with pytest.raises(ValueError):

            _val_ngrams([['Sam', 'I', 'am'], ['Egg'], ['I', 'am', 'Sam']])


    def test_accepts_good(self):

        assert _val_ngrams(None) is None

        assert _val_ngrams([['eat', 'more', 'chikn'], ['green', 'eggs']]) is None

        assert _val_ngrams(([re.compile('^[a-m]+$', re.I), 'whatever'],)) is None

        assert _val_ngrams(({'^[a-zA-Z]$', 'ICE', 'CREAM'},)) is None

        assert _val_ngrams([[re.compile('[0-9]+', re.X), re.compile('.')]]) is None







