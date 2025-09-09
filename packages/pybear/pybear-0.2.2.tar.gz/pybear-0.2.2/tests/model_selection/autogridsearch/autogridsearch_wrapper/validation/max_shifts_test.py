# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _max_shifts import _val_max_shifts



class TestMaxShifts:


    @pytest.mark.parametrize('non_numeric',
    (True, False, 'trash', [1,2], (1,2), {1,2}, {'a':1}, lambda x: x)
    )
    @pytest.mark.parametrize('can_be_None', (True, False))
    def test_rejects_non_numeric(self, non_numeric, can_be_None):
        with pytest.raises(TypeError):
            _val_max_shifts(non_numeric, can_be_None)


    @pytest.mark.parametrize('non_integer',
        (float('-inf'), -2.718, 2.718, float('inf'))
    )
    @pytest.mark.parametrize('can_be_None', (True, False))
    def test_rejects_non_integer(self, non_integer, can_be_None):
        with pytest.raises(TypeError):
            _val_max_shifts(non_integer, can_be_None)


    @pytest.mark.parametrize('less_than_one', (0, -1))
    @pytest.mark.parametrize('can_be_None', (True, False))
    def test_rejects_less_than_one(self, less_than_one, can_be_None):
        with pytest.raises(ValueError):
            _val_max_shifts(less_than_one, can_be_None)


    @pytest.mark.parametrize('_max_shifts', (None, 3, 10, 1_000))
    @pytest.mark.parametrize('can_be_None', (True, False))
    def test_accepts_good(self, _max_shifts, can_be_None):

        # int >= 1 or conditionally None
        if _max_shifts is None and not can_be_None:
            with pytest.raises(TypeError):
                _val_max_shifts(_max_shifts, can_be_None)
        else:
            assert _val_max_shifts(_max_shifts, can_be_None) is None





