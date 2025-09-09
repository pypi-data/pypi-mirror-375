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

from pybear.base._get_feature_names import get_feature_names



class TestGetFeatureNames:

    # as of 25_01_02 the landscape of headers in the python ecosystem:
    # -- numpy array, pandas series, dask array, scipy sparse never have
    #       a header and get_feature_names() should always return None.
    # -- pandas dataframe, dask series, dask dataframe
    #     -- when created with a valid header of strs get_features_names()
    #           will return that header
    #     -- when created without a header (constructed with the default
    #           header of numbers) get_features_names() will except
    #           for invalid header
    # -- polars dataframe
    #     -- when created with a valid header of strs get_features_names()
    #           will return that header
    #     -- when created without a header, constructed with a
    #           default header of STRINGS and get_features_names() will
    #           return that header


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_np(_X_factory, _shape):
        return _X_factory(
            _dupl=None,
            _has_nan=False,
            _format='np',
            _dtype='flt',
            _columns=None,
            _constants=None,
            _zeros=0,
            _shape=_shape
        )


    @pytest.mark.parametrize('_format',
        ('np', 'pd_series', 'pd', 'pl', 'pl_series', 'csr')
    )
    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    def test_accuracy(
        self, _shape, _columns, _X_np, _format, _columns_is_passed
    ):

        if _format == 'np':
            _X_wip = _X_np
        elif _format in ['pd', 'pd_series']:
            _X_wip =pd.DataFrame(
                data = _X_np,
                columns = _columns if _columns_is_passed else None
            )
            if _format == 'pd_series':
                _X_wip = _X_wip.iloc[:, 0].squeeze()
        elif _format == 'csr':
            _X_wip = ss._csr.csr_array(_X_np)
        elif _format in ['pl', 'pl_series']:
            _X_wip = pl.DataFrame(
                data=_X_np,
                schema=_columns.tolist() if _columns_is_passed else None,
                orient='row'
            )
            if _format == 'pl_series':
                _X_wip = _X_wip[:, 0]
                assert isinstance(_X_wip, pl.Series)
        else:
            raise Exception

        if _format == 'pd' and not _columns_is_passed:
            with pytest.warns():
                # this warns for non-str feature names
                # (the default header when 'columns=' is not passed)
                out = get_feature_names(_X_wip)
        else:
            out = get_feature_names(_X_wip)

        if not _columns_is_passed:
            if _format == 'pl':
                assert isinstance(out, np.ndarray)
                assert out.dtype == object
                assert np.array_equal(out, [f'column_{i}' for i in range(_shape[1])])
            else:
                assert out is None
        elif _columns_is_passed:
            if _format in ['pd', 'pl']:
                assert isinstance(out, np.ndarray)
                assert out.dtype == object
                assert np.array_equal(out, _columns)
            else:
                assert out is None





