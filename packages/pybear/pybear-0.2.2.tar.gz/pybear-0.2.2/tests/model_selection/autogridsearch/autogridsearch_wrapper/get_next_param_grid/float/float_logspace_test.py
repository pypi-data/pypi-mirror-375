# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._float._float_logspace import _float_logspace



class TestFloatLogspace:

    # _validation handled by
    # get_next_param_grid._validate_int_float_linlogspace

    @pytest.mark.parametrize('_GRID',
         (
            list(map(float, np.logspace(2, 6, 3).tolist())),
            list(map(float, np.logspace(0, 2, 3).tolist())),
            list(map(float, np.logspace(-5, 5, 11).tolist())),
          )
    )
    @pytest.mark.parametrize('_is_hard', (True, False))
    @pytest.mark.parametrize('_posn_', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_points', (3, 5, 10))
    def test_accuracy(self, _GRID, _is_hard, _posn_, _points):

        _POSN = {'left': 0, 'right': len(_GRID) - 1, 'middle': 1}
        _posn = _POSN[_posn_]

        _hard_min = _GRID[0]
        _hard_max = _GRID[-1]

        __ = np.log10(_GRID)
        _is_logspace = np.unique(__[1:] - __[:-1])[0]
        _is_logspace = __[1] - __[0]
        del __

        # ** * ** * ** * ** * ** * ** *

        out_grid = _float_logspace(
            _GRID,
            _posn,
            _is_logspace,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )

        # ** * ** * ** * ** * ** * ** *

        assert isinstance(out_grid, list)

        assert isinstance(out_grid[0], float)


        # gives correct len (== number of points)
        assert len(out_grid) == _points


        # interval is always constant
        __ = np.array(out_grid)
        _gaps = np.unique(np.round((__[1:] - __[:-1]), 6))
        assert len(_gaps) == 1

        del __, _gaps


        # min is always >= zero
        assert min(out_grid) >= 0


        if _is_hard:
            # if is_hard, min is always >= hard_min, max is always <= hard max

            if _posn == 'left':
                assert min(out_grid) == max(0, _hard_min)
                assert max(out_grid) == _GRID[1]

            elif _posn == 'right':
                assert min(out_grid) == max(0, _hard_min)
                assert max(out_grid) == _hard_max

            # for middle posn, min is always > left number,
            #   max is always < right number
            elif _posn == 'middle':
                assert min(out_grid) > _GRID[_posn-1]
                assert max(out_grid) < _GRID[_posn+1]

        elif not _is_hard:
            # if soft & left, new min < original min
            if _posn == 'left':
                assert min(out_grid) < min(_GRID)

            # if soft & right, new max > original max
            elif _posn == 'right':
                assert max(out_grid) > max(_GRID)

            # for middle posn, min is always > left number,
            #   max is always < right number
            elif _posn == 'middle':
                assert min(out_grid) > _GRID[_posn-1]
                assert max(out_grid) < _GRID[_posn+1]







