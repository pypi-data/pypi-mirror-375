# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._Lexicon._methods._find_duplicates import \
    _find_duplicates



class TestFindDuplicates:


    @pytest.mark.parametrize('junk_sf',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [0,1], (1,), {1, 2}, lambda x: x)
    )
    def test_blocks_junk_string_frequency(self, junk_sf):

        with pytest.raises(AssertionError):

            _find_duplicates(junk_sf)


    def test_accuracy(self):

        string_frequency_ = {'an': 1, 'apple': 1, 'a': 1, 'day': 1}

        out = _find_duplicates(string_frequency_)

        assert isinstance(out, dict)

        assert len(out) == 0

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        string_frequency_ = {'an': 1, 'apple': 4, 'a': 1, 'day': 13}

        out = _find_duplicates(string_frequency_)

        assert isinstance(out, dict)

        assert all(map(
            isinstance,
            string_frequency_.keys(),
            (str for _ in string_frequency_)
        ))

        assert all(map(
            isinstance,
            string_frequency_.values(),
            (int for _ in string_frequency_)
        ))

        assert 'apple' in out
        assert out['apple'] == 4

        assert 'day' in out
        assert out['day'] == 13



