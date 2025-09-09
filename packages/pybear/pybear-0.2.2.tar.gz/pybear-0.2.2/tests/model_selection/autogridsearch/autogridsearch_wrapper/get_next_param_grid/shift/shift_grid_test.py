# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._shift._shift_grid import _shift_grid



class TestShiftGrid:


    @staticmethod
    @pytest.fixture
    def good_single_param():
        return [[10, 20, 30, 40], [4, 4, 4], 'soft_float']


    @staticmethod
    @pytest.fixture
    def good_single_old_grid():
        return [20, 30, 40, 50]


    @staticmethod
    @pytest.fixture
    def good_single_is_logspace_True():
        return 1.0


    @staticmethod
    @pytest.fixture
    def good_single_is_logspace_False():
        return False

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_rejects_bad_numeric_param_format(self):
        with pytest.raises(ValueError):
            _shift_grid(
                [[1,2,3,4], [4,4,4]],
                ['a,', 'b', 'c', 'd'],
                False,
                4
            )

        with pytest.raises(ValueError):
            _shift_grid(
                [[1, 2, 3, 4]],
                ['a,', 'b', 'c', 'd'],
                False,
                4
            )

        with pytest.raises(ValueError):
            _shift_grid(
                [[1, 2, 3, 4], [4,4,4], ''],
                ['a,', 'b', 'c', 'd'],
                False,
                4
            )


    def test_reject_non_numeric_last_grid(self):

        with pytest.raises(ValueError):
            _shift_grid(
                [[1,2,3,4], [4,4,4], 'soft_integer'],
                ['a,', 'b', 'c', 'd'],
                False,
                4
            )

    def test_reject_non_numeric_param(self):

        with pytest.raises(ValueError):
            _shift_grid(
                [['a' 'b', 'c', 'c'], 3, 'fixed_string'],
                ['a', 'b', 'c', 'd'],
                False,
                'b'
            )


    def test_rejects_num_not_on_an_edge(self):
        with pytest.raises(ValueError):
            _shift_grid(
                [[10, 20, 30], [3,3,3], 'soft_float'],
                [20, 30, 40],
                False,
                30
            )


    def test_rejects_any_non_soft_param(self):
        with pytest.raises(ValueError):
            _shift_grid(
                [[1,2,3,4], [4,4,4], 'fixed_integer'],
                [1,2,3,4],
                False,
                4
            )


    @pytest.mark.parametrize('_gap', (1,2))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_edge', ('left', 'right'))
    def test_accuracy_no_universal_bound_int(self, _gap, _space, _edge):

        _points = 4
        _grid_low = 5
        _grid_high = _grid_low + _gap * (_points-1)
        _fg_params = (_grid_low, _grid_high, _points)
        _lg_params = (_grid_low + 1, _grid_high + 1, _points)

        if _space == 'linspace':
            _first_grid = np.linspace(*_fg_params).tolist()
            _latest_grid = np.linspace(*_lg_params).tolist()
        elif _space == 'logspace':
            _first_grid = np.logspace(*_fg_params).tolist()
            _latest_grid = np.logspace(*_lg_params).tolist()

        if _edge == 'left':
            _best = _latest_grid[0]
            _new_grid_params = (
                _grid_low + 1 - (_points - 2) * _gap,
                _grid_low + 1 + _gap,
                _points
            )
        elif _edge == 'right':
            _best = _latest_grid[-1]
            _new_grid_params = (
                _grid_high + 1 - _gap,
                _grid_high + 1 + (_points - 2) * _gap,
                _points
            )

        out = _shift_grid(
            [_first_grid, [4, 4, 4], 'soft_integer'],
            _latest_grid,
            _gap if _space=='logspace' else False,
            _best
        )

        if _space == 'linspace':
            EXPECTED = np.linspace(*_new_grid_params).tolist()

        elif _space == 'logspace':
            EXPECTED = np.logspace(*_new_grid_params).tolist()

        EXPECTED = list(map(int, EXPECTED))

        assert out == EXPECTED

        assert len(np.unique(list(map(str, map(type, out))))) == 1

        assert isinstance(out[0], int)



    @pytest.mark.parametrize('_gap', (1,2))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_edge', ('left', 'right'))
    def test_accuracy_int_lower_bound_1(self, _gap, _space, _edge):

        _points = 4
        _grid_low = 2
        _grid_high = _grid_low + _gap * (_points-1)
        _fg_params = (_grid_low, _grid_high, _points)
        _lg_params = (_grid_low + 1, _grid_high + 1, _points)

        if _space == 'linspace':
            _first_grid = np.linspace(*_fg_params).tolist()
            _latest_grid = np.linspace(*_lg_params).tolist()
        elif _space == 'logspace':
            _first_grid = np.logspace(*_fg_params).tolist()
            _latest_grid = np.logspace(*_lg_params).tolist()

        if _edge == 'left':
            _best = _latest_grid[0]
            _new_grid_params = (
                _grid_low + 1 - (_points - 2) * _gap,
                _grid_low + 1 + _gap,
                _points
            )
        elif _edge == 'right':
            _best = _latest_grid[-1]
            _new_grid_params = (
                _grid_high + 1 - _gap,
                _grid_high + 1 + (_points - 2) * _gap,
                _points
            )

        out = _shift_grid(
            [_first_grid, [4, 4, 4], 'soft_integer'],
            _latest_grid,
            _gap if _space=='logspace' else False,
            _best
        )

        if _space == 'linspace':

            if _new_grid_params[0] < 1:
                _diff = abs(_new_grid_params[0] - 1)
                _new_grid_params = list(_new_grid_params)
                _new_grid_params[0] += _diff
                _new_grid_params[1] += _diff
                del _diff

            EXPECTED = np.linspace(*_new_grid_params).tolist()

        elif _space == 'logspace':

            if _new_grid_params[0] < 0:
                _diff = abs(_new_grid_params[0])
                _new_grid_params = list(_new_grid_params)
                _new_grid_params[0] += _diff
                _new_grid_params[1] += _diff
                del _diff

            EXPECTED = np.logspace(*_new_grid_params).tolist()

        EXPECTED = list(map(int, EXPECTED))

        assert out == EXPECTED

        assert len(np.unique(list(map(str, map(type, out))))) == 1

        assert isinstance(out[0], int)



    @pytest.mark.parametrize('_gap', (1,2))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_edge', ('left', 'right'))
    def test_accuracy_no_universal_bound_float(self, _gap, _space, _edge):

        _points = 4
        _grid_low = 5
        _grid_high = _grid_low + _gap * (_points-1)
        _fg_params = (_grid_low, _grid_high, _points)
        _lg_params = (_grid_low + 1, _grid_high + 1, _points)

        if _space == 'linspace':
            _first_grid = np.linspace(*_fg_params).tolist()
            _latest_grid = np.linspace(*_lg_params).tolist()
        elif _space == 'logspace':
            _first_grid = np.logspace(*_fg_params).tolist()
            _latest_grid = np.logspace(*_lg_params).tolist()

        if _edge == 'left':
            _best = _latest_grid[0]
            _new_grid_params = (
                _grid_low + 1 - (_points - 2) * _gap,
                _grid_low + 1 + _gap,
                _points
            )
        elif _edge == 'right':
            _best = _latest_grid[-1]
            _new_grid_params = (
                _grid_high + 1 - _gap,
                _grid_high + 1 + (_points - 2) * _gap,
                _points
            )

        out = _shift_grid(
            [_first_grid, [4, 4, 4], 'soft_float'],
            _latest_grid,
            _gap if _space=='logspace' else False,
            _best
        )

        if _space == 'linspace':
            EXPECTED = np.linspace(*_new_grid_params).tolist()

        elif _space == 'logspace':
            EXPECTED = np.logspace(*_new_grid_params).tolist()

        EXPECTED = list(map(float, EXPECTED))

        assert out == EXPECTED

        assert len(np.unique(list(map(str, map(type, out))))) == 1

        assert isinstance(out[0], float)




    @pytest.mark.parametrize('_gap', (1,2))
    @pytest.mark.parametrize('_space', ('linspace', 'logspace'))
    @pytest.mark.parametrize('_edge', ('left', 'right'))
    def test_accuracy_float_left_bound_0(self, _gap, _space, _edge):

        _points = 4
        _grid_low = 2
        _grid_high = _grid_low + _gap * (_points-1)
        _fg_params = (_grid_low, _grid_high, _points)
        _lg_params = (_grid_low + 1, _grid_high + 1, _points)

        if _space == 'linspace':
            _first_grid = np.linspace(*_fg_params).tolist()
            _latest_grid = np.linspace(*_lg_params).tolist()
        elif _space == 'logspace':
            _first_grid = np.logspace(*_fg_params).tolist()
            _latest_grid = np.logspace(*_lg_params).tolist()

        if _edge == 'left':
            _best = _latest_grid[0]
            _new_grid_params = (
                _grid_low + 1 - (_points - 2) * _gap,
                _grid_low + 1 + _gap,
                _points
            )
        elif _edge == 'right':
            _best = _latest_grid[-1]
            _new_grid_params = (
                _grid_high + 1 - _gap,
                _grid_high + 1 + (_points - 2) * _gap,
                _points
            )

        out = _shift_grid(
            [_first_grid, [4, 4, 4], 'soft_float'],
            _latest_grid,
            _gap if _space=='logspace' else False,
            _best
        )

        if _space == 'linspace':
            if _new_grid_params[0] < 0:
                _new_grid_params = list(_new_grid_params)
                _diff = abs(_new_grid_params[0])
                _new_grid_params[0] += _diff
                _new_grid_params[1] += _diff
                del _diff

            EXPECTED = np.linspace(*_new_grid_params).tolist()

        elif _space == 'logspace':
            EXPECTED = np.logspace(*_new_grid_params).tolist()

        EXPECTED = list(map(float, EXPECTED))

        assert out == EXPECTED

        assert len(np.unique(list(map(str, map(type, out))))) == 1

        assert isinstance(out[0], float)






