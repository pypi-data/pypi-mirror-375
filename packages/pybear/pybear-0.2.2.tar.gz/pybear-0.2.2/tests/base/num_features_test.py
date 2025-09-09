# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.base._num_features import num_features



class TestNumFeatures:

    # disallows objects that does not have 'shape' attr
    # requires all scipy sparse be 2D
    # requires all other data-bearing objects be 1D or 2D


    def test_rejects_things_w_o_shape_attr(self):

        X = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8]
        ]

        with pytest.raises(ValueError):
            num_features(X)


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csr'))
    @pytest.mark.parametrize('X_shape',
        ((12, ), (77, ), (20, 3), (50, 5), (24, 13), (2, 4, 5), (8, 8, 8, 8))
    )
    def test_num_features(self, X_format: str, X_shape: tuple[int, ...]):

        # skip disallowed conditions -- -- -- -- -- -- -- -- -- -- --
        if X_format in ['pd', 'pl'] and len(X_shape) > 2:
            pytest.skip(reason=f"pd/pl cannot be more than 2D")

        if X_format == 'csr' and len(X_shape) != 2:
            pytest.skip(reason=f"pybear blocks scipy shape != 2")
        # end skip disallowed conditions -- -- -- -- -- -- -- -- -- --

        _base_X = np.random.randint(0, 10, X_shape)

        if len(X_shape) == 1:
            _columns = ['y']
        else:
            _columns = [str(uuid.uuid4())[:8] for _ in range(X_shape[1])]

        if X_format == 'np':
            _X = _base_X.copy()
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X, columns=_columns)
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X, schema=list(_columns))
        elif X_format == 'csr':
            _X = ss.csr_array(_base_X)
        else:
            raise Exception


        if len(X_shape) == 1:
            assert num_features(_X) == 1
        elif len(X_shape) == 2:
            assert num_features(_X) == X_shape[1]
        else:
            with pytest.raises(ValueError):
                num_features(_X)





