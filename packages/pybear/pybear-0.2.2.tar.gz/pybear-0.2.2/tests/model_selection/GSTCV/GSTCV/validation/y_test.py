# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.model_selection.GSTCV._GSTCV._validation._y import _val_y



class TestValY:


    @pytest.mark.parametrize('y', (0, True, min, 'junk', lambda x: x))
    def test_rejects_junk_y(self, y):

        with pytest.raises((TypeError, ValueError)):
            _val_y(y)


    def test_rejects_misshapen_y(self, _rows):

        # multicolumn y
        with pytest.raises(ValueError):
            _val_y(np.random.randint(0,2,(_rows,2)))


    def test_rejects_non_binary_y(self, _rows):

        y_np_bad_array = np.random.choice(list('abcde'), (_rows, 1), replace=True)
        y_pd_bad_df = pd.DataFrame(data=y_np_bad_array, columns=['y'])
        y_pd_bad_series = pd.Series(y_pd_bad_df.iloc[:, 0], name='y')

        with pytest.raises(ValueError):
            _val_y(y_np_bad_array)

        with pytest.raises(ValueError):
            _val_y(y_pd_bad_df)

        with pytest.raises(ValueError):
            _val_y(y_pd_bad_series)


    def test_accepts_good(self, y_np, y_pd):

        assert _val_y(list(y_np)) is None

        assert _val_y(tuple(y_np)) is None

        assert _val_y(set(list(y_np))) is None

        assert _val_y(y_np) is None

        assert _val_y(y_pd) is None

        assert _val_y(y_pd.iloc[:, 0]) is None


