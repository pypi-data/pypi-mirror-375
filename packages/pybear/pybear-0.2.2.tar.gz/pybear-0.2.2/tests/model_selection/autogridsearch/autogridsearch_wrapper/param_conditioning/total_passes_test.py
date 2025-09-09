# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _param_conditioning._total_passes import _cond_total_passes

import pytest

import numpy as np



class TestCondTotalPasses:


    @pytest.mark.parametrize('_int',
        (-1, 1, np.float64(2), np.uint8(3), np.int8(4), np.int32(5))
    )
    def test_accuracy(self, _int):

        assert _cond_total_passes(_int) == int(_int)




