# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._AutoTextCleaner._validation._get_statistics \
    import _val_get_statistics

import pytest



class TestValGetStatistics:


    @pytest.mark.parametrize('_junk_gs',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    def test_rejects_junk(self, _junk_gs):

        with pytest.raises(TypeError):

            _val_get_statistics(_junk_gs)


    @pytest.mark.parametrize('key', ('trash', 'garbage', 'before', 'after'))
    @pytest.mark.parametrize('value',
        (-2.7, -1, 0, 1, 2.7, 'trash', [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_bad_1(self, key, value):

        with pytest.raises(ValueError):

            _val_get_statistics({key: value})


    @pytest.mark.parametrize('value1',
        (-2.7, -1, 0, 1, 2.7, 'trash', [0, 1], (1,), {1, 2}, {'a': 1}, lambda x: x)
    )
    @pytest.mark.parametrize('value2',
        (-2.7, -1, 0, 1, 2.7, 'trash', [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_bad_2(self, value1, value2):

        with pytest.raises(TypeError):

            _val_get_statistics({'before': value1, 'after': value2})


    @pytest.mark.parametrize('value1', (True, False, None))
    @pytest.mark.parametrize('value2', (True, False, None))
    def test_accepts_good(self, value1, value2):

        assert _val_get_statistics({'before': value1, 'after': value2}) is None








