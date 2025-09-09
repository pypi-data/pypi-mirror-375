# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._validation._validate_grids import _validate_grids



class TestValidateGrids:


    @pytest.mark.parametrize('non_dict_GRIDS',
        (0, np.pi, True, None, min, (1,), [1, ], {1, 2}, lambda x: x, 'junk')
    )
    def test_rejects_non_dict_grids(self, non_dict_GRIDS):

        with pytest.raises(TypeError):
            _validate_grids(non_dict_GRIDS)


    @pytest.mark.parametrize('key_1',
        (np.pi, True, False, None, min, (1,), lambda x: x, 'junk')
    )
    @pytest.mark.parametrize('key_2',
        (np.pi, True, False, None, min, (1,), lambda x: x, 'junk')
    )
    def test_rejects_bad_grids_keys(self, key_1, key_2):

        if key_1 == key_2:
            pytest.skip(reason=f"redundant combination")

        bad_GRIDS = {
            key_1: {'a': [1, 2, 3], 'b': ['a', 'b', 'c']},
            key_2: {'a': [1, 2, 3], 'b': ['a', 'b', 'c']}
        }

        with pytest.raises(TypeError):
            _validate_grids(bad_GRIDS)


    @pytest.mark.parametrize('bad_dict_1',
        (0, np.pi, True, None, min, (1,), {1, 2}, {'a': [1]}, lambda x: x, 'junk')
    )
    @pytest.mark.parametrize('bad_dict_2',
        (0, np.pi, True, None, min, (1,), {1, 2}, {'a': [1]}, lambda x: x, 'junk')
    )
    def test_rejects_bad_grids_values(self, bad_dict_1, bad_dict_2):

        if isinstance(bad_dict_1, dict) and isinstance(bad_dict_2, dict):
            pytest.skip(reason=f"this is expected to pass")

        bad_GRIDS = {0: bad_dict_1, 1: bad_dict_2}

        with pytest.raises(TypeError):
            _validate_grids(bad_GRIDS)


    @pytest.mark.parametrize('key_1',
        (0, np.pi, True, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    @pytest.mark.parametrize('key_2',
        (0, np.pi, True, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    def test_rejects_inner_dict_key_not_str(self, key_1, key_2):

        if key_1 == key_2:
            pytest.skip(reason=f"redundant combination")

        if isinstance(key_1, str) and isinstance(key_2, str):
            pytest.skip(reason=f"this is expected to pass")

        bad_GRIDS = {0: {key_1: [1,2,3]}, key_2: ['a', 'b', 'c']}

        with pytest.raises(TypeError):
            _validate_grids(bad_GRIDS)


    _values = (0, np.pi, True, None, min, (1,), [1, ], {1, 2}, {'a': 1},
               lambda x: x, 'junk')
    @pytest.mark.parametrize('grid_1', _values)
    @pytest.mark.parametrize('grid_2', _values)
    def test_rejects_grid_not_list(self, grid_1, grid_2):

        if isinstance(grid_1, list) and isinstance(grid_2, list):
            pytest.skip(reason=f"this is expected to pass")

        bad_GRIDS = {0: {'a': grid_1}, 1: {'b': grid_2}}

        with pytest.raises(TypeError):
            _validate_grids(bad_GRIDS)


    def test_accepts_good_grids(self):

        _validate_grids(
            {
                0: {
                    'a': ['a','b','c'],
                    'b': [1,2,3],
                    'c': [1.1, 2.2, 3.3],
                    'd': [True, False]
                },
                1: {
                    'a': ['a','b','c'],
                    'b': [1,2,3],
                    'c': [1.1, 2.2, 3.3],
                    'd': [True, False]
                },
                2: {
                    'a': ['a','b','c'],
                    'b': [1,2,3],
                    'c': [1.1, 2.2, 3.3],
                    'd': [True, False]
                },
                3: {
                    'a': ['a','b','c'],
                    'b': [1,2,3],
                    'c': [1.1, 2.2, 3.3],
                    'd': [True, False]
                },
                4: {}
            }
        )



    def test_accepts_good_grids_len_1(self):

        _validate_grids(
            {
                0: {
                    'a': ['b'],
                    'b': [3],
                    'c': [1.1],
                    'd': [True]
                },
                1: {
                    'a': ['b'],
                    'b': [3],
                    'c': [1.1],
                    'd': [True]
                },
                2: {
                    'a': ['b'],
                    'b': [3],
                    'c': [1.1],
                    'd': [True]
                },
                3: {
                    'a': ['b'],
                    'b': [3],
                    'c': [1.1],
                    'd': [True]
                },
                4: {}
            }
        )


