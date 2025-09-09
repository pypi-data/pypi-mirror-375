# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.preprocessing._MinCountTransformer._validation._y \
    import _val_y



class TestValY:


    # def _val_y(
    #     y: YContainer
    # ) -> None:


    @pytest.mark.parametrize('junk_y',
        (0, 1, True, 'junk', [1, 2], (1, 2), {1, 2}, {'a': 1}, lambda y: y)
    )
    def test_rejects_junk(self, junk_y):

        with pytest.raises(TypeError):
            _val_y(junk_y)


    def test_rejects_bad_container(self, X_np, y_np, _columns, _shape):

        with pytest.raises(TypeError):
            _val_y(ss.csr_matrix(y_np.reshape((-1,1))))

        with pytest.raises(TypeError):
            _val_y(ss.coo_array(y_np.reshape((-1,1))))


        # numpy_recarray ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        Y_NEW = np.recarray(
            (_shape[0], ),
            names=list(_columns),
            formats=[[(_columns[0], np.uint8)]],
            buf=y_np
        )

        with pytest.raises(TypeError):
            _val_y(Y_NEW)
        del Y_NEW
        # END numpy_recarray ** ** ** ** ** ** ** ** ** ** ** ** ** **


    def test_masked_array_warns(self, y_np):

        with pytest.warns():
            _val_y(np.ma.array(y_np))


    def test_accepts_good_y(self, y_np, _columns):

        assert _val_y(None) is None

        assert _val_y(y_np) is None

        assert _val_y(y_np.reshape((-1, 1))) is None

        assert _val_y(pd.DataFrame(y_np.reshape((-1, 1)), columns=['y'])) is None

        assert _val_y(pd.Series(y_np)) is None

        assert _val_y(pl.from_numpy(y_np.reshape((-1,1)), schema=['y'])) is None

        assert _val_y(pl.from_numpy(y_np.reshape((-1,1)))[:, 0]) is None




