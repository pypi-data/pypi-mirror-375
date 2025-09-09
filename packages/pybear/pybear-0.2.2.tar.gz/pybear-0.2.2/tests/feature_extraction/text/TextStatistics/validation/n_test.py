# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._validation._n import \
    _val_n



class TestValN:


    @pytest.mark.parametrize('junk_n',
        (-2.7, 2.7, True, False, None, 'trash', [1,2], {'a': 1}, lambda x: x)
    )
    def test_val_n_rejects_junk(self, junk_n):

        with pytest.raises(TypeError):
            _val_n(junk_n)


    @pytest.mark.parametrize('junk_n', (-2, -1, 0))
    def test_val_n_rejects_bad(self, junk_n):

        with pytest.raises(ValueError):
            _val_n(junk_n)


    @pytest.mark.parametrize('good_n', (1, 2, 10))
    def test_val_n_accepts_good(self, good_n):

        assert _val_n(good_n) is None



