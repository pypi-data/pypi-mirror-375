# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation.\
    _agscv_verbose import _val_agscv_verbose



class TestAgscvVerbose:


    @pytest.mark.parametrize('non_bool',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', (1,2), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_non_bool(self, non_bool):

        with pytest.raises(TypeError):
            _val_agscv_verbose(non_bool)


    @pytest.mark.parametrize('_bool', (True, False))
    def test_accepts_bool(self, _bool):
        assert _val_agscv_verbose(_bool) is None








