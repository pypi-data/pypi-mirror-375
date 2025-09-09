# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._transform._match_finder import \
    _match_finder

import pytest

import re

import numpy as np



class TestSlider:

    # def _match_finder(
    #     _line: list[str],
    #     _ngram: Sequence[str | re.Pattern],
    # ) -> list[int]:


    def test_accuracy_1(self):

        _line1 = ['EGG', 'SANDWICHES', 'AND', 'ICE', 'CREAM']

        _ngram1 = (re.compile('EGG'), re.compile('sandwich[es]+', re.I))

        out = _match_finder(_line1, _ngram1)

        exp = [0]

        assert np.array_equal(out, exp)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _ngram2 = (re.compile('ICE'), re.compile('CREAM'))

        out2 = _match_finder(_line1, _ngram2)

        exp2 = [3]

        assert np.array_equal(out2, exp2)


    def test_accuracy_2(self):

        _line1 = ['BIG', 'BIG', 'MONEY', 'NO', 'WHAMMY', 'BIG', 'MONEY']

        _ngram1 = (re.compile('big', re.I), re.compile('money', re.I))

        out = _match_finder(_line1, _ngram1)

        exp = [1, 5]

        assert np.array_equal(out, exp)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _ngram2 = (re.compile('NO'), re.compile('WHAMM.+', re.I))

        out2 = _match_finder(_line1, _ngram2)

        exp2 = [3]

        assert np.array_equal(out2, exp2)


    def test_ignores_empty_line(self):

        out = _match_finder([], (re.compile('NEW'), re.compile('YORK')))
        assert isinstance(out, list)
        assert len(out) == 0







