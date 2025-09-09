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

from pybear.preprocessing._InterceptManager._inverse_transform._remove_intercept \
    import _remove_intercept

from pybear.utilities._nan_masking import nan_mask



class TestRemoveIntercept:


    # no validation


    # must be IM internal container
    @pytest.mark.parametrize('_format',('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('_dtype', ('int', 'flt', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_keep',
        ('first', 'last', 'random', 'none', 0, 'str', lambda x: 0)
    )
    def test_flows_thru_if_keep_not_dict(
        self, _X_factory, _shape, _columns, _format, _dtype, _keep
    ):

        # all of these should flow thru and be equal to what was passed

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _format not in ('np', 'pd', 'pl') and _dtype not in ('int', 'flt'):
            pytest.skip(reason=f'scipy sparse cannot take str')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _keep == 'str':
            if _format not in ('pd', 'pl'):
                pytest.skip(reason=f'cant have str keep without header')
            _keep = _columns[0]

        _constants = {1: 1, _shape[1]-2: np.nan}

        _X_trfm = _X_factory(
            _format=_format,
            _dtype=_dtype,
            _constants=_constants,
            _columns=_columns if _format in ('pd', 'pl') else None,
            _shape=_shape
        )

        try:
            _og_X_trfm = _X_trfm.copy()
        except:
            _og_X_trfm = _X_trfm.clone()

        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v
        out = _remove_intercept(_X_trfm, _keep)
        # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        assert type(out) == type(_og_X_trfm)

        # convert out and the og to np for array_equal
        if isinstance(_og_X_trfm, np.ndarray):
            pass
        elif hasattr(_og_X_trfm, 'columns'):
            _og_X_trfm = _og_X_trfm.to_numpy()
            out = out.to_numpy()
        elif hasattr(_og_X_trfm, 'toarray'):
            _og_X_trfm = _og_X_trfm.toarray()
            out = out.toarray()
        else:
            raise Exception


        if _dtype in ('int', 'flt'):
            _og_X_trfm[nan_mask(_og_X_trfm)] = np.nan
            out[nan_mask(out)] = np.nan
        else:
            _og_X_trfm[nan_mask(_og_X_trfm)] = 'nan'
            out[nan_mask(out)] = 'nan'


        if _dtype in ('int', 'flt'):
            assert np.array_equal(out, _og_X_trfm, equal_nan=True)
        else:
            assert np.array_equal(out, _og_X_trfm)


    # v v v v v v v v v v keep must be dict v v v v v v v v v v v v v v


    # must be IM internal container
    @pytest.mark.parametrize('_format',('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('_dtype', ('int', 'flt', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_value', (-1, 2, 1_000_000_000))
    def test_rejects_unexpected_constant(
        self, _X_factory, _shape, _columns, _format, _dtype, _value
    ):

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _format not in ('np', 'pd', 'pl') and _dtype not in ('int', 'flt'):
            pytest.skip(reason=f'scipy sparse cannot take str')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # make a rigged trfm_x that has the bad constants in the last column
        _trfm_X = _X_factory(
            _format=_format,
            _dtype=_dtype,
            _columns=_columns if _dtype in ('pd', 'pl') else None,
            _constants={_shape[1]-1: _value},   # <============
            _shape=_shape
        )

        # keep has a constant different than '_value'
        with pytest.raises(ValueError):
            _remove_intercept(_trfm_X, _keep={'Intercept': 1})


    # must be IM internal container
    @pytest.mark.parametrize('_format, _nan_type',
        (('np', np.nan), ('pd', pd.NA), ('pl', None), ('csc_array', np.nan))
    )
    @pytest.mark.parametrize('_dtype', ('int', 'flt', 'str', 'obj', 'hybrid'))
    def test_finds_appended_column_of_nans(
        self, _X_factory, _shape, _columns, _format, _nan_type, _dtype
    ):

        # if the column of nans is removed, then _remove_intercept found it

        assert _format in ('np', 'pd', 'pl', 'csc_array')
        assert _dtype in ('int', 'flt', 'str', 'obj', 'hybrid')

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _dtype == 'int' and _format in ('np', 'csc_array'):
            pytest.skip(reason=f'cant have nans in int')

        if _format not in ('np', 'pd', 'pl') and _dtype not in ('int', 'flt'):
            pytest.skip(reason=f'scipy sparse cannot take str')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # make a rigged trfm_x that has the nans in the last column
        _X_trfm = _X_factory(
            _format=_format,
            _dtype=_dtype,
            _constants=None,
            _columns=_columns if _format in ('pd', 'pl') else None,
            _shape=_shape  # add the column below
        )
        # _X_factory machinery doesnt want to make columns of nans
        # so do it the hard way
        if _format == 'np':
            _X_trfm = np.insert(_X_trfm, _shape[1], _nan_type, axis=1)
        elif _format == 'pd':
            _X_trfm['Intercept'] = _nan_type
        elif _format == 'pl':
            _X_trfm = _X_trfm.with_columns(
                pl.DataFrame({'Intercept': [_nan_type for i in range(_shape[0])]})
            )
        elif _format == 'csc_array':
            _X_trfm = ss.hstack(
                (_X_trfm, np.full((_shape[0], ), _nan_type).reshape((-1, 1))),
                format="csc",
                dtype=_X_trfm.dtype
            )
        else:
            raise Exception

        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v
        out = _remove_intercept(_X_trfm, _keep={'Intercept': _nan_type})
        # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        assert out.shape[1] == (_X_trfm.shape[1] - 1)


    # must be IM internal container
    @pytest.mark.parametrize('_format',('np', 'pd', 'pl', 'csc_matrix'))
    @pytest.mark.parametrize('_dtype, _value',
        (('int', 1), ('flt', np.e), ('str', 'a'), ('obj', 'b'), ('hybrid', 'c'))
    )
    def test_accuracy(self, _X_factory, _shape, _columns, _format, _dtype, _value):

        # _remove_intercept....
        # 1) looks at keep checks if it is a dict. if not dict, X just
        #    flows thru. if it is a dict then expects the last column in
        #    X to be a constant whose value matches the value in the
        #    dict, if not match then raise.
        # 2) if keep is dict and it matches, remove last column.

        # an appended intercept cannot be sprinkled with nans (but it
        # could be all nans if the user wanted that for some reason)
        # output container is same as given
        # the operation is the same regardless of dtype

        assert _dtype in ('int', 'flt', 'str', 'obj', 'hybrid')

        # skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _format not in ('np', 'pd', 'pl') and _dtype not in ('int', 'flt'):
            pytest.skip(reason=f'scipy sparse cannot take str')
        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --


        _keep = {'Intercept': _value}

        # NEED TO FUDGE THE COLUMN NAMES TO PUT THE APPENDED COLUMN NAME
        # IN THE LAST SLOT
        _columns[-1] = list(_keep)[0]

        # BUILD X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _trfm_X = _X_factory(
            _format=_format,
            _dtype=_dtype,
            _constants={_shape[1]-1: _value},
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _shape=_shape
        )
        # END BUILD X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        out = _remove_intercept(_trfm_X, _keep)

        assert out.shape[1] == (_trfm_X.shape[1] - 1)




