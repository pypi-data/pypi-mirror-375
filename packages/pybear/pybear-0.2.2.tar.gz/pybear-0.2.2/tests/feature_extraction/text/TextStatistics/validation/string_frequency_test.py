# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._validation._string_frequency \
    import _val_string_frequency



class TestStringFrequency:

    @pytest.mark.parametrize('junk_string_frequency',
        (-2.7, -1, 0, 1, 2.7, True, None, 'rubbish', [0, 1], (1,), lambda x: x)
    )
    def test_rejects_non_dict(self, junk_string_frequency):

        with pytest.raises(AssertionError):

            _val_string_frequency(junk_string_frequency)


    @pytest.mark.parametrize('bad_key',
        (-2.7, -1, 0, 1, 2.7, True, False, None)
    )
    def test_rejects_bad_key(self, bad_key):

        # non-str key
        with pytest.raises(AssertionError):
            _val_string_frequency({bad_key: 1})


    @pytest.mark.parametrize('bad_value',
        (-2.7, -1, 0, 2.7, True, False, None, 'junk', [0, 1], (1,), lambda x: x)
    )
    def test_rejects_bad_value(self, bad_value):

        # non-positive-int value
        with pytest.raises(AssertionError):
            _val_string_frequency({'what': bad_value})


    def test_accepts_good_string_frequency(self):

        _val_string_frequency({'apple': 1})

        _val_string_frequency({'APPLE': 1_234_567})








