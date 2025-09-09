# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_logspace_gap_gt_1_soft import \
    _int_logspace_gap_gt_1_soft



class TestIntLogspaceGapGT1Soft:

    # def _int_logspace_gap_gt_1_soft(
    #     _LOG_SINGLE_GRID: npt.NDArray[np.float64],
    #     _is_logspace: LogspaceType,
    #     _posn: int
    # ) -> tuple[np.float64, np.float64]:


    @pytest.mark.parametrize('non_ndarray, gap',
        (([2,3,4], 1.0), ((1,3,5), 2.0), ({2,4,6}, 2.0))
    )
    def test_rejects_non_nd_array(self, non_ndarray, gap):
        with pytest.raises(TypeError):
            _int_logspace_gap_gt_1_soft(non_ndarray, gap, 1)


    def test_rejects_negative_log_search_values(self):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_soft(
                np.array([-4,-3,-2]).astype(int), 1.0, 1
            )


    @pytest.mark.parametrize('_gap', (1.0, 3.0, 4.0))
    @pytest.mark.parametrize('_posn', (0, 1, 2))
    def test_reject_log_gap_and_is_logspace_not_equal(self, _gap, _posn):
        with pytest.raises(ValueError):
            _int_logspace_gap_gt_1_soft(
                np.array([0,2,4], dtype=int), _gap, _posn
            )


    @pytest.mark.parametrize('grid, is_logspace',
        (
            ([1, 2, 3], 1.0),
            ([0, 2, 4], 2.0),
            ([0, 1, 2, 3], 1.0),
            ([5, 10, 15], 5.0),
            ([3, 6, 9, 12], 3.0)
        )
    )
    @pytest.mark.parametrize('posn', ('left', 'right', 'middle'))
    def test_accuracy(self, grid, is_logspace, posn):

        POSN_DICT = {'left':0, 'middle':1, 'right':len(grid)-1}
        _posn = POSN_DICT[posn]
        _best = grid[_posn]

        _left, _right = _int_logspace_gap_gt_1_soft(
            np.array(grid, dtype=int),
            is_logspace,
            _posn
        )

        # _left always above universal min
        # remember in logspace! 10**0 == 1!
        assert _left == 0

        if posn == 'left':

            assert _right == max(grid[1], grid[0] + 1)

        elif posn == 'right':

            assert _right == (grid[-1] + (grid[-1] - grid[-2]))

        elif posn == 'middle':

            assert _right == max(grid[_posn + 1], grid[_posn] + 1)




