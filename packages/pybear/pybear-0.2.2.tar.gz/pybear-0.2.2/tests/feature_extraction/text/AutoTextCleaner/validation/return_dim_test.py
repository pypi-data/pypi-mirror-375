# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._AutoTextCleaner._validation._return_dim \
    import _val_return_dim

import pytest




class TestValReturnDim:



    @pytest.mark.parametrize('_junk_rd',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk(self, _junk_rd):

        with pytest.raises(TypeError):

            _val_return_dim(_junk_rd)


    @pytest.mark.parametrize('_rd', (None, 1, 2))
    def test_rejects_junk(self, _rd):

        assert _val_return_dim(_rd) is None














