# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int import _int



class TestInt:

    # def _int(
    #     _SINGLE_GRID: IntGridType,
    #     _is_logspace: LogspaceType,
    #     _posn: int,
    #     _is_hard: bool,
    #     _hard_min: IntDataType,
    #     _hard_max: IntDataType,
    #     _points: int
    # ) -> tuple[IntGridType, LogspaceType]:

    # all _validation is handled in the individual modules. verify all the
    # calls work and are accurate.



    @pytest.mark.parametrize('_space, _gap, _low, _high, _points, _is_logspace',
        (
         ('linspace', 1.0, 3, 12, 10, False),
         ('linspace', 1.0, 1, 12, 12, False),
         ('linspace', 2.0, 2, 4, 3, False),
         ('logspace', 1.0, 0, 9, 10, 1.0),
         ('logspace', 1.0, 3, 12, 10, 1.0),
         ('logspace', 2.0, 2, 6, 3, 2.0)
        ),
    )
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_is_hard', (True, False))
    @pytest.mark.parametrize('_hard_min', (1, 2))
    @pytest.mark.parametrize('_hard_max', (12, 16))
    def test_accuracy(
        self, _space, _gap, _low, _high, _points, _is_logspace, _posn,
        _is_hard, _hard_min, _hard_max
    ):

        if _space == 'linspace':
            _SINGLE_GRID = np.linspace(_low, _high, _points).tolist()
        elif _space == 'logspace':
            _SINGLE_GRID = np.logspace(_low, _high, _points).tolist()
            _hard_min = 10 ** _hard_min
            _hard_max = 10 ** _hard_max

        if _hard_min == 0 and _space == 'linspace':
            pytest.skip(reason=f"expected to fail")

        if _hard_min > min(_SINGLE_GRID):
            pytest.skip(reason=f"expected to fail")


        _SINGLE_GRID = list(map(int, _SINGLE_GRID))

        _POSN = {'left':0, 'middle':1, 'right':len(_SINGLE_GRID)-1}
        _posn_ = _POSN[_posn]

        _grid_out, _is_logspace = _int(
            _SINGLE_GRID,
            _is_logspace,
            _posn_,
            _is_hard,
            _hard_min,
            _hard_max,
            (_points // 2) + 2
        )

        assert isinstance(_grid_out, list)
        assert isinstance(_grid_out[0], int)
        assert _grid_out[-1] > _grid_out[0]

        assert min(_grid_out) >= 1
        assert len(_grid_out) >= 3

        if _posn != 'right':
            assert max(_grid_out) <= max(_SINGLE_GRID)

        if _is_hard:
            assert min(_grid_out) >= _hard_min

        assert _is_logspace is False





