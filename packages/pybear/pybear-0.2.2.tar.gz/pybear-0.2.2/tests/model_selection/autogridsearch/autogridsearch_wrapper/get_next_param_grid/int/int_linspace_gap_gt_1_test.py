# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._int._int_linspace_gap_gt_1 import \
    _int_linspace_gap_gt_1



class TestIntLinspaceGap_GT_1:


    # _validation handled by get_next_param_grid._validate_int_float_linlogspace

    # relic val from before _validate_int_float_linlogspace ** * ** * **
    def test_rejects_floats(self):
        with pytest.raises(TypeError):
            _int_linspace_gap_gt_1([1.1,1.2,1.3], 1, False, 1, 10, 3)


    def test_rejects_search_values_lt_1(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([-1,2,3], 1, False, -1, 3, 3)

        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([0,2,4], 1, False, 0, 4, 3)


    def test_rejects_invalid_index(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([4,8,12], 3, False, 4, 12, 4)

        with pytest.raises(TypeError):
            _int_linspace_gap_gt_1([4,8,12], 1.98, False, 4, 12, 4)


    def test_rejects_bad_hard_min(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([3,15,27,39], 3, True, 10, 39, 4)

        with pytest.raises(TypeError):
            _int_linspace_gap_gt_1([3, 15, 27, 39], 3, False, 3.14, 39, 4)


    def test_rejects_bad_hard_max(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([3,15,27,39], 3, True, 3, 31, 4)

        with pytest.raises(TypeError):
            _int_linspace_gap_gt_1([3,15,27,39], 3, False, 3, 39.77, 4)


    def test_rejects_points_lte_1(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([10,20,30,40], 0, False, 10, 40, 0)

        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([10,20,30,40], 0, False, 10, 40, 1)


    def test_rejects_duplicate_search_points(self):
        with pytest.raises(ValueError):
            _int_linspace_gap_gt_1([10,20,30,30], 0, False, 10, 40, 3)

    # END relic val from before _validate_int_float_linlogspace ** * **



    # correctness of soft _left & _right in int_linspace_gap_gt_1_soft
    # correctness of hard _left & _right in int_linspace_gap_gt_1_hard

    # should only need to validate number of points and how they fall

    @pytest.mark.parametrize('_low, _high, _points',
        ((3, 12, 4), (10, 24, 8), (3, 24, 4)),
    )
    @pytest.mark.parametrize('_posn', ('left', 'middle', 'right'))
    @pytest.mark.parametrize('_is_hard', (True, False))
    @pytest.mark.parametrize('_hard_min', (1, 3))
    @pytest.mark.parametrize('_hard_max', (24, 30))
    def test_accuracy(
        self, _low, _high, _points, _posn, _is_hard, _hard_min, _hard_max
    ):

        _SINGLE_GRID = np.linspace(_low, _high, _points).tolist()

        # MAKE AN IRREGULAR INTERVAL
        _SINGLE_GRID[-2] = _SINGLE_GRID[-2] - 1

        _POSN = {'left':0, 'middle':1, 'right':len(_SINGLE_GRID)-1}
        _posn_ = _POSN[_posn]

        _grid_out = _int_linspace_gap_gt_1(
            _SINGLE_GRID,
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
                _gap = _SINGLE_GRID[1] - _SINGLE_GRID[0]
                assert min(_grid_out) == max(1, _hard_min, _SINGLE_GRID[0] - _gap)
                assert max(_grid_out) == _SINGLE_GRID[1] - 1
                del _gap

            elif _posn == 'right':
                _gap = _SINGLE_GRID[-1] - _SINGLE_GRID[-2]
                assert min(_grid_out) == _SINGLE_GRID[-2] + 1
                assert max(_grid_out) == min(_hard_max, _SINGLE_GRID[-1] + _gap)
                del _gap

            elif _posn == 'middle':
                assert min(_grid_out) >= _SINGLE_GRID[_posn_ - 1] + 1
                assert max(_grid_out) <= _SINGLE_GRID[_posn_ + 1] - 1


        elif not _is_hard:

            if _posn == 'left':
                _gap = _SINGLE_GRID[1] - _SINGLE_GRID[0]
                assert min(_grid_out) == max(1, _SINGLE_GRID[0] - _gap)
                assert max(_grid_out) == _SINGLE_GRID[1] - 1
                del _gap

            elif _posn == 'right':
                _gap = _SINGLE_GRID[-1] - _SINGLE_GRID[-2]
                assert min(_grid_out) == _SINGLE_GRID[-2] + 1
                assert max(_grid_out) == _SINGLE_GRID[-1] + _gap
                del _gap

            elif _posn == 'middle':
                assert min(_grid_out) >= _SINGLE_GRID[_posn_ - 1] + 1
                assert max(_grid_out) <= _SINGLE_GRID[_posn_ + 1] - 1







