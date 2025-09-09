# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _build_character_frequency import _build_character_frequency



class TestBuildCharacterFrequency:

    @pytest.mark.parametrize('junk_freq',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0,1], (1,), lambda x: x)
    )
    def test_rejects_junk(self, junk_freq):

        with pytest.raises(Exception):
            _build_character_frequency(junk_freq)


    def test_rejects_bad(self):

        with pytest.raises(Exception):
            _build_character_frequency({1: 1})

        with pytest.raises(Exception):
            _build_character_frequency({1: 'a'})

        with pytest.raises(Exception):
            _build_character_frequency({'a': 'a'})


    def test_accuracy(self):

        _freq1 = {
            'I': 3,
            'Sam': 2,
            'Sam-I-am': 3,
            'That': 2,
            'am': 2,
            'do': 1,
            'like': 1,
            'not': 1,
            'that': 1
        }

        out = _build_character_frequency(_freq1)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.keys())))

        exp = {
            'I': 6, 'S': 5, 'T': 2, 'a': 13, 'd': 1, 'e': 1, 'h': 3,
            'i': 1, 'k': 1, 'l': 1, 'm': 10, 'n': 1, 'o': 2, 't': 5,
            '-': 6
        }

        assert out == exp


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        _freq2 = {
            'Do': 1,
            'I': 2,
            'Sam-I-am': 1,
            'and': 2,
            'do': 2,
            'eggs': 2,
            'green': 2,
            'ham': 2,
            'like': 3,
            'not': 2,
            'them': 1,
            'you': 1
        }

        out = _build_character_frequency(_freq2)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.keys())))

        exp = {
            'D': 1, 'I': 3, 'S': 1, 'a': 6, 'd': 4, 'e': 10, 'g': 6,
            'h': 3, 'i': 3, 'k': 3, 'l': 3, 'm': 5, 'n': 6, 'o': 6,
            'r': 2, 's': 2, 't': 3, 'u': 1, 'y': 1, '-': 2
        }

        assert out == exp





