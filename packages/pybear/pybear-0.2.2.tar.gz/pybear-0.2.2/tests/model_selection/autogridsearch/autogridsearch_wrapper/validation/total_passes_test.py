# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.autogridsearch._autogridsearch_wrapper._validation. \
    _total_passes import _val_total_passes

import numpy as np

import pytest



class TestValTotalPasses:


    #   points could be passed as single int or a list-like[int].
    #   when a param in params has points that are int, total_passes
    #   must be used to convert to list.


    @pytest.mark.parametrize('non_numeric',
        (True, False, None, 'trash', [1, 2], (1, 2), {1, 2}, lambda x: x, {'a': 1})
    )
    def test_rejects_non_numeric(self, non_numeric):
        with pytest.raises(TypeError):
            _val_total_passes(non_numeric)


    @pytest.mark.parametrize('non_numeric',
        (-np.pi, -np.e, np.e, np.pi, float('inf'))
    )
    def test_rejects_non_integer(self, non_numeric):
        with pytest.raises(TypeError):
            _val_total_passes(non_numeric)


    @pytest.mark.parametrize('less_than_one', (0, -1))
    def test_rejects_less_than_one(self, less_than_one):
        with pytest.raises(ValueError):
            _val_total_passes(less_than_one)


    def test_accepts_good_positive_integer(self):
        assert _val_total_passes(3) is None

    # END total_passes ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *








