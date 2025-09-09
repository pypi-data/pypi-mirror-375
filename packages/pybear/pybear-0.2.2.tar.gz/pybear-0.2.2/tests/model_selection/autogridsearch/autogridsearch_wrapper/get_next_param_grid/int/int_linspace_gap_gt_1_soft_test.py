# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid. _int._int_linspace_gap_gt_1_soft import \
    _int_linspace_gap_gt_1_soft



class TestIntLinspaceGapGT1Soft:


    # no _validation


    # unit gap only to test for robustness against span falling below 2
    @pytest.mark.parametrize('grid',
        ([1,3,5], [10,20,30], [10, 15, 25], [3,4,5])
    )
    @pytest.mark.parametrize('posn', ('left', 'right', 'middle'))
    def test_accuracy(self, grid, posn):

        POSN_DICT = {'left':0, 'middle':1, 'right':len(grid)-1}
        _posn = POSN_DICT[posn]
        _best = grid[_posn]

        _left, _right = _int_linspace_gap_gt_1_soft(grid, _posn)

        # _left always above universal min
        assert _left >= 1

        if posn == 'left':
            if _left != 1:
                assert _left == (grid[0] - (grid[1] - grid[0]))

            assert _right == max(grid[1] - 1, grid[0] + 1)

        elif posn == 'right':

            assert _left == min(grid[-2] + 1, grid[-1] - 1)

            assert _right == (grid[-1] + (grid[-1] - grid[-2]))

        elif posn == 'middle':

            assert _left >= min(grid[0] + 1, grid[1] - 1)

            assert _right <= max(grid[-1] - 1, grid[1] + 1)








