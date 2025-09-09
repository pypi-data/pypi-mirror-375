# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._validation._validate_phlite import _validate_phlite



class TestPHLITE:

    @pytest.mark.parametrize('non_dict_PHLITE',
        (0, np.pi, True, None, min, (1,), [1, ], {1, 2}, lambda x: x, 'junk')
    )
    def test_rejects_non_dict_phlite(self, non_dict_PHLITE):

        with pytest.raises(TypeError):
            _validate_phlite(non_dict_PHLITE)


    @pytest.mark.parametrize('key_1',
        (1, np.pi, True, False, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    @pytest.mark.parametrize('key_2',
        (1, np.pi, True, False, None, min, (1,), lambda x: x, 'junk1', 'junk2')
    )
    def test_rejects_non_str_keys(self, key_1, key_2):

        if key_1 == key_2:
            pytest.skip(reason=f"redundant combination")

        if isinstance(key_1, str) and isinstance(key_2, str):
            pytest.skip(reason=f"expected to pass")

        bad_PHLITE = {key_1: True, key_2: False}

        with pytest.raises(TypeError):
            _validate_phlite(bad_PHLITE)


    @pytest.mark.parametrize('bad_dict_1',
        (0, np.pi, True, False, None, min, (1,), {1, 2}, {'a': True},
         lambda x: x, 'junk')
    )
    @pytest.mark.parametrize('bad_dict_2',
        (0, np.pi, True, False, None, min, (1,), {1, 2}, {'a': True},
         lambda x: x, 'junk')
    )
    def test_rejects_bad_grids_values(self, bad_dict_1, bad_dict_2):

        if isinstance(bad_dict_1, dict) and isinstance(bad_dict_2, dict):
            pytest.skip(reason=f"this is expected to pass")

        bad_PHLITE = {0: bad_dict_1, 1: bad_dict_2}

        with pytest.raises(TypeError):
            _validate_phlite(bad_PHLITE)


    def test_accepts_good_phlite(self):

        _validate_phlite({'a': True, 'b': False})





