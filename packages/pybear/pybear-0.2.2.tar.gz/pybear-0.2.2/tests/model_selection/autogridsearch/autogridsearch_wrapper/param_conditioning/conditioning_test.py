# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _param_conditioning._conditioning import _conditioning

import numbers

import numpy as np

import pytest



class TestConditioning:

    # this module is a hub for the conditioning submodules, whose
    # accuracy are tested elsewhere. just do basic checks to make sure
    # this module works.

    @pytest.mark.parametrize('_total_passes', (2, 3))
    @pytest.mark.parametrize('_max_shifts', (None, 3))
    @pytest.mark.parametrize('_inf_max_shifts', (985682, 1_000_000))
    def test_accuracy(self, _total_passes, _max_shifts, _inf_max_shifts):

        _params = {
            'param_1': [{'a', 'b', 'c'}, 1, 'fixed_StRiNg'],
            'param_2': ({True, False}, [2,2,1][:_total_passes], 'FiXeD_BOOL'),
            'param_3': [(1,2,3,4), [4,1,1][:_total_passes], 'fixed_inTEGER'],
            'param_4': (np.logspace(-5, 5, 11), 11, 'SOFT_float')
        }

        out_params, out_total_passes, out_max_shifts = \
            _conditioning(
                _params,
                _total_passes,
                _max_shifts,
                _inf_max_shifts
            )

        key_key = {0: 'param_1', 1:'param_2', 2:'param_3', 3:'param_4'}
        type_key = {
            0: 'fixed_string', 1: 'fixed_bool', 2: 'fixed_integer',
            3: 'soft_float'
        }

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # out_params
        assert isinstance(out_params, dict)
        for idx, (key, value) in enumerate(out_params.items()):
            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # params keys
            assert isinstance(key, str)
            assert key == key_key[idx]
            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # params values
            assert isinstance(value, list)
            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # values idx 0
            assert isinstance(value[0], list)
            assert np.array_equal(value[0], list(_params[key][0]))
            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # values idx 1
            assert isinstance(value[1], list)
            assert all(map(isinstance, value[1], (int for _ in value[1])))
            assert len(value[1]) == out_total_passes
            if isinstance(_params[key][1], numbers.Integral):
                _ref_points = [_params[key][1] for i in range(_total_passes)]
            else:
                _ref_points = _params[key][1]
            _ref_points[0] = len(_params[key][0])
            assert np.array_equal(out_params[key][1], _ref_points)
            del _ref_points
            # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
            # values idx 2
            assert isinstance(value[-1], str)
            assert value[-1] == type_key[idx]
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # out_total_passes
        assert isinstance(out_total_passes, numbers.Integral)
        assert out_total_passes == _total_passes
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # out_max_shifts
        assert isinstance(out_max_shifts, numbers.Integral)
        assert out_max_shifts == (_max_shifts or _inf_max_shifts)
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --




