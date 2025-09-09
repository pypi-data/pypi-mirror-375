# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _param_conditioning._max_shifts import _cond_max_shifts

import numbers

import pytest



class TestCondMaxShifts:


    @pytest.mark.parametrize('_max_shifts', (1, 1_000, None))
    @pytest.mark.parametrize('_inf_max_shifts', (1_000, 1_000_000))
    def test_accuracy(self, _max_shifts, _inf_max_shifts):

        out = _cond_max_shifts(_max_shifts, _inf_max_shifts)

        assert isinstance(out, numbers.Integral)
        assert out == (_max_shifts or _inf_max_shifts)






