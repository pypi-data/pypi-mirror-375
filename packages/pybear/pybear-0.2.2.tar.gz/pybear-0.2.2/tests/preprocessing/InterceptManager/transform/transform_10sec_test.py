# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing._InterceptManager._partial_fit. \
    _parallel_constant_finder import _parallel_constant_finder

from pybear.preprocessing._InterceptManager._shared._set_attributes \
    import _set_attributes

from pybear.preprocessing._InterceptManager._transform._transform import \
    _transform

from pybear.utilities import nan_mask



class TestTransform:

    # these tests prove that _transform:
    # - blocks anything that is not numpy ndarray, pandas/polars dataframe,
    #       or ss csc matrix/array
    # - correctly removes columns based on _instructions
    # - format and dtype(s) of the transformed are same as passed
    # - For appended intercept:
    #   - if numpy and ss, constant value is correct and is forced to
    #       dtype of X
    #   - if pd and pl, appended header is correct, and appended constant
    #       is correct dtype (float if num, otherwise object)


    # def _transform(
    #     _X: InternalXContainer,
    #     _instructions: InstructionType
    # ) -> InternalXContainer:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @staticmethod
    @pytest.fixture(scope='module')
    def _const_col_flt():
        # must be in range of shape
        # must match columns in _instructions!
        return {0:np.pi, 1:0, 3:1, 4: np.e, 8: -1}


    @staticmethod
    @pytest.fixture(scope='module')
    def _const_col_str():
        # must be in range of shape
        # must match columns in _instructions!
        return {0:'a', 1:'b', 3:'c', 4:'d', 8:'e'}

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


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
                {'keep': [0, 1, 4], 'delete': [3, 8], 'add': None}
            )


    @pytest.mark.parametrize('_dtype', ('flt', 'str'), scope='module')
    @pytest.mark.parametrize('_has_nan', (True, False), scope='module')
    @pytest.mark.parametrize('_equal_nan', (True, False), scope='module')
    @pytest.mark.parametrize('_instructions',
         (
             {'keep': [1, 3, 8], 'delete': [0, 4], 'add': None},
             {'keep': [0, 1, 4], 'delete': [3, 8], 'add': None},
             {'keep': [0, 1, 3, 4, 8], 'delete': None, 'add': {'Intercept': 1}},
             {'keep': [0, 1, 3, 4, 8], 'delete': None, 'add': None},
             {'keep': [1], 'delete': [0, 3, 4, 8], 'add': None}
         ), scope='module'
     )
    @pytest.mark.parametrize('_format',
        ('np', 'pd', 'pl', 'csc_array', 'csc_matrix'), scope='function'
    )
    def test_output(
        self, _X_factory, _dtype, _has_nan, _equal_nan, _instructions,
        _format, _shape, _columns, _const_col_str, _const_col_flt
    ):

        # Methodology:
        # even tho it is a fixture, _instructions is conditional based on
        # the test and sometimes is modified below.
        #
        # pass (the possibly modified) :fixture: _instructions to
        # _set_attributes() to build the expected column mask that would be
        # applied during transform.
        # pass X and _instructions to _transform.
        # the transformed X should have kept the columns as in the expected
        # column mask.
        # iterate over input X and output X simultaneously, using the
        # expected column mask to map columns in output X to their
        # original locations in input X.
        # Columns that are mapped to each other must be array_equal.
        # if they are, that means:
        # 1) that _transform() used _instructions['delete'] from
        # _make_instructions() to mask the same columns as _set_attributes()
        # did here.
        # 2) _transform correctly deleted the masked columns for diff containers
        # 3) Columns that are not mapped must be constant.

        if _dtype == 'str' and _format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take strings")


        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=_has_nan,
            _format=_format,
            _dtype=_dtype,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=_const_col_flt if _dtype=='flt' else _const_col_str,
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

        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # must do this. even though _instructions is function scope when it is
        # modified by 'if _has_nan and not _equal_nan' below it isnt resetting.
        _wip_instr = deepcopy(_instructions)

        # if has_nan, _X_factory puts nans in every column.
        # therefore when not equal_nan there can be no constant columns.
        if _has_nan and not _equal_nan:
            _wip_instr['keep'] = None
            _wip_instr['delete'] = None
            _constant_columns = {}
        else:
            _constant_columns = \
                {'str': _const_col_str, 'flt': _const_col_flt}[_dtype]


        # get a referee column mask from _set_attributes
        # _set_attributes builds a column mask based on the idxs that are
        # in _wip_instr['keep'] and _wip_instr['delete']
        _, _, _ref_column_mask = _set_attributes(
            _constant_columns,
            _wip_instr,
            _n_features_in = _shape[1]
        )
        del _
        if _constant_columns == {}:
            assert np.all(_ref_column_mask)

        # apply the instructions to X via _transform
        out = _transform(_X_wip, _wip_instr)


        # ASSERTIONS ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # output format is same as given
        assert isinstance(out, _og_format)

        # out shape & _column_mask
        assert out.shape[1] == \
               sum(_ref_column_mask) + isinstance(_wip_instr['add'], dict)

        # output dtypes are same as given ------------------------------
        if _format in ['pd', 'pl']:
            # check the dtypes for the og columns in X first
            assert np.array_equal(
                out.dtypes[:_shape[1]], _og_dtype[_ref_column_mask]
            )
            # check header for og columns
            assert np.array_equal(
                out.columns[:_shape[1]], _columns[_ref_column_mask]
            )
        elif _format == 'np' and '<U' in str(_og_dtype):
            # str dtypes are changing in _transform() at
            # _X = np.hstack((_X, _new_column))
            # there does not seem to be an obvious connection between what
            # the dtype of _value is and the resultant dtype (for example,
            # _X with dtype '<U10' when appending float(1.0), the output dtype
            # is '<U21' (???, maybe the floating points on the float?) )
            assert '<U' in str(out.dtype)
        else:
            # could be np or ss
            # the stacked column and the value in it takes the dtype
            # of the original X
            assert out.dtype == _og_dtype
        # END output dtypes are same as given --------------------------

        # appended intercept -------------------------------------------
        # check the dtype & header for the appended column separately
        if _wip_instr['add'] is not None:  # should only be dict

            _key = list(_wip_instr['add'].keys())[0]
            _value = _wip_instr['add'][_key]

            if _format in ['pd', 'pl']:
                try:
                    float(_value)
                    _dtype_dict = {'pd': np.float64, 'pl': pl.Float64}
                except:
                    _dtype_dict = {'pd': object, 'pl': pl.Object}

                # header
                assert _key in out

                # dtype
                assert out[_key].dtype == _dtype_dict[_format]
                del _dtype_dict
            elif _format == 'np' and '<U' in str(_og_dtype):
                assert out[0, -1] == str(_value)
            elif _format == 'np':
                assert out[0, -1] == _value
            else:
                assert out[[0], [out.shape[1]-1]] == _value
        # END appended intercept ---------------------------------------


        # iterate over input X and output X simultaneously, use _kept_idxs to
        # map columns in output X to their original locations in input X.
        # This ignores any intercept column that may have been appended,
        # which was already tested above.
        _kept_idxs = np.arange(len(_ref_column_mask))[_ref_column_mask]

        _out_idx = -1
        for _og_idx in range(_shape[1]):

            if _og_idx in _kept_idxs:
                _out_idx += 1

            if isinstance(_X_wip, np.ndarray):
                _og_col = _X_wip[:, _og_idx]
                if _og_idx in _kept_idxs:
                    _out_col = out[:, _out_idx]
            elif isinstance(_X_wip, pd.DataFrame):
                _og_col = _X_wip.iloc[:, _og_idx].to_numpy()
                if _og_idx in _kept_idxs:
                    _out_col = out.iloc[:, _out_idx].to_numpy()
                    # verify header matches
                    assert _X_wip.columns[_og_idx] == out.columns[_out_idx]
            elif isinstance(_X_wip, pl.DataFrame):
                _og_col = _X_wip[:, _og_idx].to_numpy()
                if _og_idx in _kept_idxs:
                    _out_col = out[:, _out_idx].to_numpy()
                    # verify header matches
                    assert _X_wip.columns[_og_idx] == out.columns[_out_idx]
            elif hasattr(_X_wip, 'toarray'):
                _og_col = _X_wip.tocsc()[:, [_og_idx]].toarray()
                if _og_idx in _kept_idxs:
                    _out_col = out.tocsc()[:, [_out_idx]].toarray()
            else:
                raise Exception


            if _og_idx in _kept_idxs:
                # then both _og_col and _out_col exist
                # the columns must be array_equal
                assert np.array_equal(
                    _out_col[np.logical_not(nan_mask(_out_col))],
                    _og_col[np.logical_not(nan_mask(_og_col))]
                )
            else:
                # columns not in column mask must therefore be constant
                assert _parallel_constant_finder(_og_col, _equal_nan, 1e-5, 1e-8)

        # END ASSERTIONS ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


class TestHStackDtypesOnNP:

    @pytest.mark.parametrize('_dtype', ('flt', 'str', 'obj'))
    @pytest.mark.parametrize('_value', (1, '1', 'a'))
    def test_various_dtypes_hstacked_to_np(self, _X_factory, _dtype, _value):

        # this tests / shows what happens to the X container dtype when
        # various types of values are appended to X from the 'keep' dictionary

        # when hstacking a str constant to a float array, numpy is
        # changing the array to '<U...'
        # otherwise, the stacked value assumes the existing dtype of X

        X = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format='np',
            _dtype=_dtype,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=(100, 10)
        )

        out = _transform(
            X,
            {'keep': None, 'delete': None, 'add': {'Intercept': _value}}
        )

        if isinstance(_value, str) and _dtype == 'flt':
            assert '<U' in str(out.dtype)
        elif '<U' in str(X.dtype):
            assert '<U' in str(out.dtype)
        else:
            assert X.dtype == out.dtype




