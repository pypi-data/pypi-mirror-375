# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


# see _shift_points_and_passes and points_and_passes_test for proving out
# shifting of points arrays, and _total_passes_is_hard

# see _shift_grid and shift_grid_test for proving out accuracy of shifted
# search grids for left/right shift, for linspace/logspace


import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._shift._shift import _shift



class TestShift:


    @staticmethod
    @pytest.fixture
    def good_grid():

        return {
            0: {'a': [20, 30, 40], 'b': ['a', 'b', 'c']},
            1: {'a': [10, 20, 30], 'b': ['a', 'b', 'c']},
            2: {}
        }


    @staticmethod
    @pytest.fixture
    def good_phlite():
        return {'a': False}


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {'a': False, 'b': False}


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[1, 2, 3], [3, 3, 3], 'soft_integer'],
            'b': [['a', 'b', 'c'], [3, 3, 3], 'fixed_string']
        }


    @staticmethod
    @pytest.fixture
    def good_best_params():
        return {'a': [40], 'b': ['a']}

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_rejects_non_empty_param_grid(
        self, good_grid, good_phlite, good_is_logspace, good_params,
        good_best_params
    ):

        with pytest.raises(ValueError):
            _shift(
                good_grid,
                good_phlite,
                good_is_logspace,
                good_params,
                1,
                good_best_params,
                _total_passes_is_hard=False
            )


    def test_rejects_pass_not_in_grid(
        self, good_grid, good_phlite, good_is_logspace, good_params,
        good_best_params
    ):

        with pytest.raises(ValueError):
            _shift(
                good_grid,
                good_phlite,
                good_is_logspace,
                good_params,
                10,
                good_best_params,
                _total_passes_is_hard=False
            )


    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_dtype',
    ('fixed_string', 'hard_integer, hard_float', 'fixed_integer', 'fixed_float')
    )
    @pytest.mark.parametrize('_total_passes_is_hard', (True, False))
    @pytest.mark.parametrize('_landing_spot', ('left', 'middle', 'right'))
    def test_non_soft_grid_is_unaltered_by_shift(
        self, _dtype, _space, _total_passes_is_hard, _landing_spot
    ):
        # but points/shrink_pass will change!

        # _is_logspace shouldnt matter, so passing it shouldnt matter

        _grid_size = 4

        if 'fixed_string' in _dtype:
            _grid = list('abcdefghijklmnop'[:_grid_size])
        else:
            if _space == 'linspace':
                _grid = np.linspace(1, _grid_size, _grid_size).tolist()
            elif _space == 'logspace':
                _grid = np.logspace(1, _grid_size, _grid_size).tolist()

            if 'integer' in _dtype:
                _grid = list(map(int, _grid))
            else:
                _grid = list(map(float, _grid))

        _GRIDS = {0: {'a': _grid}, 1: {}}

        _params = {'a': [_grid, [_grid_size for _ in range(3)], _dtype]}


        _phlite = {}

        if _landing_spot == 'left':
            _best = {'a': _grid[0]}
        elif _landing_spot == 'right':
            _best = {'a': _grid[-1]}
        elif _landing_spot == 'middle':
            _best = {'a': _grid[1]}


        grids_out, params_out  = _shift(
            _GRIDS=_GRIDS,
            _PHLITE=_phlite,
            _IS_LOGSPACE={'a': _space=='logspace'},  # gap is 1
            _params=_params,
            _pass=1,
            _best_params_from_previous_pass=_best,
            _total_passes_is_hard=_total_passes_is_hard
        )

        assert grids_out[1] == _GRIDS[0]
        assert grids_out[1] == grids_out[0]


        assert params_out['a'][0] == _params['a'][0]

        if _total_passes_is_hard:
            assert len(params_out['a'][1]) == len(_params['a'][1])
        else:
            assert len(params_out['a'][1]) == (len(_params['a'][1]) + 1)

        assert params_out['a'][2] == _params['a'][2]



    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_dtype', ('soft_integer', 'soft_float'))
    @pytest.mark.parametrize('_total_passes_is_hard', (True, False))
    @pytest.mark.parametrize('_landing_spot', ('left', 'middle', 'right'))
    def test_soft_grid_is_altered_by_shift(
        self, _dtype, _space, _total_passes_is_hard, _landing_spot
    ):

        _grid_size = 4

        if _space == 'linspace':
            _grid = np.linspace(1, _grid_size, _grid_size).tolist()
        elif _space == 'logspace':
            _grid = np.logspace(1, _grid_size, _grid_size).tolist()

        if 'integer' in _dtype:
            _grid = list(map(int, _grid))
        else:
            _grid = list(map(float, _grid))

        _GRIDS = {0: {'a': _grid}, 1: {}}

        _params = {'a': [_grid, [_grid_size for _ in range(3)], _dtype]}


        _phlite = {'a': True if _landing_spot == 'middle' else False}

        if _landing_spot == 'left':
            _best = {'a': _grid[0]}
        elif _landing_spot == 'right':
            _best = {'a': _grid[-1]}
        elif _landing_spot == 'middle':
            _best = {'a': _grid[1]}


        grids_out, params_out  = _shift(
            _GRIDS=_GRIDS,
            _PHLITE=_phlite,
            _IS_LOGSPACE={'a': _space=='logspace'},  # gap is 1
            _params=_params,
            _pass=1,
            _best_params_from_previous_pass=_best,
            _total_passes_is_hard=_total_passes_is_hard
        )

        assert len(grids_out[1]['a']) == len(grids_out[0]['a'])
        assert len(grids_out[1]['a']) == len(_GRIDS[0]['a'])
        assert len(grids_out[1]['a']) == len(_GRIDS[1]['a'])

        assert len(params_out['a'][0]) == len(_params['a'][0])
        assert len(params_out['a'][0]) == len(_GRIDS[1]['a'])
        assert len(params_out['a'][0]) == len(_GRIDS[0]['a'])

        if _total_passes_is_hard:
            assert len(params_out['a'][1]) == len(_params['a'][1])
        else:
            assert len(params_out['a'][1]) == (len(_params['a'][1]) + 1)

        assert params_out['a'][2] == _params['a'][2]







