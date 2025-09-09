# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing.__shared._validation. _equal_nan import _val_equal_nan



class TestEqualNan:


    @pytest.mark.parametrize('junk_ign_nan',
        (-1,0,1,3.14,None,min,'trash',[0,1],{0,1}, (1,), {'a':1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_ign_nan):
        with pytest.raises(TypeError):
            _val_equal_nan(junk_ign_nan)


    @pytest.mark.parametrize('good_ign_nan', (True, False))
    def test_accepts_bool(self, good_ign_nan):
        assert _val_equal_nan(good_ign_nan) is None




