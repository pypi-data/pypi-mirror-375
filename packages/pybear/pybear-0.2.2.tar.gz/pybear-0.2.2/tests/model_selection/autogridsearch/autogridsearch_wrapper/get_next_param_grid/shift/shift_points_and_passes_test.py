# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper.\
    _get_next_param_grid._shift._shift_points_and_passes import \
    _shift_points_and_passes



class TestShiftPoints:

    # no _validation


    @pytest.mark.parametrize('total_passes', (2, 3, 4))
    @pytest.mark.parametrize('number_of_params', (1, 3, 10))
    @pytest.mark.parametrize('total_passes_is_hard', (True, False))
    def test_accuracy(self, total_passes, number_of_params, total_passes_is_hard):

        # build params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        _params = {}

        _keys = list('abcdefghijklmn'[:number_of_params])

        for _key in _keys:

            _random_dtype = np.random.choice(
                ['fixed_string', 'fixed_integer', 'soft_float', 'fixed_bool'],
                size=1
            )[0]
            _random_grid_size = int(np.random.randint(1,10))

            if _random_dtype == 'fixed_string':
                _grid = list('abcdefghijklmn'[:_random_grid_size])
                _shrink_pass = int(np.random.randint(1,5))
                _points = []
                for _idx in range(total_passes):
                    if _idx >= (_shrink_pass - 1):
                        _points.append(1)
                    else:
                        _points.append(len(_grid))
                del _shrink_pass
                _params[_key] = [_grid, _points, _random_dtype]
            elif _random_dtype == 'fixed_bool':
                _grid = [True, False]
                _shrink_pass = int(np.random.randint(1,5))
                _points = []
                for _idx in range(total_passes):
                    if _idx >= (_shrink_pass - 1):
                        _points.append(1)
                    else:
                        _points.append(len(_grid))
                del _shrink_pass
                _params[_key] = [_grid, _points, _random_dtype]
            else:
                _grid = np.arange(1, _random_grid_size+1).tolist()
                _points = list(map(int, np.random.randint(2, 11, total_passes)))
                _params[_key] = [_grid, _points, _random_dtype]


        del _random_dtype, _random_grid_size, _grid

        # END build params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        _pass = int(np.random.randint(1, total_passes))   # cannot be pass 0


        # ** * ** *

        out_params = _shift_points_and_passes(
            _params,
            _pass,
            total_passes_is_hard
        )

        # ** * ** *


        # build expected_params ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        expected_params = _params

        for _param in expected_params:

            expected_params[_param][1].insert(
                _pass, expected_params[_param][1][_pass-1]
            )

            if total_passes_is_hard:
                expected_params[_param][1] = expected_params[_param][1][:-1]

        # END build expected_params ** * ** * ** * ** * ** * ** * ** * ** * **


        assert out_params == expected_params








