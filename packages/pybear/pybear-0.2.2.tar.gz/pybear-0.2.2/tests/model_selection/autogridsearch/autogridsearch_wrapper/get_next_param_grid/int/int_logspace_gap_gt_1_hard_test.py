# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np
from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_logspace_gap_gt_1_hard import \
    _int_logspace_gap_gt_1_hard



class TestIntLogspaceGapGT1Hard:


    # def _int_logspace_gap_gt_1_hard(
    #     _LOG_SINGLE_GRID: npt.NDArray[np.float64],
    #     _is_logspace: LogspaceType,
    #     _posn: int,
    #     _log_hard_min: np.float64,
    #     _log_hard_max: np.float64
    # ) -> tuple[np.float64, np.float64]:


    @pytest.mark.parametrize('non_ndarray, gap',
        (([2,3,4], 1), ((1,3,5), 2), ({2,4,6}, 2))
    )
    def test_rejects_non_nd_array(self, non_ndarray, gap):
        with pytest.raises(TypeError):
            _int_logspace_gap_gt_1_hard(non_ndarray, gap, 1, 0, 10)


    def test_rejects_negative_log_search_values(self):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_hard(
                np.array([-4,-3,-2]).astype(int), 1, 1, -10, 10
            )


    @pytest.mark.parametrize('_gap', (1.0, 3.0, 4.0))
    @pytest.mark.parametrize('_posn', (0, 1, 2))
    def test_reject_log_gap_and_is_logspace_not_equal(self, _gap, _posn):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_hard(
                np.array([0,2,4], dtype=int), _gap, _posn, 0, 4
            )


    def test_rejects_grid_lt_hard_min(self):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_hard(
                np.array([2,4,6], dtype=int), 2.0, 1, 3, 20
            )


    def test_rejects_grid_gt_hard_max(self):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_hard(
                np.array([2,4,6], dtype=int), 2.0, 1, 0, 5
            )


    def test_rejects_log_hard_min_lt_0(self):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_hard(
                np.array([2,4,6], dtype=int), 2.0, 1, -1, 10
            )


    # remember search grids are in logspace!
    @pytest.mark.parametrize('grid, gap',
        (
            ([11,13,15], 2.0),
            ([10,20,30], 10.0),
            ([1, 2, 3], 1.0),
            ([1, 3, 5], 2.0),
            ([10,11,12], 1.0)
        )
    )
    @pytest.mark.parametrize('posn', ('left', 'right', 'middle'))
    @pytest.mark.parametrize('hard_min, hard_max',
        ((0, 30), (0, 50), (1, 50), (1, 30))
    )
    def test_accuracy(self, grid, gap, posn, hard_min, hard_max):

        POSN_DICT = {'left':0, 'middle':1, 'right':len(grid)-1}
        _posn = POSN_DICT[posn]
        _best = grid[_posn]

        _left, _right = _int_logspace_gap_gt_1_hard(
            np.array(grid, dtype=int),
            gap,
            _posn,
            hard_min,
            hard_max
        )

        # _left always above hard min
        assert _left >= hard_min

        if posn == 'left':
            assert _left == max(hard_min, 0)
            assert _right == min(hard_max, max(grid[1], grid[0] + 1))

        elif posn == 'right':
            assert _left == max(hard_min, 0)
            assert _right == min(hard_max, (grid[-1] + (grid[-1] - grid[-2])))

        elif posn == 'middle':
            assert _left == max(hard_min, 0)
            assert _right == min(hard_max, max(grid[2], grid[1] + 1))








