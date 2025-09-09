# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text.__shared._validation._1D_X import \
    _val_1D_X

import pytest



class TestVal_1D_X:


    def test_takes_empty(self):


        assert _val_1D_X([], _require_all_finite=True) is None








