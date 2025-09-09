# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_linspace_gap_gt_1_hard import \
    _int_linspace_gap_gt_1_hard



class TestIntLinspaceGapGT1Hard:

    # _validate_int_float_linlogspace is handling this check before
    # _int_linspace_gap_gt_1_hard, but do it here too anyway
    def test_rejects_hard_min_lt_0(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1_hard([2,4,6], 1, -1, 10)


    def test_rejects_grid_lt_hard_min(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1_hard([10,20,30], 1, 15, 100)


    def test_rejects_grid_gt_hard_max(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1_hard([10,20,30], 1, 1, 25)


    # unit gap only to tests for robustness against span falling below 2
    @pytest.mark.parametrize('grid',
        ([11,13,15], [10,20,30], [10, 15, 25], [10,11,12])
    )
    @pytest.mark.parametrize('posn', ('left', 'right', 'middle'))
    @pytest.mark.parametrize('hard_min, hard_max',
        ((10, 30), (10, 50), (1, 50), (1, 30))
    )
    def test_accuracy(self, grid, posn, hard_min, hard_max):

        POSN_DICT = {'left':0, 'middle':1, 'right':len(grid)-1}
        _posn = POSN_DICT[posn]
        _best = grid[_posn]

        _left, _right = _int_linspace_gap_gt_1_hard(
            grid,
            _posn,
            hard_min,
            hard_max
        )

        # _left always above hard min
        assert _left >= hard_min

        if posn == 'left':
            if _left != 1:
                assert _left == max(hard_min, (grid[0] - (grid[1] - grid[0])))

            assert _right == min(hard_max, max(grid[1] - 1, grid[0] + 1))

        elif posn == 'right':

            assert _left == max(hard_min, min(grid[-2] + 1, grid[-1] - 1))

            assert _right == min(hard_max, (grid[-1] + (grid[-1] - grid[-2])))

        elif posn == 'middle':

            assert _left >= max(hard_min, min(grid[0] + 1, grid[1] - 1))

            assert _right <= min(hard_max, max(grid[-1] - 1, grid[1] + 1))








