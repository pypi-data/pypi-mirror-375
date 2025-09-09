# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest



import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing._InterceptManager._inverse_transform. \
    _inverse_transform import _inverse_transform

from pybear.preprocessing._InterceptManager.InterceptManager import \
    InterceptManager

from pybear.utilities._nan_masking import nan_mask





class TestInverseTransform:

    # verify that inverse_transform takes transformed back to original.
    # build an X with duplicates, use IM to manage the constant columns
    # under different parameters (IM transform() is independently tested)
    # use inverse_transform to reconstruct back to the original X.


    @pytest.mark.parametrize('_format',
        (
            'csr_matrix', 'coo_matrix', 'dia_matrix', 'lil_matrix', 'dok_matrix',
            'bsr_matrix', 'csr_array', 'coo_array', 'dia_array', 'lil_array',
            'dok_array', 'bsr_array'
        )
    )
    def test_rejects_all_ss_that_are_not_csc(
        self, _X_factory, _shape, _kwargs, _format
    ):

        # everything except ndarray, pd dataframe, & scipy csc matrix/array
        # are blocked. should raise.

        # build X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format=_format,
            _dtype='flt',
            _constants={0:1, _shape[1]-1: 1},
            _shape=_shape
        )
        # END build X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # _IM is only being used here to get the legit TRFM_X. only test
        # the core _inverse_transform module, not _IM.inverse_transform.
        _IM = InterceptManager(**_kwargs)

        TRFM_X = _IM.fit_transform(_X_wip)

        with pytest.raises(AssertionError):
            _inverse_transform(
                _X=TRFM_X,
                _removed_columns=_IM.removed_columns_,
                _feature_names_in=None
            )


    @pytest.mark.parametrize('_dtype', ('flt', 'str'))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random', 'none'))
    @pytest.mark.parametrize('_constants', ('constants1', 'constants2'))
    @pytest.mark.parametrize('_format, _has_header',
        (('np', False), ('pd', True), ('pd', False), ('pl', True), ('pl', False),
         ('csc_matrix', False), ('csc_array', False))
    )
    def test_accuracy(
        self, _X_factory, _dtype, _keep, _constants,
        _format, _has_header, _columns, _shape
    ):

        # Methodology: transform data, then transform back using
        # inverse_transform. the inverse transform must be equal to the
        # originally fitted data, except for nans. inverse transform
        # cannot infer the presence of nans in the original data.

        # everything except ndarray, pd/pl dataframe, & scipy csc matrix/array
        # are blocked.

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if _dtype == 'str' and _format not in ('np', 'pd', 'pl'):
            pytest.skip(reason=f"scipy sparse cannot take strings")
        # END skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- --

        # build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        if _constants == 'constants1':
            if _dtype in ('int', 'flt'):
                _constants = {0:1, _shape[1]-1: 1}
            else:
                _constants = {0: 'a', _shape[1]-1:'b'}
        elif _constants == 'constants2':
            if _dtype in ('int', 'flt'):
                _constants = {0:1, _shape[1]-1: np.nan}
            else:
                _constants = {0: '1', _shape[1]-1:'nan'}
        else:
            raise Exception

        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=True,
            _format=_format,
            _dtype=_dtype,
            _columns=_columns if _has_header else None,
            _constants=_constants,
            _shape=_shape
        )
        # END build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # _IM is only being used here to get the legit TRFM_X. only test
        # the core _inverse_transform module, not _IM.inverse_transform.
        _IM = InterceptManager(
            keep=_keep,
            rtol=1e-5,
            atol=1e-8,
            equal_nan=True
        )

        TRFM_X = _IM.fit_transform(_X_wip)


        _num_removed = len(_constants) - 1 + (_keep == 'none')
        assert TRFM_X.shape[1] == _X_wip.shape[1] - _num_removed
        assert len(_IM.removed_columns_) == _num_removed
        del _num_removed

        # inverse transform v v v v v v v v v v v v v v v

        # _IM is only being used here to get the legit TRFM_X. only test
        # the core _inverse_transform module, not _IM.inverse_transform.
        out = _inverse_transform(
            _X=TRFM_X,
            _removed_columns=_IM.removed_columns_,
            _feature_names_in= \
                _columns if _format in ['pd', 'pl'] and _has_header else None
        )
        # inverse transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        assert type(out) is type(_X_wip)

        assert out.shape == _X_wip.shape


        if _has_header:
            assert np.array_equal(out.columns, _columns)
        elif not _has_header:
            exp_hdr = pd.RangeIndex(start=0, stop=_shape[1], step=1)
            if _format == 'pd':
                assert np.array_equal(out.columns, exp_hdr)
            elif _format == 'pl':
                exp_hdr = [f'column_{i}' for i in range(_shape[1])]
                assert np.array_equal(out.columns, exp_hdr)
            del exp_hdr

        # iterate over the input X and output X simultaneously, check
        # equality column by column. remember that inverse_transform
        # cannot replicate any nan-likes that may have been in the
        # removed columns in the original data.

        for _og_idx in range(_shape[1]):

            # OK to extract in 1D, using np.array_equal
            if isinstance(_X_wip, np.ndarray):
                _og_col = _X_wip[:, _og_idx]
                _out_col = out[:, _og_idx]
            elif isinstance(_X_wip, pd.DataFrame):
                _og_col = _X_wip.iloc[:, _og_idx].to_numpy()
                _out_col = out.iloc[:, _og_idx].to_numpy()
            elif isinstance(_X_wip, pl.DataFrame):
                # Polars uses zero-copy conversion when possible, meaning the
                # underlying memory is still controlled by Polars and marked
                # as read-only. NumPy and Pandas may inherit this read-only
                # flag, preventing modifications.
                # THE ORDER IS IMPORTANT HERE. CONVERT TO PANDAS FIRST THEN SLICE.
                _og_col = _X_wip.to_pandas().to_numpy()[:, _og_idx]
                _out_col = out.to_pandas().to_numpy()[:, _og_idx]
            elif hasattr(_X_wip, 'toarray'):
                _og_col = _X_wip[:, [_og_idx]].toarray()
                _out_col = out[:, [_og_idx]].toarray()
            else:
                raise Exception

            # allclose is not calling equal on two identical vectors,
            # one w nans and the other without, even with equal_nan.
            # also verified this behavior externally.
            # _og_col may or may not have the nans, but _out_col cannot.
            # put nans into _out_col to get around this.
            MASK = nan_mask(_og_col)
            _is_num = False
            try:
                _og_col[np.logical_not(MASK)].astype(np.float64)
                _is_num = True
            except Exception as e:
                pass
                # is str

            if _is_num:
                _og_col[MASK] = np.nan
                _out_col[MASK] = np.nan
                assert np.allclose(
                    _out_col.astype(np.float64),
                    _og_col.astype(np.float64),
                    equal_nan=True
                )
            elif not _is_num:
                _og_col[MASK] = 'nan'
                _out_col[MASK] = 'nan'
                assert np.array_equal(_out_col, _og_col)



