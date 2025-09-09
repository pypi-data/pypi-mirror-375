# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _total_passes_is_hard import _val_total_passes_is_hard



class TestTotalPassesIsHard:

    @pytest.mark.parametrize('non_bool',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [1,2], (1,2), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_non_bool(self, non_bool):

        with pytest.raises(TypeError):
            _val_total_passes_is_hard(non_bool)


    def test_accepts_bool(self):

        assert _val_total_passes_is_hard(True) is None

        assert _val_total_passes_is_hard(False) is None








