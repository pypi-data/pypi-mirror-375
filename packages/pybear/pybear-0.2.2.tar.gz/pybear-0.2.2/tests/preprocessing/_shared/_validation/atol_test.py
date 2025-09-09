# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing.__shared._validation._atol import _val_atol



class TestAtol:


    @pytest.mark.parametrize('junk_atol',
        (None, 'trash', [0,1], (0,1), {0,1}, {'a':1}, min, lambda x: x)
    )
    def test_rejects_junk(self, junk_atol):
        with pytest.raises(TypeError):
            _val_atol(junk_atol)


    @pytest.mark.parametrize('bad_atol', (True, False, -1, -3.1415))
    def test_rejects_bad(self, bad_atol):
        with pytest.raises(ValueError):
            _val_atol(bad_atol)


    @pytest.mark.parametrize('good_atol', (0, 1e-6, 0.1, 1, 3.1415))
    def test_accepts_good(self, good_atol):
        assert _val_atol(good_atol) is None






