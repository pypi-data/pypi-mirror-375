# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _validation import _validation



class TestValidation:

    # the heavy lifting is handled by the submodules, which have their own
    # tests. just ensure this module works and passes good.


    @pytest.mark.parametrize('_total_passes', (1, 3))
    @pytest.mark.parametrize('_total_passes_is_hard', (True, False))
    @pytest.mark.parametrize('_max_shifts', (None, 3))
    @pytest.mark.parametrize('_agscv_verbose', (True, False))
    def test_accuracy(
        self, _total_passes, _total_passes_is_hard, _max_shifts, _agscv_verbose,
        mock_estimator_params
    ):

        # save the og arguments to prove nothing is mutated
        _og_params = deepcopy(mock_estimator_params)
        _og_total_passes = deepcopy(_total_passes)
        _og_total_passes_is_hard = deepcopy(_total_passes_is_hard)
        _og_max_shifts = deepcopy(_max_shifts)
        _og_agscv_verbose = deepcopy(_agscv_verbose)

        assert _validation(
            mock_estimator_params,
            _total_passes,
            _total_passes_is_hard,
            _max_shifts,
            _agscv_verbose
        ) is None

        # prove nothing is mutated
        for _key, _value in mock_estimator_params.items():
            assert _key in _og_params
            assert len(_value) == 3
            assert len(_og_params[_key]) == 3
            assert np.array_equal(_value[0], _og_params[_key][0])
            assert _value[1] == _og_params[_key][1]
            assert _value[2] == _og_params[_key][2]
        assert _total_passes == _og_total_passes
        assert _total_passes_is_hard == _og_total_passes_is_hard
        assert _max_shifts == _og_max_shifts
        assert _agscv_verbose == _og_agscv_verbose




