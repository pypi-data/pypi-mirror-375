# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_linspace_unit_gap import \
    _int_linspace_unit_gap



class TestIntLinspaceUnitGap:


    # _validation handled by get_next_param_grid._validate_int_float_linlogspace


    @pytest.mark.parametrize('_SINGLE_GRID',
        (np.linspace(3, 7, 5),
        np.linspace(10, 25, 16)),
    )
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_is_hard', (True, False))
    @pytest.mark.parametrize('_hard_min', (1, 3))
    @pytest.mark.parametrize('_hard_max', (25, 30))
    @pytest.mark.parametrize('_points', (3, 10, 20))
    def test_accuracy(
        self, _SINGLE_GRID, _posn, _is_hard, _hard_min, _hard_max, _points
    ):

        _POSN = {'left':0, 'middle':1, 'right':len(_SINGLE_GRID)-1}
        _posn_ = _POSN[_posn]

        _grid_out = _int_linspace_unit_gap(
            _SINGLE_GRID,
            _posn_,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )

        assert isinstance(_grid_out, list)
        assert isinstance(_grid_out[0], int)

        if _points > 1:
            __ = np.array(_grid_out)
            _gaps = np.unique(__[1:] - __[:-1])
            del __
            assert len(_gaps) == 1
            assert _gaps[0] == 1


        assert min(_grid_out) >= 1

        if _is_hard:
            assert min(_grid_out) >= _hard_min
            assert max(_grid_out) <= _hard_max

            if _posn == 'left':
                assert min(_grid_out) == max(_hard_min, _SINGLE_GRID[0] - 1)
                assert max(_grid_out) == min(
                    _hard_max, max(_hard_min, _SINGLE_GRID[0] - 1) + _points - 1
                )

            if _posn == 'right':
                assert min(_grid_out) == max(
                    _hard_min, min(_hard_max, _SINGLE_GRID[-1] + 1) - _points + 1
                )
                assert max(_grid_out) == min(
                    _hard_max, max(_SINGLE_GRID[-1] + 1, _hard_min + _points - 1)
                )

            if _posn == 'middle':
                assert _SINGLE_GRID[_posn_] in _grid_out


        elif not _is_hard:
            assert len(_grid_out) == _points

            if _posn == 'left':
                assert min(_grid_out) == max(1, _SINGLE_GRID[0] - 1)
                assert max(_grid_out) == max(1, _SINGLE_GRID[0] - 1) + _points - 1

            if _posn == 'right':
                assert min(_grid_out) == \
                    max(_SINGLE_GRID[-1] + 1, _points) - _points + 1
                assert max(_grid_out) == max(_SINGLE_GRID[-1] + 1, _points)

            if _posn == 'middle':
                assert _SINGLE_GRID[_posn_] in _grid_out
                if min(_grid_out) != 1:
                    _num_left = _SINGLE_GRID[_posn_] - min(_grid_out)
                    _num_right = max(_grid_out) - _SINGLE_GRID[_posn_]
                    assert abs(_num_left - _num_right) in [0, 1]






