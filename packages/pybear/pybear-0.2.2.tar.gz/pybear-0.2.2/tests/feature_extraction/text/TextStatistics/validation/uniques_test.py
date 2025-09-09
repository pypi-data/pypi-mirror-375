# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.feature_extraction.text._TextStatistics._validation._uniques \
    import _val_uniques



class TestValUniques:


    @pytest.mark.parametrize('junk_uniques',
        (-2.7, -1, 0, 1, 2.7, True, None, 'garbage', [0,1], (1,), {'a':1},
         lambda x: x)
    )
    def test_reject_not_sequence_of_str(self, junk_uniques):

        with pytest.raises(TypeError):
            _val_uniques(junk_uniques)


    def test_rejects_duplicates(self):

        with pytest.raises(TypeError):
            _val_uniques(['a', 'a', 'if', 'and', 'but'])


    def test_accepts_sequence_of_str(self):

        _base_seq = ['A', 'IT', 'THE', 'WHEN', 'WHERE', 'ANYWAY', 'SOMETIMES']

        _val_uniques(list(_base_seq))

        _val_uniques(set(_base_seq))

        _val_uniques(tuple(_base_seq))

        _val_uniques(np.array(_base_seq))

        _val_uniques(pd.Series(_base_seq))











