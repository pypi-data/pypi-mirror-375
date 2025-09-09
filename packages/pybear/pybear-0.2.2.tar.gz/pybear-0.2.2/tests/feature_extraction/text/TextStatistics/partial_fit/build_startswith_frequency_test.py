# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _build_startswith_frequency import _build_startswith_frequency



class TestBuildStartswithFrequency:

    @pytest.mark.parametrize('junk_freq',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0,1], (1,), lambda x: x)
    )
    def test_rejects_junk(self, junk_freq):

        with pytest.raises(Exception):
            _build_startswith_frequency(junk_freq)


    def test_rejects_bad(self):

        with pytest.raises(Exception):
            _build_startswith_frequency({1: 1})

        with pytest.raises(Exception):
            _build_startswith_frequency({1: 'a'})

        with pytest.raises(Exception):
            _build_startswith_frequency({'a': 'a'})


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

        out = _build_startswith_frequency(_freq1)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.keys())))

        exp = {'I': 3, 'S': 5, 'T': 2, 'a': 2, 'd': 1, 'l': 1, 'n': 1, 't': 1}

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

        out = _build_startswith_frequency(_freq2)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.keys())))

        exp = {
            'D': 1, 'I': 2, 'S': 1, 'a': 2, 'd': 2, 'e': 2, 'g': 2,
            'h': 2, 'l': 3, 'n': 2, 't': 1, 'y': 1
        }

        assert out == exp





