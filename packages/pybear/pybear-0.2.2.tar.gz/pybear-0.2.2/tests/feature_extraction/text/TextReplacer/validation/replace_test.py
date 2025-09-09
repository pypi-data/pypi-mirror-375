# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextReplacer._validation._replace \
    import _val_replace



class TestValReplace:


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return np.random.choice(list('abcde'), (10, ), replace=True)


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_replace',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_replace(self, _text, junk_replace):
        # could be None, tuple, list
        with pytest.raises(TypeError):
            _val_replace(junk_replace, len(_text))


    def test_rejects_bad_len_replace(self, _text):

        # too short
        with pytest.raises(ValueError):
            _val_replace(
                [('@', '') for _ in range(len(_text)-1)],
                len(_text)
            )

        # too long
        with pytest.raises(ValueError):
            _val_replace(
                [('@', '') for _ in range(len(_text)+1)],
                len(_text)
            )


    @pytest.mark.parametrize('good_replace',
        (
            None,
            ('a', ''),
            ('A', lambda x: 'some string'),
            (re.compile('a'), ''),
            (re.compile('A'), lambda x: 'some string'),
            (('b', 'B'), (re.compile('c', re.X), 'C')),
            [None for _ in range(10)],
            [('@', lambda x: 'new_word') for _ in range(10)],
            [(re.compile('@', re.I), '') for _ in range(10)],
            [(('b', 'B'), (re.compile('c', re.X), 'C')) for _ in range(10)]
        )
    )
    def test_accepts_good_replace(self, _text, good_replace):
        # could be None, tuple, list
        _val_replace(good_replace, len(_text))





