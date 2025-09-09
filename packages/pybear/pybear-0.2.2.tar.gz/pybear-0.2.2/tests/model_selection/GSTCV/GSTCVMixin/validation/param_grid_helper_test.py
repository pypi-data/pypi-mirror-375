# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._validation._param_grid_helper \
    import _val_param_grid_helper



class TestValParamGridHelper:


    # def _val_param_grid_helper(
    #     _param_grid: ParamGridInputType,
    #     _grid_idx: int
    # ) -> None:


    @staticmethod
    @pytest.fixture(scope='function')
    def good_param_grid():
        return {
            'thresholds': np.linspace(0,1,11), 'solver': ['saga', 'lbfgs'],
            'C': np.logspace(-5,5,11)
        }

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_param_grid',
        (0, 1, 3.14, True, False, 'trash', min, lambda x: x)
    )
    def test_rejects_junk_param_grid(self, junk_param_grid):
        with pytest.raises(TypeError):
            _val_param_grid_helper(junk_param_grid, 0)


    @pytest.mark.parametrize('junk_param_grid',
        ({0:1, 1:2}, {'a': 1, 'b': 2}, {0: False, 1: True}, {0:[1,2,3]})
    )
    def test_rejects_junk_dicts(self, junk_param_grid):
        with pytest.raises(TypeError):
            _val_param_grid_helper(junk_param_grid, 1)


    @pytest.mark.parametrize('junk_thresh',
        (-1, 3.14, True, False, 'trash', min, [-1,2], (-2,1), lambda x: x)
    )
    def test_rejects_junk_thresh(self, good_param_grid, junk_thresh):

        good_param_grid['thresholds'] = junk_thresh

        with pytest.raises((TypeError, ValueError)):
            _val_param_grid_helper(good_param_grid, 6)


    def test_accepts_good_param_grids(self, good_param_grid):

        # and good thresholds

        assert _val_param_grid_helper(good_param_grid, 2) is None


    def test_accepts_valid_empties(self):

        assert _val_param_grid_helper({}, 3) is None


    @pytest.mark.parametrize('bad_empties', (((),), ([{}],), [[]], [(), ()]))
    def test_rejects_invalid_empties(self, bad_empties):

        with pytest.raises(TypeError):
            _val_param_grid_helper(bad_empties, 4)





