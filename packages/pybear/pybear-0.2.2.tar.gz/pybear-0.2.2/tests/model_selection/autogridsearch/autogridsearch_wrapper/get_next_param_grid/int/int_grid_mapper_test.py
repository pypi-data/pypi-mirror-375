# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_grid_mapper import _int_grid_mapper



class TestIntGridMapper:


    # _validation handled by _int_linspace_gap_gt_1, which is handled by
    # _validate_int_float_linlogspace


    @pytest.mark.parametrize('_left, _right',
        ((1,2), (1,3), (1,4), (1, 10), (10, 50), (13, 37)))
    @pytest.mark.parametrize('_points',
        (2, 4, 8, 16, 32, 64)
    )
    def test_accuracy(self, _left, _right, _points):

        _out_grid = _int_grid_mapper(_left, _right, _points)

        assert _out_grid[0] == _left

        assert _out_grid[-1] == _right

        if _points > (_right - _left + 1) / 2 or (_right - _left) in [2,3,4]:
            assert len(_out_grid) == (_right - _left + 1)
        else:
            assert len(_out_grid) >= _points
            assert len(_out_grid) < (_right - _left + 1)











