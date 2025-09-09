# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._validation. \
    _character_frequency import _val_character_frequency



class TestCharacterFrequency:


    @pytest.mark.parametrize('junk_character_frequency',
        (-2.7, -1, 0, 1, 2.7, True, None, 'rubbish', [0, 1], (1,), lambda x: x)
    )
    def test_rejects_non_dict(self, junk_character_frequency):

        with pytest.raises(AssertionError):

            _val_character_frequency(junk_character_frequency)


    @pytest.mark.parametrize('bad_key', (-2.7, -1, 0, 1, 2.7, True, False, None))
    def test_rejects_bad_key(self, bad_key):

        # non-str key
        with pytest.raises(AssertionError):
            _val_character_frequency({bad_key: 1})


    @pytest.mark.parametrize('long_key', ('these', 'keys', 'are', 'too', 'long'))
    def test_rejects_key_too_long(self, long_key):

        # long key
        with pytest.raises(AssertionError):
            _val_character_frequency({long_key: 1})


    @pytest.mark.parametrize('bad_value',
        (-2.7, -1, 0, 2.7, True, False, None, 'junk', [0, 1], (1,), lambda x: x)
    )
    def test_rejects_bad_value(self, bad_value):

        # non-positive-int value
        with pytest.raises(AssertionError):
            _val_character_frequency({'a': bad_value})


    def test_accepts_good_startwith_frequency(self):

        _val_character_frequency({'a': 1})

        _val_character_frequency({'A': 9_876_543})