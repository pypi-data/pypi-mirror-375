# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing._ColumnDeduplicator._transform._transform \
    import _transform

from pybear.preprocessing._ColumnDeduplicator._partial_fit. \
    _parallel_column_comparer import _parallel_column_comparer



class TestTransform:

    # these tests prove that _transform:
    # - blocks anything that is not numpy ndarray, pandas/polars dataframe,
    #       or ss csc matrix/array
    # - correctly removes columns based on _column_mask
    # - format and dtype(s) of the transformed are same as passed

    @pytest.mark.parametrize('_format',
        (
            'coo_matrix', 'coo_array', 'dia_matrix', 'dia_array',
            'lil_matrix', 'lil_array', 'dok_matrix', 'dok_array',
            'bsr_matrix', 'bsr_array', 'csr_array', 'csr_matrix'
        )
    )
    def test_rejects_bad_container(self, _X_factory, _shape, _format):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=None, _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        with pytest.raises(AssertionError):
            _transform(
                _X_wip,
                np.random.randint(0, 2, (_shape[1],)).astype(bool)
            )


    @pytest.mark.parametrize('_dtype', ('flt', 'str'), scope='module')
    @pytest.mark.parametrize('_has_nan', (True, False), scope='module')
    @pytest.mark.parametrize('_equal_nan', (True, False), scope='module')
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'), scope='module')
    @pytest.mark.parametrize('_dupl', ([[0, 3], [2, 6, 8]], ), scope='module')
    @pytest.mark.parametrize('_format',
        ('np', 'pd', 'pl', 'csc_array', 'csc_matrix')
    )
    def test_output(
        self, _X_factory, _dtype, _has_nan, _equal_nan, _keep, _dupl, _format,
        _shape, _columns
    ):

        # Methodology:
        # pass X and _column_mask to _transform.
        # the transformed X should have kept the columns as in the expected
        # column mask.
        # iterate over input X and output X simultaneously, using the
        # expected column mask to map columns in output X to their
        # original locations in input X.
        # Columns that are mapped to each other must be array_equal.
        # if they are, that means _transform correctly deleted the masked
        # columns for different containers


        if _dtype == 'str' and _format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take strings")


        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        _X_wip = _X_factory(
            _dupl=_dupl,
            _has_nan=_has_nan,
            _format=_format,
            _dtype=_dtype,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )

        # retain the original dtype(s)
        _og_format = type(_X_wip)
        if isinstance(_X_wip, (pd.DataFrame, pl.DataFrame)):
            # need to cast pl to ndarray
            _og_dtype = np.array(_X_wip.dtypes)
        else:
            _og_dtype = _X_wip.dtype

        # retain the original num columns
        _og_cols = _X_wip.shape[1]

        # END BUILD_X v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # build the column mask for the parameter inputs - - - - - - - -
        # this would otherwise be done by _identify_idxs_to_delete....
        # it is probably just as well to construct this independently.

        # when not equal_nan, all columns must be unequal (full mask, all
        # columns are kept) because every column in X gets some nans
        if _equal_nan:
            _del = []
            for _set in _dupl:
                __ = _set.copy()
                __.remove(np.random.choice(_set))
                _helper_dict = {'first': _set[1:], 'last': _set[:-1], 'random': __}
                del __

                _del += _helper_dict[_keep]

            _del.sort()
            assert len(np.array(_del).shape) == 1

            _column_mask = np.ones((_shape[1], )).astype(bool)
            _column_mask[_del] = False
        elif not _equal_nan:
            _column_mask = np.ones((_shape[1], )).astype(bool)
        # END build the column mask for the parameter inputs - - - - - -


        # apply the column mask to the original X
        out = _transform(_X_wip, _column_mask)


        # ASSERTIONS ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        # output format is same as given
        assert isinstance(out, _og_format)

        # output dtypes are same as given
        if isinstance(out, (pd.DataFrame, pl.DataFrame)):
            assert np.array_equal(out.dtypes, _og_dtype[_column_mask])
        else:
            assert out.dtype == _og_dtype

        # out matches _column_mask
        assert out.shape[1] == sum(_column_mask)

        _kept_idxs = list(map(int, np.arange(_shape[1])[_column_mask]))

        for _out_idx, _og_idx in enumerate(_kept_idxs):

            # nans in string columns are being a real pain
            # _parallel_column_comparer instead of np.array_equal
            if isinstance(_X_wip, np.ndarray):
                _out_col = out[:, _out_idx]
                _og_col = _X_wip[:, _og_idx]
            elif isinstance(_X_wip, pd.DataFrame):
                _out_col = out.iloc[:, _out_idx].to_numpy()
                _og_col = _X_wip.iloc[:, _og_idx].to_numpy()
                # verify header matches
                assert _X_wip.columns[_og_idx] == out.columns[_out_idx]
            elif isinstance(_X_wip, pl.DataFrame):
                _out_col = out[:, _out_idx].to_numpy()
                _og_col = _X_wip[:, _og_idx].to_numpy()
                # verify header matches
                assert _X_wip.columns[_og_idx] == out.columns[_out_idx]
            elif hasattr(_X_wip, 'toarray'):
                _out_col = out[:, [_out_idx]].toarray().ravel()
                _og_col = _X_wip[:, [_og_idx]].toarray().ravel()
            else:
                raise Exception

            if not _has_nan or (_has_nan and _equal_nan):
                assert _parallel_column_comparer(
                    _out_col, _og_col, 1e-5, 1e-8, _equal_nan
                )
            else:
                assert not _parallel_column_comparer(
                    _out_col, _og_col, 1e-5, 1e-8, _equal_nan
                )

        # END ASSERTIONS ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **





