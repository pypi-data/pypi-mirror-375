# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from copy import deepcopy
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._get_next_param_grid import _get_next_param_grid



# def _get_next_param_grid(
#     _GRIDS: GridsType,
#     _params: ParamsType,
#     _PHLITE: PhliteType,
#     _IS_LOGSPACE: IsLogspaceType,
#     _best_params_from_previous_pass: BestParamsType,
#     _pass: int,
#     _total_passes: int,
#     _total_passes_is_hard: bool,
#     _shift_ctr: int,
#     _max_shifts: int
# ) -> tuple[GridsType, ParamsType, PhliteType, IsLogspaceType, int, int]:



class TestValidation:

    #   _GRIDS
    # core _GRIDS _validation handled by _validate_grid / validate_grids_test


    # special _GRIDS _validation
    # 'max_shifts' can never be None going into _get_next_param_grid

    @pytest.mark.parametrize('bad_GRIDS',
        ({}, {0: {'a': [1, 2, 3], 'b': [3, 4, 5]}, 1: {}})
    )
    def test_rejects_empty_grids(self, bad_GRIDS, mock_estimator_params):

        with pytest.raises(ValueError):
            _get_next_param_grid(
                bad_GRIDS,
                mock_estimator_params,
                _PHLITE={'c': False},
                _IS_LOGSPACE={'a': False, 'b': False, 'c': 1.0, 'd': False},
                _best_params_from_previous_pass = \
                    {'a': 'y', 'b': 3, 'c': 1e3, 'd': False},
                _pass=1,
                _total_passes=3,
                _total_passes_is_hard=False,
                _shift_ctr=0,
                _max_shifts=100
            )

    # remaining _validation handed in dedicated modules


class TestOutputFormats:


    @pytest.mark.parametrize('_total_passes', (4,))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_pass', (1,2,3))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    def test_output_formats(self, _total_passes, _tpih, _pass, _posn):

        # this is not exhaustive for logspace, gaps, shrink passes, shrinks, etc.

        _keys = 'abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        _types = ('soft_integer', 'soft_float', 'hard_integer',
                  'hard_float', 'fixed_string', 'fixed_bool')

        _params = {}
        ctr = 0
        for _type in _types:
            if 'fixed_string' in _type:
                _grid = ['mmm', 'nnn', 'ooo', 'ppp']
                _params[_keys[ctr]] = [_grid, [4]*_total_passes, _type]
            elif 'fixed_bool' in _type:
                _grid = [True, False]
                _params[_keys[ctr]] = [_grid, [2]*_total_passes, _type]
            else:
                _grid = [2,3,4,5]

                if 'int' in _type:
                    _grid = list(map(int, _grid))
                elif 'float' in _type:
                    _grid = list(map(float, _grid))

                _points = [len(_grid) for _ in range(_total_passes)]

                _params[_keys[ctr]] = [_grid, _points, _type]

            ctr += 1

        _GRIDS = {}
        for _pass_ in range(_pass):
            _GRIDS[_pass_] = {}
            for _param in _params:
                _GRIDS[_pass_][_param] = _params[_param][0]

        # this is a snapshot of the state after the last pass
        _PHLITE = {}
        for _param in _params:
            _type = _params[_param][-1]
            if 'soft' in _type:
                _PHLITE[_param] = True if _posn == 'middle' else False
            elif 'hard' in _type or 'fixed' in _type:
                continue

        # this is a snapshot of the state after the last pass
        _IS_LOGSPACE = {}
        for _param in _params:
            if _params[_param][-1] in ['fixed_string', 'fixed_bool']:
                _IS_LOGSPACE[_param] = False
            else:
                _log_grid = np.log10(_GRIDS[_pass-1][_param])
                _log_gaps = np.unique(_log_grid[1:] - _log_grid[:-1])
                if len(_log_gaps) == 1:
                    _IS_LOGSPACE[_param] = _log_gaps[0]
                else:
                    _IS_LOGSPACE[_param] = False

        if _posn == 'left':
            idx = 0
        elif _posn == 'middle':
            idx = 1
        elif _posn == 'right':
            idx = -1

        _best = {_param: _GRIDS[_pass-1][_param][idx] for _param in _params}

        _OUT_GRIDS, _out_params, _OUT_PHLITE, _OUT_IS_LOGSPACE, \
        _OUT_shift_ctr_end, _out_total_passes_end = \
            _get_next_param_grid(
                _GRIDS=_GRIDS,
                _params=_params,
                _PHLITE=_PHLITE,
                _IS_LOGSPACE=_IS_LOGSPACE,
                _best_params_from_previous_pass=_best,
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=0,
                _max_shifts=3
            )

        assert isinstance(_out_params, dict)
        assert _out_params.keys() == _params.keys()
        _lens = np.unique(list(map(len, _out_params.values())))
        assert len(_lens) == 1
        assert _lens[0] == 3
        del _lens

        assert isinstance(_OUT_GRIDS, dict)
        assert all(map(
            isinstance, _OUT_GRIDS.keys(), (int for _ in _OUT_GRIDS)
        ))
        assert list(_OUT_GRIDS.keys()) == list(range(_pass + 1))
        assert all(map(
            isinstance, _OUT_GRIDS.values(), (dict for _ in _OUT_GRIDS)
        ))

        for _pass_ in _OUT_GRIDS:
            assert all(map(
                isinstance, _OUT_GRIDS[_pass_].keys(), (str for _ in _OUT_GRIDS)
            ))
            assert _OUT_GRIDS[_pass_].keys() == _params.keys()
            assert _OUT_GRIDS[_pass_].keys() == _GRIDS[_pass_].keys()
            assert all(map(
                isinstance,
                _OUT_GRIDS[_pass_].values(),
                (list for _ in _OUT_GRIDS)
            ))

            for _param in _OUT_GRIDS[_pass]:
                _type = _params[_param][-1]
                _out_grid = _OUT_GRIDS[_pass_][_param]
                if 'int' in _type:
                    assert all(map(
                        isinstance, _out_grid, (int for _ in _out_grid)
                    ))
                elif 'float' in _type:
                    assert all(map(
                        isinstance, _out_grid, (float for _ in _out_grid)
                    ))
                elif _type == 'fixed_string':
                    assert all(map(
                        isinstance, _out_grid, (str for _ in _out_grid)
                    ))
                elif _type == 'fixed_bool':
                    assert all(map(
                        isinstance, _out_grid, (bool for _ in _out_grid)
                    ))


        assert isinstance(_OUT_PHLITE, dict)
        assert _OUT_PHLITE.keys() == _PHLITE.keys()
        assert list(_OUT_PHLITE.values()) == list(_PHLITE.values())


        assert isinstance(_OUT_IS_LOGSPACE, dict)
        assert _OUT_IS_LOGSPACE.keys() == _OUT_IS_LOGSPACE.keys()
        assert _OUT_IS_LOGSPACE.keys() == _params.keys()
        assert list(_OUT_IS_LOGSPACE.values()) == list(_OUT_IS_LOGSPACE.values())


        assert isinstance(_OUT_shift_ctr_end, int)
        assert isinstance(_out_total_passes_end, int)


class TestFixedBoolAndStringGrids:

    # fixed bool & string just pass thru unless shrink pass
    # never increments total_passes (no shift)

    @pytest.mark.parametrize('_type',
        ('fixed_integer', 'fixed_float', 'fixed_string', 'fixed_bool')
    )
    @pytest.mark.parametrize('_best', (1,2,3,4))
    @pytest.mark.parametrize('_pass, _total_passes', ((1, 3), (2, 3), (1, 2)))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_shift_ctr', (0, 1))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    def test_fixed_str_bool_grids_unchanged(
        self, _type, _best, _pass, _total_passes, _tpih, _shift_ctr,
        _max_shifts,
    ):

        # total_passes unchanged
        # shift_ctr never incremented

        _grid = [1,2,3,4]
        if _type == 'fixed_string':
            _grid = list(map(str, _grid))
            _best = str(_best)
            _points = [4]*_total_passes
        elif _type == 'fixed_bool':
            _grid = [True, False]
            _best = True if _best in [1, 2] else False
            _points = [2]*_total_passes
        else:
            _points = [4]*_total_passes

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS={i: {'a': _grid} for i in range(_pass)},
                _params={'a': [_grid, _points, _type]},
                _PHLITE={'a': True},
                _IS_LOGSPACE={'a': False},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=0,
                _max_shifts=_max_shifts
            )


        assert _GRIDS == {i: {'a': _grid} for i in range(_pass + 1)}
        assert _params == {'a': [_grid, _points, _type]}
        assert _PHLITE == {'a': True}
        assert _IS_LOGSPACE == {'a': False}
        assert _shift_ctr == 0
        assert _total_passes_end == _total_passes



    @pytest.mark.parametrize('_type', ('fixed_string', 'fixed_bool'))
    @pytest.mark.parametrize('_best_posn', (0, 1))
    @pytest.mark.parametrize('_pass, _total_passes', ((1, 2), (1, 3), (2, 3)))
    @pytest.mark.parametrize('_shrink_pass', (True, False))
    def test_string_bool_shrink_pass(
        self, _type, _best_posn, _pass, _total_passes, _shrink_pass
    ):

        # total_passes unchanged
        # shift_ctr never incremented
        if _type == 'fixed_string':
            _grid = ['a', 'b']
            _points = [2]*_total_passes
        elif _type == 'fixed_bool':
            _grid = [True, False]
            _points = [2] * _total_passes
        else:
            raise Exception

        if _shrink_pass:
            for _idx in range(len(_points)):
                if _idx >= _pass:
                    _points[_idx] = 1

        _best = _grid[_best_posn]

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS={i: {'a': _grid} for i in range(_pass)},
                _params={'a': [_grid, _points, _type]},
                _PHLITE={'a': True},
                _IS_LOGSPACE={'a': False},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=False,
                _shift_ctr=0,
                _max_shifts=3
            )

        if _shrink_pass is True:
            EXP_GRIDS = {i: {'a': _grid} for i in range(_pass)} | \
               {j: {'a': [_best]} for j in range(_pass, _pass + 1)}
        else:
            EXP_GRIDS = {i: {'a': _grid} for i in range(_pass + 1)}

        assert _GRIDS == EXP_GRIDS
        assert _params == {'a': [_grid, _points, _type]}
        assert _PHLITE == {'a': True}
        assert _IS_LOGSPACE == {'a': False}
        assert _shift_ctr == 0
        assert _total_passes_end == _total_passes


class TestSoftShifts:

    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_type', ('soft_integer', 'soft_float'))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_pass, _total_passes', ((1, 3), (2, 3), (1, 2)))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_max_shifts', (100, 3))
    @pytest.mark.parametrize('_shift_ctr', (0, 1))
    def test_soft_grid_shifts(
        self, _space, _type, _posn, _pass, _total_passes, _tpih,
        _max_shifts, _shift_ctr,
    ):

        if _space == 'linspace':
            _grid = [40, 50, 60, 70]
        elif _space == 'logspace':
            _grid = [1e2, 1e3, 1e4, 1e5]

        if 'int' in _type:
            _grid = list(map(int, _grid))
        elif 'float' in _type:
            _grid = list(map(float, _grid))

        if _posn == 'left':
            _best = _grid[0]
        elif _posn == 'middle':
            _best = _grid[1]
        elif _posn == 'right':
            _best = _grid[-1]

        _points = [len(_grid) for _ in range(_total_passes)]

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS={i: {'a': _grid} for i in range(_pass)},
                _params={'a': [_grid, _points, _type]},
                _PHLITE={'a': True if _posn == 'middle' else False},
                _IS_LOGSPACE={'a': 1.0 if _space == 'logspace' else False},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=_max_shifts
            )

        if _tpih or _posn == 'middle':
            assert _total_passes_end == _total_passes
        else:
            _points.append(len(_grid))
            assert _total_passes_end == _total_passes + 1

        base_exp_grids = {i: {'a': _grid} for i in range(_pass)}
        if _posn == 'left':
            if _space == 'linspace':
                offset = max(_grid) - _grid[1]
                newest_grid = (np.array(_grid) - offset).tolist()
            elif _space == 'logspace':
                _log_grid = np.log10(_grid)
                offset = max(_log_grid) - _log_grid[1]
                newest_grid = np.power(10, (_log_grid - offset)).tolist()
                del _log_grid

            assert _GRIDS == base_exp_grids | {_pass: {'a': newest_grid}}

        elif _posn == 'middle':
            pass  # this is a drill

        elif _posn == 'right':
            if _space == 'linspace':
                offset = _grid[-2] - min(_grid)
                newest_grid = (np.array(_grid) + offset).tolist()
            elif _space == 'logspace':
                _log_grid = np.log10(_grid)
                offset = _log_grid[-2] - min(_log_grid)
                newest_grid = np.power(10, (_log_grid + offset)).tolist()

            assert _GRIDS == base_exp_grids | {_pass: {'a': newest_grid}}

        assert _params == {'a': [_grid, _points, _type]}

        assert _PHLITE == {'a': True if _posn == 'middle' else False}

        assert _IS_LOGSPACE == {
            'a': 1.0 if _space == 'logspace' and _posn != 'middle' else False
        }

        if _posn == 'middle':
            assert _shift_ctr_end == _shift_ctr
        else:
            assert _shift_ctr_end == _shift_ctr + 1



class TestHardShiftsLinspace:

    @pytest.mark.parametrize('_type', ('hard_integer', 'hard_float'))
    @pytest.mark.parametrize('_hard_min', ('left', 'lt_left'))
    @pytest.mark.parametrize('_hard_max', ('right', 'gt_right'))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_pass, _total_passes', ((1, 4), (2, 4), (3, 4)))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    @pytest.mark.parametrize('_shift_ctr', (0, 1))
    def test_hard_grid_shifts_linspace(
        self, _type, _hard_min, _hard_max, _posn, _pass, _total_passes,
        _tpih, _max_shifts, _shift_ctr
    ):

        _grid = [40, 50, 60, 70]

        # set hard_min & hard_max in grid 0
        # (grid zero is always already run when _gnpg is accessed)
        # so essentially fudging grid 0 retroactively for tests purposes

        grid_0 = deepcopy(_grid)

        if _hard_min == 'left':
            pass # grid_0 stays the same as _grid
        elif _hard_min == 'lt_left':
            grid_0[0] = grid_0[0] - (grid_0[1] - grid_0[0])

        if _hard_max == 'right':
            pass  # grid_0 stays the same as _grid
        elif _hard_max == 'gt_right':
            grid_0[-1] = grid_0[-1] + (grid_0[-1] - grid_0[-2])

        # END fudging of hard_min & hard_max ** * ** * ** * ** * ** * **

        if 'int' in _type:
            _grid = list(map(int, _grid))
            grid_0 = list(map(int, grid_0))
        elif 'float' in _type:
            _grid = list(map(float, _grid))
            grid_0 = list(map(float, grid_0))

        _dict = {'left': 0, 'middle': 1, 'right': len(_grid)-1}
        _best = [*(grid_0 if _pass == 1 else _grid)][_dict[_posn]]
        del _dict

        _points = [len(_grid) for _ in range(_total_passes)]

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS= {0: {'a': grid_0}} | {i: {'a': _grid} for i in range(1, _pass)},
                _params={'a': [grid_0, _points, _type]},
                _PHLITE={},
                _IS_LOGSPACE={'a': False},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=_max_shifts
            )


        assert _total_passes_end == _total_passes

        if _posn == 'left':

            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[_pass-1]['a'][1]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]

        elif _posn == 'middle':
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[_pass-1]['a'][0]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]
            assert _GRIDS[_pass]['a'][2] <= _GRIDS[_pass - 1]['a'][2]

        elif _posn == 'right':

            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[_pass-1]['a'][-2]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]

        assert _params == {'a': [grid_0, _points, _type]}

        assert _PHLITE == {}

        assert _IS_LOGSPACE == {'a': False}

        assert _shift_ctr_end == _shift_ctr



class TestHardShiftsLogspace:

    @pytest.mark.parametrize('_type', ('hard_integer', 'hard_float'))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_hard_min', ('left', 'lt_left'))
    @pytest.mark.parametrize('_hard_max', ('right', 'gt_right'))
    @pytest.mark.parametrize('_pass, _total_passes', ((1, 4), (2, 4), (3, 4)))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    @pytest.mark.parametrize('_shift_ctr', (0, 1))
    def test_hard_grid_shifts_logspace(
        self, _type, _posn, _hard_min, _hard_max, _pass, _total_passes,
        _tpih, _max_shifts, _shift_ctr
    ):

        _grid = [1e2, 1e3, 1e4, 1e5]

        # set hard_min & hard_max in grid 0
        # (grid zero is always already run when _gnpg is accessed)
        # so essentially fudging grid 0 retroactively for tests purposes

        grid_0 = np.log10(deepcopy(_grid)).tolist()

        if _hard_min == 'left':
            pass # grid_0 stays the same as _grid
        elif _hard_min == 'lt_left':
            grid_0 = [grid_0[0] - (grid_0[1] - grid_0[0])] + grid_0

        if _hard_max == 'right':
            pass  # grid_0 stays the same as _grid
        elif _hard_max == 'gt_right':
            grid_0.append(grid_0[-1] + (grid_0[-1] - grid_0[-2]))

        grid_0 = np.power(10, grid_0).tolist()
        # END fudging of hard_min & hard_max ** * ** * ** * ** * ** * **

        if 'int' in _type:
            _grid = list(map(int, _grid))
            grid_0 = list(map(int, grid_0))
        elif 'float' in _type:
            _grid = list(map(float, _grid))
            grid_0 = list(map(float, grid_0))

        _dict = {'left': 0, 'middle': 1, 'right': len(_grid)-1}
        _best = [*(grid_0 if _pass == 1 else _grid)][_dict[_posn]]
        del _dict

        _points = [len(grid_0)] + [len(_grid) for _ in range(_total_passes)][1:]

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS= {0: {'a': grid_0}} | {i: {'a': _grid} for i in range(1, _pass)},
                _params={'a': [grid_0, _points, _type]},
                _PHLITE={},
                _IS_LOGSPACE={'a': 1.0},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=_max_shifts
            )


        assert _total_passes_end == _total_passes

        if _posn == 'left':
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[_pass-1]['a'][1]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]

        elif _posn == 'middle':
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]
            assert _GRIDS[_pass]['a'][2] <= _GRIDS[_pass - 1]['a'][2]

        elif _posn == 'right':
            assert _GRIDS[_pass]['a'][0] >= _GRIDS[0]['a'][0]
            assert _GRIDS[_pass]['a'][-1] <= _GRIDS[0]['a'][-1]

        assert _params == {'a': [grid_0, _points, _type]}

        assert _PHLITE == {}

        assert _IS_LOGSPACE == {'a': False}

        assert _shift_ctr_end == _shift_ctr



class TestLogspaceRegap:

    # this proves out that regap only happens when 'hard' in type,
    # or shift_ctr == max_shifts, or landed off an edge, and regaps
    # correctly. total passes never incremented when only a regap.

    @pytest.mark.parametrize('_type', ('soft_float', 'hard_float'))
    @pytest.mark.parametrize('_gap', (2, 3))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_total_passes', (3,))
    @pytest.mark.parametrize('_pass, _shift_ctr, _max_shifts',
        ((1, 0, 1),(1, 0, 2), (2, 0, 1), (2, 0, 2),(2, 1, 1), (2, 1, 2))
    )
    @pytest.mark.parametrize('_tpih', (True, False))
    def test_logspace_regap_float(
        self, _type, _gap, _posn, _pass, _total_passes, _tpih, _max_shifts,
        _shift_ctr
    ):

        _grid = np.logspace(0, 3 * _gap, 4).tolist()

        _grid = list(map(float, _grid))

        if _posn == 'left':
            _best = _grid[0]
        elif _posn == 'middle':
            _best = _grid[1]
        elif _posn == 'right':
            _best = _grid[-1]

        _points = [len(_grid) for _ in range(_total_passes)]

        if 'hard' in _type:
            _PHLITE = {}
        else:
            _PHLITE = {'a': True if _posn == 'middle' else False}

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS={i: {'a': _grid} for i in range(_pass)},
                _params={'a': [_grid, _points, _type]},
                _PHLITE=_PHLITE,
                _IS_LOGSPACE={'a': float(_gap)},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=_max_shifts
            )

        _log_GRID = np.log10(_GRIDS[_pass]['a'])
        _gaps = np.unique(_log_GRID[1:] - _log_GRID[:-1])

        if 'hard' in _type:
            assert len(_gaps) == 1
            assert _gaps[0] == 1
            assert _PHLITE == {}
            assert _IS_LOGSPACE == {'a': 1.0}
            assert _shift_ctr_end == _shift_ctr
            assert _total_passes_end == _total_passes
        elif 'soft' in _type:
            if _shift_ctr == _max_shifts or _posn == 'middle':
                assert len(_gaps) == 1
                assert _gaps[0] == 1
                assert _PHLITE == {'a': True}
                assert _IS_LOGSPACE == {'a': 1.0}
                assert _shift_ctr_end == _shift_ctr
                assert _total_passes_end == _total_passes
            elif _posn != 'middle':
                assert len(_gaps) == 1
                assert _gaps[0] == _gap
                assert _PHLITE == {'a': False}
                assert _IS_LOGSPACE == {'a': _gap}
                assert _shift_ctr_end == _shift_ctr + 1
                if _tpih:
                    assert _total_passes_end == _total_passes
                else:
                    # a shift was done, insert new points
                    _points.insert(_pass, len(_GRIDS[0]['a']))
                    assert _total_passes_end == _total_passes + 1


        _points[_pass] = len(_log_GRID)

        assert _params == {'a': [_grid, _points, _type]}


    @pytest.mark.parametrize('_type', ('soft_integer', 'hard_integer'))
    @pytest.mark.parametrize('_gap', (2, 3))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_total_passes', (3,))
    @pytest.mark.parametrize('_pass, _shift_ctr, _max_shifts',
        ((1, 0, 1), (1, 0, 2), (2, 0, 1), (2, 0, 2), (2, 1, 1), (2, 1, 2))
    )
    @pytest.mark.parametrize('_tpih', (True, False))
    def test_logspace_regap_integer(
        self, _type, _gap, _posn, _pass, _total_passes, _tpih, _max_shifts,
        _shift_ctr
    ):

        _grid = np.logspace(0, 3 * _gap, 4).tolist()

        _grid = list(map(int, _grid))

        if _posn == 'left':
            _best = _grid[0]
        elif _posn == 'middle':
            _best = _grid[1]
        elif _posn == 'right':
            _best = _grid[-1]

        _points = [len(_grid) for _ in range(_total_passes)]

        if 'hard' in _type:
            _PHLITE = {}
        else:
            _PHLITE = {'a': True if _posn == 'middle' else False}

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS={i: {'a': _grid} for i in range(_pass)},
                _params={'a': [_grid, _points, _type]},
                _PHLITE=_PHLITE,
                _IS_LOGSPACE={'a': float(_gap)},
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=_max_shifts
            )

        _log_hard_min = np.log10(_GRIDS[0]['a'][0])
        _log_hard_max = np.log10(_GRIDS[0]['a'][-1])

        _log_GRID = np.log10(_GRIDS[_pass]['a'])
        _gaps = np.unique(_log_GRID[1:] - _log_GRID[:-1])

        if 'hard' in _type:
            assert len(_gaps) == 1
            assert _gaps[0] == 1
            assert _PHLITE == {}
            assert _IS_LOGSPACE == {'a': 1.0}
            assert _shift_ctr_end == _shift_ctr
            assert _total_passes_end == _total_passes
        elif 'soft' in _type:
            if (_shift_ctr == _max_shifts) or \
                    _posn == 'middle' or (_log_GRID[0] == _log_hard_min):
                assert len(_gaps) == 1
                assert _gaps[0] == 1
                assert _PHLITE == {'a': True}
                assert _IS_LOGSPACE == {'a': 1.0}
                assert _shift_ctr_end == _shift_ctr
                assert _total_passes_end == _total_passes
            elif _posn != 'middle':
                assert len(_gaps) == 1
                assert _gaps[0] == _gap
                assert _PHLITE == {'a': False}
                assert _IS_LOGSPACE == {'a': _gap}
                assert _shift_ctr_end == _shift_ctr + 1
                if _tpih:
                    assert _total_passes_end == _total_passes
                else:
                    # a shift was done, insert new points
                    _points.insert(_pass, len(_GRIDS[_pass]['a']))
                    assert _total_passes_end == _total_passes + 1

        _points[_pass] = len(_log_GRID)

        assert _params == {'a': [_grid, _points, _type]}



class TestHardSoftFixedShrinkPass:

    # verify hard, soft, & fixed shrink pass

    @pytest.mark.parametrize('_space, _gap',
        (('linspace', 'na'), ('logspace', 1.0), ('logspace', 2.0))
    )
    @pytest.mark.parametrize('_type',
        ('hard_float', 'hard_integer', 'soft_integer', 'soft_float',
         'fixed_integer', 'fixed_float')
    )
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_pass, _total_passes, _shrink_pass',
        (
         (1, 4, 1), (1, 4, 2), (1, 4, 3), (2, 4, 1), (2, 4, 2),
         (2, 4, 3), (3, 4, 1), (3, 4, 2), (3, 4, 3))
    )
    @pytest.mark.parametrize('_shift_ctr', (0,))
    @pytest.mark.parametrize('_tpih', (True, False))
    def test_hard_soft_fixed_shrink_pass(
        self, _space, _gap, _type, _posn, _pass, _total_passes,
        _shrink_pass, _shift_ctr, _tpih
    ):


        if 'soft' in _type and _posn in ['left', 'right']:
            # below, PHLITE is set to True when 'middle', forcing a shift
            pytest.skip(reason=f"cannot have a shrink when wants to shift")


        if _space == 'linspace':
            _grid = [40, 50, 60, 70]
        elif _space == 'logspace':
            _grid = np.logspace(0, int(3 * _gap), 4).tolist()

        if 'int' in _type:
            _grid = list(map(int, _grid))
        elif 'float' in _type:
            _grid = list(map(float, _grid))

        if _posn == 'left':
            _best = _grid[0]
        elif _posn == 'middle':
            _best = _grid[1]
        elif _posn == 'right':
            _best = _grid[-1]

        _GRIDS = {}
        for _pass_ in range(_pass):
            _GRIDS[_pass_] = {}
            if _pass_ < _shrink_pass - 1:
                _GRIDS[_pass_]['a'] = _grid
            else:
                _GRIDS[_pass_]['a'] = [_best]


        _points = []
        for _pass_ in range(_total_passes):
            if _pass_ < _shrink_pass - 1:
                _points.append(len(_grid))
            else:
                _points.append(1)

        if 'soft' in _type:
            _PHLITE = {'a': True if _posn == 'middle' else False}
        elif 'hard' in _type or 'fixed' in _type:
            _PHLITE = {}

        if _space == 'logspace' and len(_GRIDS[_pass-1]['a']) > 1:
            _IS_LOGSPACE = {'a': _gap}
        else:
            _IS_LOGSPACE = {'a': False}

        _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr_end, _total_passes_end = \
            _get_next_param_grid(
                _GRIDS=_GRIDS,
                _params={'a': [_grid, _points, _type]},
                _PHLITE=_PHLITE,
                _IS_LOGSPACE=_IS_LOGSPACE,
                _best_params_from_previous_pass={'a': _best},
                _pass=_pass,
                _total_passes=_total_passes,
                _total_passes_is_hard=_tpih,
                _shift_ctr=_shift_ctr,
                _max_shifts=10
            )

        if _pass >= _shrink_pass - 1:
            assert len(_GRIDS[_pass]['a']) == 1
            assert _points[_pass] == 1
        else:
            assert len(_GRIDS[_pass]['a']) == _params['a'][1][_pass]
            if _gap == 2 and 'fixed' not in _params['a'][-1]:
                # 'hard' or 'soft' logspace gap > 1 before shrink pass,
                # wants to regap, which is changing len grid.
                pass
            else:
                assert len(_GRIDS[_pass]['a']) == len(_grid)
                assert _points[_pass] == len(_grid)

        assert _shift_ctr_end == _shift_ctr
        assert _total_passes_end == _total_passes


class TestDrill:

    @pytest.mark.parametrize('_type', ('soft_float', 'soft_integer'))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_pass', ((1, 2, 3)))
    @pytest.mark.parametrize('_total_passes', (4,))
    @pytest.mark.parametrize('_shift_ctr', (0, 1, 2, 3))
    @pytest.mark.parametrize('_max_shifts', (3, ))
    @pytest.mark.parametrize('_tpih', (True, False))
    def test_soft_drill(
        self, _type, _space, _posn, _pass, _total_passes, _shift_ctr,
        _max_shifts, _tpih
    ):

        # soft only drills if landed in the middle or reached max shifts

        if _shift_ctr < _max_shifts and _posn in ['left', 'right']:
            pytest.skip(reason=f"this is shift not a drill")

        if _space == 'linspace':
            _grid = [50, 60, 70, 80]
            _IS_LOGSPACE = {'a': False}
        elif _space == 'logspace':
            _grid = np.logspace(1, 4, 4).tolist()
            _IS_LOGSPACE = {'a': True}

        if 'int' in _type:
            _grid = list(map(int, _grid))
            _univ_bound = 1
        elif 'float' in _type:
            _grid = list(map(float, _grid))
            _univ_bound = 0

        _points = [4 for _ in range(_total_passes)]

        _PHLITE = {'a': False}
        if _posn == 'left':
            best_idx = 0
        elif _posn == 'middle':
            _PHLITE = {'a': True}
            best_idx = 1
        elif _posn == 'right':
            best_idx = -1

        _GRIDS = {i: {'a': _grid} for i in range(_pass)}

        _params = {'a': [_grid, _points, _type]}

        _out_GRIDS, _out_params, _out_PHLITE, _out_IS_LOGSPACE, \
            _out_shift_ctr, _out_total_passes = \
                _get_next_param_grid(
                    _GRIDS=_GRIDS,
                    _params=_params,
                    _PHLITE=_PHLITE,
                    _IS_LOGSPACE=_IS_LOGSPACE,
                    _best_params_from_previous_pass={'a': _grid[best_idx]},
                    _pass=_pass,
                    _total_passes=_total_passes,
                    _total_passes_is_hard=_tpih,
                    _shift_ctr=_shift_ctr,
                    _max_shifts=_max_shifts
                )

        for _past_pass in range(_pass):
            assert _out_GRIDS[_past_pass] == _GRIDS[_past_pass]

        _new_grid = _out_GRIDS[_pass]['a']
        assert min(_new_grid) >= _univ_bound

        if _posn == 'left':
            assert max(_new_grid) <= _grid[1]
            if _space == 'linspace':
                assert min(_new_grid) >= (_grid[0] - (_grid[1] - _grid[0]))

        elif _posn == 'middle':
            assert max(_new_grid) <= _grid[2]
            if _space == 'linspace':
                assert min(_new_grid) >= _grid[0]

        elif _posn == 'right':
            if _space == 'linspace':
                assert min(_new_grid) >= _grid[-2]
                assert max(_new_grid) <= _grid[-1] + (_grid[-1] - _grid[-2])
            if _space == 'logspace':
                _log_grid = np.log10(_grid)
                _new_max = 10**(_log_grid[-1] + (_log_grid[-1] - _log_grid[-2]))
                assert max(_new_grid) <= _new_max


        assert _params['a'][1][_pass] == len(_new_grid)
        if 'int' in _type:
            # unpredictable new points
            pass
        elif 'float' in _type:
            assert _out_params == _params
        if _posn in ['middle'] or _shift_ctr == _max_shifts:
            assert _out_PHLITE == {'a': True}
        else:
            assert _out_PHLITE == {'a': False}
        assert _out_IS_LOGSPACE == {'a': False}  # logspaces convert to linspace
        assert _out_shift_ctr == _shift_ctr # no shifts
        assert _out_total_passes == _total_passes  # no shifts



    @pytest.mark.parametrize('_type', ('hard_float', 'hard_integer'))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_pass', ((1, 2, 3)))
    @pytest.mark.parametrize('_total_passes', (4,))
    @pytest.mark.parametrize('_shift_ctr', (0, 1, 2, 3))
    @pytest.mark.parametrize('_max_shifts', (3, ))
    @pytest.mark.parametrize('_tpih', (True, False))
    def test_hard_drill(
        self, _type, _space, _posn, _pass, _total_passes,
        _shift_ctr, _max_shifts, _tpih
    ):

        # hard always drills

        if _space == 'linspace':
            _grid = [50, 60, 70, 80]
            _IS_LOGSPACE = {'a': False}
        elif _space == 'logspace':
            _grid = np.logspace(1, 4, 4).tolist()
            _IS_LOGSPACE = {'a': True}

        if 'int' in _type:
            _grid = list(map(int, _grid))
            _univ_bound = 1
        elif 'float' in _type:
            _grid = list(map(float, _grid))
            _univ_bound = 0

        _points = [4 for _ in range(_total_passes)]

        if _posn == 'left':
            best_idx = 0
        elif _posn == 'middle':
            _PHLITE = {'a': True}
            best_idx = 1
        elif _posn == 'right':
            best_idx = -1

        _GRIDS = {i: {'a': _grid} for i in range(_pass)}

        _params = {'a': [_grid, _points, _type]}

        _out_GRIDS, _out_params, _out_PHLITE, _out_IS_LOGSPACE, \
            _out_shift_ctr, _out_total_passes = \
                _get_next_param_grid(
                    _GRIDS=_GRIDS,
                    _params=_params,
                    _PHLITE={},
                    _IS_LOGSPACE=_IS_LOGSPACE,
                    _best_params_from_previous_pass={'a': _grid[best_idx]},
                    _pass=_pass,
                    _total_passes=_total_passes,
                    _total_passes_is_hard=_tpih,
                    _shift_ctr=_shift_ctr,
                    _max_shifts=_max_shifts
                )

        for _past_pass in range(_pass):
            assert _out_GRIDS[_past_pass] == _GRIDS[_past_pass]

        _new_grid = _out_GRIDS[_pass]['a']
        assert min(_new_grid) >= _univ_bound

        if _posn == 'left':
            assert max(_new_grid) <= _grid[1]
            if _space == 'linspace':
                assert min(_new_grid) >= (_grid[0] - (_grid[1] - _grid[0]))

        elif _posn == 'middle':
            assert max(_new_grid) <= _grid[2]
            if _space == 'linspace':
                assert min(_new_grid) >= _grid[0]

        elif _posn == 'right':
            if _space == 'linspace':
                assert min(_new_grid) >= _grid[-2]
                assert max(_new_grid) <= _grid[-1] + (_grid[-1] - _grid[-2])
            if _space == 'logspace':
                _log_grid = np.log10(_grid)
                _new_max = 10**(_log_grid[-1] + (_log_grid[-1] - _log_grid[-2]))
                assert max(_new_grid) <= _new_max


        assert _params['a'][1][_pass] == len(_new_grid)
        if 'int' in _type:
            # unpredictable new points
            pass
        elif 'float' in _type:
            assert _out_params == _params

        assert _out_PHLITE == {}
        assert _out_IS_LOGSPACE == {'a': False}  # logspaces convert to linspace
        assert _out_shift_ctr == _shift_ctr # no shifts
        assert _out_total_passes == _total_passes  # no shifts



class TestMultiPass:

    @pytest.mark.parametrize('_shrink_pass', (2, 3, 4, None))
    @pytest.mark.parametrize('_best_posn', (0, 1, -1))
    @pytest.mark.parametrize('_total_passes', (2, 4))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    def test_fixed_and_string(
        self, _shrink_pass, _best_posn, _total_passes, _tpih, _max_shifts
    ):

        # fixed & string never increment total_passes or shift_ctr

        _params = {
            'fixed_integer_lin': [[],[], 'fixed_integer'],
            'fixed_integer_log1': [[], [], 'fixed_integer'],
            'fixed_integer_log2': [[], [], 'fixed_integer'],
            'fixed_float_lin': [[],[], 'fixed_float'],
            'fixed_float_log1': [[], [], 'fixed_float'],
            'fixed_float_log2': [[], [], 'fixed_float'],
            'string': [[], None, 'fixed_string'],
            'bool': [[], None, 'fixed_bool']
        }

        for _param in _params:
            if 'string' in _param:
                _grid = ['w', 'x', 'y', 'z']
            elif 'bool' in _param:
                _grid = [True, False]
            elif 'lin' in _param:
                _grid = [40, 50, 60, 70]
            elif 'log1' in _param:
                _grid = np.logspace(0, 3, 4).tolist()
            elif 'log2' in _param:
                _grid = np.logspace(0, 6, 4).tolist()

            if 'int' in _param:
                _grid = list(map(int, _grid))
            elif 'float' in _param:
                _grid = list(map(float, _grid))

            _params[_param][0] = _grid

            if _param in ['fixed_string', 'fixed_bool']:
                _params[_param][1] = _shrink_pass
            else:
                _shrink_pass = _shrink_pass or 1_000_000
                _points = [len(_grid) for _ in range(_total_passes)]
                _points[_shrink_pass - 1:] = [1 for _ in _points[_shrink_pass - 1:]]

                _params[_param][1] = _points
                del _points

        _GRIDS = {0: {_param: _params[_param][0] for _param in _params}}

        _PHLITE = {}

        # see _build_is_logspace, fixed logspace is not "logspace"
        _IS_LOGSPACE = {_param: False for _param in _params}

        _start_GRIDS = deepcopy(_GRIDS)
        _start_params = deepcopy(_params)
        _start_PHLITE = {}
        _start_IS_LOGSPACE = deepcopy(_IS_LOGSPACE)
        _start_total_passes = _total_passes

        _best_params = {_param: _params[_param][0][_best_posn] for _param in _params}

        for _pass in range(1, _total_passes):

            _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes = \
                _get_next_param_grid(
                    _GRIDS=_GRIDS,
                    _params=_params,
                    _PHLITE=_PHLITE,
                    _IS_LOGSPACE=_IS_LOGSPACE,
                    _best_params_from_previous_pass=_best_params,
                    _pass=_pass,
                    _total_passes=_total_passes,
                    _total_passes_is_hard=_tpih,
                    _shift_ctr=0,
                    _max_shifts=_max_shifts
                )

            assert list(_GRIDS) == list(range(_pass+1))
            assert _GRIDS[0] == _start_GRIDS[0]
            for _past_pass in range(1, _pass):
                if _past_pass < ((_shrink_pass or 1_000_000) - 1):
                    assert _GRIDS[_past_pass] == _GRIDS[0]
                elif _past_pass >= ((_shrink_pass or 1_000_000) - 1):
                    _exp = dict((
                        zip(_best_params.keys(),
                        [[_] for _ in _best_params.values()])
                    ))
                    assert _GRIDS[_past_pass] == _exp
                    del _exp

            for _param in _params:
                _param_value = _params[_param]
                if _params[_param][-1] not in ['fixed_string', 'fixed_bool']:
                    assert _param_value == _start_params[_param]
                else:
                    assert _param_value[0] == _start_params[_param][0]
                    assert _param_value[1] == \
                       (_start_params[_param][1] or 1_000_000)
                    assert _param_value[2] == _start_params[_param][2]
            assert _PHLITE == _start_PHLITE == {}
            assert _IS_LOGSPACE == _start_IS_LOGSPACE == \
                   {_param: False for _param in _params}
            assert _shift_ctr == 0
            assert _total_passes == _start_total_passes


    @pytest.mark.parametrize('_shrink_pass', (2, 3, 4, None))
    @pytest.mark.parametrize('_best_posn', (0, 1, -1))
    @pytest.mark.parametrize('_total_passes', (2, 4))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    def test_hard(
        self, _shrink_pass, _best_posn, _total_passes, _tpih, _max_shifts
    ):

        # hard never increments total_passes or shift_ctr

        _params = {
            'hard_integer_lin': [[], [], 'hard_integer'],
            'hard_integer_log1': [[], [], 'hard_integer'],
            'hard_integer_log2': [[], [], 'hard_integer'],
            'hard_float_lin': [[], [], 'hard_float'],
            'hard_float_log1': [[], [], 'hard_float'],
            'hard_float_log2': [[], [], 'hard_float']
        }

        _shrink_pass = _shrink_pass or 1_000_000

        for _param in _params:
            if 'lin' in _param:
                _grid = [40, 50, 60, 70]
            elif 'log1' in _param:
                _grid = np.logspace(0, 3, 4).tolist()
            elif 'log2' in _param:
                _grid = np.logspace(0, 6, 4).tolist()

            if 'int' in _param:
                _grid = list(map(int, _grid))
            elif 'float' in _param:
                _grid = list(map(float, _grid))

            _params[_param][0] = _grid

            _points = [len(_grid) for _ in range(_total_passes)]
            _points[_shrink_pass - 1:] = [1 for _ in _points[_shrink_pass - 1:]]

            _params[_param][1] = _points
            del _grid, _points

        _GRIDS = {0: {_param: _params[_param][0] for _param in _params}}

        _PHLITE = {}

        _IS_LOGSPACE = {}
        for _param in _params:
            if 'log' in _param:
                _IS_LOGSPACE[_param] = float(_param[-1])
            else:
                _IS_LOGSPACE[_param] = False

        _start_GRIDS = deepcopy(_GRIDS)
        _start_params = deepcopy(_params)
        _start_PHLITE = {}
        _start_IS_LOGSPACE = deepcopy(_IS_LOGSPACE)
        _start_total_passes = _total_passes

        _best_params = {i: _params[i][0][_best_posn] for i in _params}

        for _pass in range(1, _total_passes):

            _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes = \
                _get_next_param_grid(
                    _GRIDS=_GRIDS,
                    _params=_params,
                    _PHLITE=_PHLITE,
                    _IS_LOGSPACE=_IS_LOGSPACE,
                    _best_params_from_previous_pass=_best_params,
                    _pass=_pass,
                    _total_passes=_total_passes,
                    _total_passes_is_hard=_tpih,
                    _shift_ctr=0,
                    _max_shifts=_max_shifts
                )

            # GRIDS
            assert list(_GRIDS) == list(range(_pass+1))
            assert _GRIDS[0] == _start_GRIDS[0]

            for _param in _params:
                # GRIDS
                _new_grid = _GRIDS[_pass][_param]
                _old_grid = _GRIDS[_pass - 1][_param]
                if _pass < (_shrink_pass - 1):
                    # too much complication in here with repaps and
                    # logspace -> linspace etc.  keep it simple.
                    _min = 1 if 'int' in _param else 0
                    if 'lin' in _param:
                        if _best_posn == 0:
                            assert min(_new_grid) == _old_grid[0]
                            assert max(_new_grid) <= max(_old_grid)
                        elif _best_posn == 1:
                            assert min(_new_grid) >= max(_min, _GRIDS[0][_param][0])
                            assert max(_new_grid) <= max(_old_grid)
                        elif _best_posn == -1:
                            assert min(_new_grid) >= max(_min, _GRIDS[0][_param][0])
                            assert max(_new_grid) == max(_old_grid)
                    elif 'log' in _param:
                        if _best_posn == 0:
                            assert min(_new_grid) == max(_min, _GRIDS[0][_param][0])
                            assert max(_new_grid) <= max(_old_grid)
                        elif _best_posn == 1:
                            assert min(_new_grid) >= max(_min, _GRIDS[0][_param][0])
                            assert max(_new_grid) <= max(_old_grid)
                        elif _best_posn == -1:
                            assert min(_new_grid) >= max(_min, _GRIDS[0][_param][0])
                            assert max(_new_grid) == max(_old_grid)
                    del _min
                elif _pass == (_shrink_pass - 1):
                    assert _new_grid == [_old_grid[_best_posn]]
                elif _pass > (_shrink_pass - 1):
                    assert _new_grid == _old_grid

                # params
                _param_value = _params[_param]
                assert _param_value[0] == _start_params[_param][0]
                assert len(_param_value[1]) == _total_passes
                assert _param_value[2] == _start_params[_param][2]


                # must replace _best_params with new values before looping
                if _pass <= (_shrink_pass - 2):
                    _best_params[_param] = _GRIDS[_pass][_param][_best_posn]
                # after this _best_params always stays the same


            del _new_grid, _old_grid

            # PHLITE
            assert _PHLITE == _start_PHLITE == {}

            # IS_LOGSPACE
            if _pass == 1:
                _exp = {}
                for _param in _params:
                    if _shrink_pass == 2:
                        _exp[_param] = False
                    elif _start_IS_LOGSPACE[_param] > 0:
                        _exp[_param] = 1.0
                    else:
                        _exp[_param] = False
                assert _IS_LOGSPACE == _exp
                del _exp
            else:
                assert _IS_LOGSPACE == {_param: False for _param in _params}

            # shift_ctr & total_passes
            assert _shift_ctr == 0
            assert _total_passes == _start_total_passes


    @pytest.mark.parametrize('_shrink_pass', (2, 3, 4, None))
    @pytest.mark.parametrize('_best_posn', (0, 1, -1))
    @pytest.mark.parametrize('_total_passes', (3, 4))
    @pytest.mark.parametrize('_tpih', (True, False))
    @pytest.mark.parametrize('_shift_ctr', (0,))
    @pytest.mark.parametrize('_max_shifts', (1, 3)) # dont do none, runaway condition
    def test_soft(
        self, _shrink_pass, _best_posn, _total_passes, _tpih, _shift_ctr,
        _max_shifts
    ):

        # soft can shift and increment total_passes and shift_ctr!

        _params = {
            'soft_integer_lin': [[40, 50, 60, 70], [], 'soft_integer'],
            'soft_integer_lin_0': [[1, 11, 21, 31], [], 'soft_integer'],
            'soft_integer_log1': [np.logspace(0, 3, 4).tolist(), [], 'soft_integer'],
            'soft_integer_log2': [np.logspace(0, 4, 3).tolist(), [], 'soft_integer'],
            'soft_float_lin': [[40, 50, 60, 70], [], 'soft_float'],
            'soft_float_lin_0': [[0, 10, 20, 30], [], 'soft_float'],
            'soft_float_log1': [np.logspace(-2, 2, 5).tolist(), [], 'soft_float'],
            'soft_float_log2': [np.logspace(-16, -8, 5).tolist(), [], 'soft_float']
        }

        _shrink_pass = _shrink_pass or 1_000_000

        for _param in _params:

            if 'int' in _param:
                _params[_param][0] = list(map(int, _params[_param][0]))
            elif 'float' in _param:
                _params[_param][0] = list(map(float, _params[_param][0]))

            _points = [len(_params[_param][0]) for _ in range(_total_passes)]
            _points[_shrink_pass - 1:] = [1 for _ in _points[_shrink_pass - 1:]]

            _params[_param][1] = _points
            del _points

        _GRIDS = {0: {_param: _params[_param][0] for _param in _params}}

        _PHLITE = {}
        for _param in _params:
            # all of them because all are soft
            _PHLITE[_param] = True if _best_posn == 1 else False


        _IS_LOGSPACE = {}
        for _param in _params:
            if 'log' in _param:
                _IS_LOGSPACE[_param] = float(_param[-1])
            else:
                _IS_LOGSPACE[_param] = False

        _start_GRIDS = deepcopy(_GRIDS)
        _start_params = deepcopy(_params)
        _start_PHLITE = deepcopy(_PHLITE)
        _start_IS_LOGSPACE = deepcopy(_IS_LOGSPACE)
        _start_total_passes = _total_passes

        _best_params = {i: _params[i][0][_best_posn] for i in _params}

        _pass = 1
        while _pass < _total_passes:

            _start_shift_ctr = _shift_ctr

            _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes = \
                _get_next_param_grid(
                    _GRIDS=_GRIDS,
                    _params=_params,
                    _PHLITE=_PHLITE,
                    _IS_LOGSPACE=_IS_LOGSPACE,
                    _best_params_from_previous_pass=_best_params,
                    _pass=_pass,
                    _total_passes=_total_passes,
                    _total_passes_is_hard=_tpih,
                    _shift_ctr=_shift_ctr,
                    _max_shifts=_max_shifts
                )



            if _shift_ctr > _start_shift_ctr:
                _shrink_pass += 1

            # GRIDS
            assert list(_GRIDS) == list(range(_pass+1))
            assert _GRIDS[0] == _start_GRIDS[0]

            for _param in _params:
                # GRIDS
                _new_grid = _GRIDS[_pass][_param]
                _old_grid = _GRIDS[_pass - 1][_param]
                if _pass < (_shrink_pass - 1):
                    # these need to be really wide shifts drills and regaps
                    # in lin & logspace
                    _min = 1 if 'int' in _param else 0
                    if 'lin' in _param:
                        _gap = _old_grid[1] - _old_grid[0]
                        if _best_posn == 0:
                            assert min(_new_grid) >= _min
                            assert max(_new_grid) <= _GRIDS[0][_param][-1]
                        elif _best_posn == 1:
                            assert min(_new_grid) >= _old_grid[0]
                            assert max(_new_grid) <= _GRIDS[0][_param][-1]
                        elif _best_posn == -1:
                            assert min(_new_grid) >= _min
                            assert max(_new_grid) <= _old_grid[-1] + _gap * 2
                    elif 'log' in _param:
                        _log_old_grid = np.log10(_old_grid)
                        _log_gap = int((_log_old_grid[1:]-_log_old_grid[:-1])[0])
                        if _best_posn == 0:
                            assert min(_new_grid) >= _min
                            assert max(_new_grid) <= _GRIDS[0][_param][-1]
                        elif _best_posn == 1:
                            assert min(_new_grid) >= _min
                            assert max(_new_grid) <= _GRIDS[0][_param][-1]
                        elif _best_posn == -1:
                            assert min(_new_grid) >= _min
                            assert max(_new_grid) <= \
                                   10**(_log_old_grid[-1] + _gap * 2)
                        del _min
                elif _pass == (_shrink_pass - 1):
                    assert _new_grid == [_old_grid[_best_posn]]
                elif _pass > (_shrink_pass - 1):
                    assert _new_grid == _old_grid

                # params
                _param_value = _params[_param]
                assert _param_value[0] == _start_params[_param][0]
                assert len(_param_value[1]) == _total_passes
                assert _param_value[2] == _start_params[_param][2]


                # must replace _best_params with new values before looping
                if _pass <= (_shrink_pass - 2):
                    _best_params[_param] = _GRIDS[_pass][_param][_best_posn]
                # after this _best_params always stays the same

            del _new_grid, _old_grid

            if _shift_ctr > _max_shifts:
                raise Exception

            # PHLITE
            if _start_shift_ctr == _max_shifts:
                assert _PHLITE == {_param: True for _param in _params}
            elif _pass >= (_shrink_pass - 1):
                assert _PHLITE == {_param: True for _param in _params}
            elif _start_shift_ctr > _max_shifts:
                raise Exception
            else:
                if _best_posn == 1:
                    assert _PHLITE == {_param: True for _param in _params}
                elif _best_posn == -1:
                    assert _PHLITE == {_param: False for _param in _params}
                elif _best_posn == 0:
                    _exp = {}
                    for _param in _params:
                        _univ_bound = 1 if 'int' in _param else 0
                        if _GRIDS[_pass - 1][_param][0] == _univ_bound:
                            _exp[_param] = True
                        else:
                            _exp[_param] = False

                    assert _PHLITE == _exp


            # IS_LOGSPACE
            _exp = {}
            if _pass >= _shrink_pass - 1:
                _exp = {_param: False for _param in _params}
            elif _start_shift_ctr == _max_shifts:
                if _pass == _max_shifts + 1:
                    _exp = {i: bool(_start_IS_LOGSPACE[i]) for i in _params}
                elif _pass > _max_shifts + 1:
                    _exp = {_param: False for _param in _params}
            elif _start_shift_ctr > _max_shifts:
                raise Exception
            elif _best_posn == -1:
                _exp = {_param: _start_IS_LOGSPACE[_param] for _param in _params}
            elif _best_posn == 1:
                if _pass == 1:
                    _exp = {i: bool(_start_IS_LOGSPACE[i]) for i in _params}
                elif _pass > 1:
                    _exp = {_param: False for _param in _params}
            elif _best_posn == 0:

                for _param in _IS_LOGSPACE:
                    if _start_IS_LOGSPACE[_param] is False:
                        _exp[_param] = False
                    # must be log
                    elif 'float' in _param:
                        _exp[_param] = _start_IS_LOGSPACE[_param]
                    elif 'int' in _param:
                        _exp[_param] = bool(_start_IS_LOGSPACE[_param])

            assert _IS_LOGSPACE == _exp

            del _exp

            # shift_ctr
            if _best_posn == 1:
                assert _shift_ctr == 0
            elif _best_posn == -1:
                if _start_shift_ctr < _max_shifts:
                    assert _shift_ctr == _pass
                else:
                    assert _shift_ctr == _max_shifts
            elif _best_posn == 0:
                if _start_shift_ctr == _max_shifts:
                    assert _shift_ctr == _max_shifts
                elif _start_shift_ctr < _max_shifts:  # havent reached max shifts
                    _any_shifted = 0
                    for _param in _params:
                        _univ_bound = 0 if 'float' in _param else 1
                        if _GRIDS[_pass-1][_param][0] == _univ_bound:
                            pass
                        else:
                            _any_shifted += 1

                    if not _any_shifted:
                        assert _shift_ctr == _start_shift_ctr
                    elif _any_shifted:
                        assert _shift_ctr == _pass
                else:
                    raise Exception(f"shift ctr > max shifts!")

            # total_passes
            if _tpih or _best_posn == 1:
                assert _total_passes == _start_total_passes
            elif _best_posn == -1:
                if _start_shift_ctr < _max_shifts:
                    assert _total_passes == _start_total_passes + _pass
                elif _start_shift_ctr >= _max_shifts:
                    assert _total_passes == _start_total_passes + _max_shifts
            else:  # _best_posn == 0
                _was_shifted = 0
                for _param in _params:
                    _univ_bound = 1 if 'int' in _param else 0
                    if _GRIDS[_pass - 1][_param][0] != _univ_bound:
                        _was_shifted += 1
                if _was_shifted:
                    assert _total_passes == \
                           (_start_total_passes + min(_pass, _max_shifts))
                else:
                    assert _total_passes == _start_total_passes


            _pass += 1


