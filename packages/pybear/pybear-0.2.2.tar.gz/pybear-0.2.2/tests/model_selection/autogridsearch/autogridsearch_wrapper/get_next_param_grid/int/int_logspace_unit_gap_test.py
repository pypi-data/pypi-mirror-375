# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np
import pytest
from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_logspace_unit_gap import \
    _int_logspace_unit_gap



class TestIntLogspaceUnitGap:

    # def _int_logspace_unit_gap(
    #     _SINGLE_GRID: IntGridType,
    #     _is_logspace: LogspaceType,
    #     _posn: int,
    #     _is_hard: bool,
    #     _hard_min: IntDataType,
    #     _hard_max: IntDataType,
    #     _points: int
    # ) -> IntGridType:


    # _validation handled by get_next_param_grid._validate_int_float_linlogspace

    # relic val from before _validate_int_float_linlogspace ** * ** * **
    def test_rejects_floats(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [10**1.1,10**1.2,10**1.3],
                1.0, 1, False, 1, 10, 3
            )


    def test_rejects_search_values_lt_1(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e-1,1e0,1e1],
                1.0, 1, False, -1, 3, 3
            )


    def test_rejects_reversed_grid(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e8,1e7,1e6],
                1.0, 1, False, -1, 3, 3
            )


    def test_rejects_duplicate_search_points(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e9,1e10,1e11,1e11],
                1.0, 0, True, 1e8, 1e18, 3
            )


    def test_rejects_invalid_posn_index(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e1,1e2,1e3,1e4],
                1.0, 4, False, 1e1, 1e4, 4
            )

        with pytest.raises(TypeError):
            _int_logspace_unit_gap(
                [1e1,1e2,1e3,1e4],
                1.0, 1.98, False, 1e1, 1e4, 4
            )


    def test_rejects_bad_hard_min(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e3,1e4,1e5,1e6],
                1.0, 3, True, 1e4, 1e18, 4
            )

        with pytest.raises(TypeError):
            _int_logspace_unit_gap(
                [1e9,1e10,1e11,1e12],
                1.0, 3, True, 10**2.14, 1e18, 4
            )


    def test_rejects_bad_hard_max(self):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e3,1e4,1e5,1e6],
                1.0, 3, True, 1e3, 1e5, 4
            )

        with pytest.raises(TypeError):
            _int_logspace_unit_gap(
                [1e2,1e3,1e4,1e5],
                1.0, 3, True, 1e1, 10**13.77, 4
            )


    @pytest.mark.parametrize('points', (0, 1, 2))
    def test_rejects_points_lte_2(self, points):
        with pytest.raises(ValueError):
            _int_logspace_unit_gap(
                [1e2,1e3,1e4,1e5],
                 1.0, 0, False, 1e2, 1e10, points
            )

    # END relic val from before _validate_int_float_linlogspace ** * **



    # correctness of soft _left & _right in int_logspace_gap_gt_1_soft
    # correctness of hard _left & _right in int_logspace_gap_gt_1_hard

    # should only need to validate number of points and how they fall

    @pytest.mark.parametrize('_low, _high, _points, _is_logspace',
        (
         (3, 12, 10, 1.0),
         (2, 4, 3, 1.0),
         (4, 11, 8, 1.0)
        ),
    )
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_is_hard', (True, False))
    @pytest.mark.parametrize('_hard_min', (1e1, 1e2))
    @pytest.mark.parametrize('_hard_max', (1e12, 1e16))
    def test_accuracy(
        self, _low, _high, _points, _is_logspace, _posn, _is_hard,
        _hard_min, _hard_max
    ):

        _SINGLE_GRID = np.logspace(_low, _high, _points).tolist()

        _SINGLE_GRID = list(map(int, _SINGLE_GRID))

        _POSN = {'left':0, 'middle':1, 'right':len(_SINGLE_GRID)-1}
        _posn_ = _POSN[_posn]

        _grid_out = _int_logspace_unit_gap(
            _SINGLE_GRID,
            _is_logspace,
            _posn_,
            _is_hard,
            _hard_min,
            _hard_max,
            _points
        )

        assert isinstance(_grid_out, list)
        assert isinstance(_grid_out[0], int)
        assert _grid_out[-1] > _grid_out[0]

        assert min(_grid_out) >= 1
        assert len(_grid_out) >= 3


        if _is_hard:

            assert min(_grid_out) >= _hard_min
            assert max(_grid_out) <= _hard_max

            if _posn == 'left':
                _gap = np.subtract(*np.log10(_SINGLE_GRID)[[1,0]])
                assert min(_grid_out) == max(_hard_min, 1)
                assert max(_grid_out) == _SINGLE_GRID[1]
                del _gap

            elif _posn == 'right':
                _gap = np.subtract(*np.log10(_SINGLE_GRID)[[-1, -2]])
                assert min(_grid_out) == max(_hard_min, 1)
                assert max(_grid_out) == \
                       min(_hard_max, 10**(np.log10(_SINGLE_GRID[-1]) + _gap))
                del _gap

            elif _posn == 'middle':
                assert min(_grid_out) == max(_hard_min, 1)
                assert max(_grid_out) == _SINGLE_GRID[_posn_ + 1]


        elif not _is_hard:

            if _posn == 'left':
                _gap = np.subtract(*np.log10(_SINGLE_GRID)[[1,0]])
                assert min(_grid_out) == 1
                assert max(_grid_out) == _SINGLE_GRID[1]
                del _gap

            elif _posn == 'right':
                _gap = np.subtract(*np.log10(_SINGLE_GRID)[[-1, -2]])
                assert min(_grid_out) == 1
                assert max(_grid_out) == 10**(np.log10(_SINGLE_GRID[-1]) + _gap)
                del _gap

            elif _posn == 'middle':
                assert min(_grid_out) == 1
                assert max(_grid_out) == _SINGLE_GRID[_posn_ + 1]








