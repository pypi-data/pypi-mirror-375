# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._float._float import _float



class TestFloat:


    @pytest.mark.parametrize('_GRID',
         (
            list(map(float, np.linspace(100, 200, 11).tolist())),
            list(map(float, np.linspace(0, 2, 3).tolist())),
            list(map(float, np.linspace(10, 30, 3).tolist())),
            list(map(float, np.logspace(1, 3, 3).tolist())),
            list(map(float, np.logspace(1, 5, 2).tolist())),
            list(map(float, np.logspace(-4, 4, 5).tolist())),
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

        _ = np.log10(_GRID)
        __ = np.unique(_[1:] - _[:-1])
        if len(__) == 1:
            _is_logspace = __[0]
        else:
            _is_logspace = False


        out_grid, logspace_out =  _float(
            _GRID,
            _is_logspace,
            _posn,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )


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

        # if is_hard, min is always >= hard_min, max is always <= hard max
        if _is_hard:
            assert min(out_grid) >= _hard_min
            assert max(out_grid) <= _hard_max

        # for middle posn, min is always > left number,
        #   max is always < right number
        if _posn == 'middle':
            assert min(out_grid) > _GRID[_posn-1]
            assert max(out_grid) < _GRID[_posn+1]

        # if soft & left, new min < original min
        if not _is_hard and _posn == 'left':
            assert min(out_grid) < min(_GRID)

        # if soft & right, new max > original max
        if not _is_hard and _posn == 'right':
            assert max(out_grid) > max(_GRID)



        assert logspace_out is False








