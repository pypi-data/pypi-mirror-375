# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import os
import random
import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.preprocessing._InterceptManager.InterceptManager import \
    InterceptManager as IM

from pybear.preprocessing._InterceptManager._partial_fit. \
    _parallel_constant_finder import _parallel_constant_finder

from pybear.preprocessing._ColumnDeduplicator._partial_fit. \
    _parallel_column_comparer import _parallel_column_comparer

from pybear.base.exceptions import NotFittedError

from pybear.utilities import (
    nan_mask,
    nan_mask_numerical
)


bypass = False


# test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestInitValidation:


    # keep ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_keep',
        (np.e, np.pi, True, False, None, [1,2], {1,2})
    )
    def test_junk_keep(self, X_np, _kwargs, junk_keep):

        _kwargs['keep'] = junk_keep

        with pytest.raises(TypeError):
            IM(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_keep', (-1, 'rubbish', {1:'trash'}, lambda x: 'junk'))
    def test_bad_keep(self, X_np, _kwargs, bad_keep):

        _kwargs['keep'] = bad_keep

        with pytest.raises(ValueError):
            IM(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_keep',
        ('first', 'last', 'random', 'none', {'Intercept': 1},
         'lambda', 'int', 'string')
    )
    def test_good_keep(self, _constants, _columns, _kwargs, good_keep, X_np):

        # get one column of constants from the _constants fixture
        _rand_good_keep_idx = random.choice(list(_constants))

        if good_keep == 'int':
            good_keep = _rand_good_keep_idx
        elif good_keep == 'string':
            good_keep = _columns[_rand_good_keep_idx]
        elif good_keep == 'lambda':
            good_keep = lambda x: _rand_good_keep_idx
        # else:
        #     otherwise good_keep is unchanged

        _kwargs['equal_nan'] = True
        _kwargs['keep'] = good_keep
        IM(**_kwargs).fit_transform(pd.DataFrame(X_np, columns=_columns))
    # END keep ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # equal_nan ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_junk',
        (-1, 0, 1, np.pi, None, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_non_bool_equal_nan(self, X_np, _kwargs, _junk):

        _kwargs['equal_nan'] = _junk

        with pytest.raises(TypeError):
            IM(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_equal_nan', [True, False])
    def test_equal_nan_accepts_bool(self, X_np, _kwargs, _equal_nan):

        _kwargs['equal_nan'] = _equal_nan

        IM(**_kwargs).fit_transform(X_np)
    # END equal_nan ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # rtol & atol ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_junk',
        (True, False, None, 'trash', [1,2], {1,2}, {'a':1}, lambda x: x, min)
    )
    def test_junk_rtol_atol(self, X_np, _kwargs, _param, _junk):

        _kwargs[_param] = _junk

        # non-num are handled by np.allclose, let it raise
        # whatever it will raise
        with pytest.raises(Exception):
            IM(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_bad', (-np.pi, -2, -1, True, False))
    def test_bad_rtol_atol(self, X_np, _kwargs, _param, _bad):

        _kwargs[_param] = _bad

        with pytest.raises(ValueError):
            IM(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_good', (1e-5, 1e-6, 1e-1, 1_000_000))
    def test_good_rtol_atol(self, X_np, _kwargs, _param, _good):

        _kwargs[_param] = _good

        IM(**_kwargs).fit_transform(X_np)
    # END rtol & atol ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

# END test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestX:

    # - accepts ndarray, pd.DataFrame, pl.DataFrame, and all ss
    # - cannot be None
    # - must be 2D
    # - must have at least 1 column
    # - must have at least 1 sample
    # - allows nan
    # - partial_fit/transform num columns must equal num columns seen during first fit


    # CONTAINERS #######################################################
    @pytest.mark.parametrize('_junk_X',
        (-1, 0, 1, 3.14, None, 'junk', [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_X(self, _kwargs, X_np, _junk_X):

        TestCls = IM(**_kwargs)

        # these are caught by base.validate_data.
        with pytest.raises(ValueError):
            TestCls.partial_fit(_junk_X)

        with pytest.raises(ValueError):
            TestCls.fit(_junk_X)

        with pytest.raises(ValueError):
            TestCls.fit_transform(_junk_X)

        TestCls.fit(X_np)

        with pytest.raises(ValueError) as e:
            TestCls.transform(_junk_X)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            TestCls.inverse_transform(_junk_X)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('py_list', 'py_tuple'))
    def test_rejects_invalid_container(self, X_np, _columns, _kwargs, _format):

        assert _format in ('py_list', 'py_tuple')

        TestCls = IM(**_kwargs)

        if _format == 'py_list':
            _X_wip = list(map(list, X_np))
        elif _format == 'py_tuple':
            _X_wip = tuple(map(tuple, X_np))

        with pytest.raises(ValueError):
            TestCls.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            TestCls.fit(_X_wip)

        with pytest.raises(ValueError):
            TestCls.fit_transform(_X_wip)

        TestCls.fit(X_np) # fit on numpy, not the converted data

        with pytest.raises(ValueError) as e:
            TestCls.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            TestCls.inverse_transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    def test_good_X_container(
        self, _X_factory, _columns, _shape, _kwargs, _constants, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=_constants, _noise=0, _zeros=None,
            _shape=_shape
        )


        _IM = IM(**_kwargs)

        _IM.partial_fit(_X_wip)

        _IM.fit(_X_wip)

        _IM.fit_transform(_X_wip)

        TRFM_X = _IM.transform(_X_wip)

        _IM.inverse_transform(TRFM_X)

    # END CONTAINERS ###################################################


    # SHAPE ############################################################
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_rejects_1D(self, X_np, _kwargs, _format):

        # validation order is
        # 1) check_fitted (for transform & inv_transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits, transform & inv_transform, 1D will always catch first

        _IM = IM(**_kwargs)

        if _format == 'np':
            _X_wip = X_np[:, 0]
        elif _format == 'pd':
            _X_wip = pd.Series(X_np[:, 0])
        elif _format == 'pl':
            _X_wip = pl.Series(X_np[:, 0])
        else:
            raise Exception

        with pytest.raises(ValueError):
            _IM.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _IM.fit(_X_wip)

        with pytest.raises(ValueError):
            _IM.fit_transform(_X_wip)

        _IM.fit(X_np)

        with pytest.raises(ValueError) as e:
            _IM.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            _IM.inverse_transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_num_cols', (0, 1, 2))
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_array'))
    def test_X_2D_number_of_columns(
        self, X_np, _kwargs, _columns, _format, _num_cols
    ):

        # validation order is
        # 1) check_fitted (for transform & inv_transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits, transform & inv_transform, validate_data will catch
        # for all methods the min number of columns is 1

        _base_X = X_np[:, :_num_cols]
        if _format == 'np':
            _X_wip = _base_X
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_base_X, columns=_columns[:_num_cols])
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_base_X, schema=list(_columns[:_num_cols]))
        elif _format == 'coo_array':
            _X_wip = ss.coo_array(_base_X)
        else:
            raise Exception

        assert len(_X_wip.shape) == 2
        assert _X_wip.shape[1] == _num_cols

        _IM = IM(**_kwargs)

        if _num_cols == 0:
            with pytest.raises(ValueError):
                _IM.partial_fit(_X_wip)
            with pytest.raises(ValueError):
                _IM.fit(_X_wip)
            with pytest.raises(ValueError):
                _IM.fit_transform(_X_wip)
            _IM.fit(X_np)
            with pytest.raises(ValueError) as e:
                _IM.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            with pytest.raises(ValueError) as e:
                _IM.inverse_transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)
        else:
            _IM.partial_fit(_X_wip)
            _IM.fit(_X_wip)
            _IM.fit_transform(_X_wip)
            TRFM_X = _IM.transform(_X_wip)
            _IM.inverse_transform(TRFM_X)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'lil_matrix'))
    def test_rejects_no_samples(self, _shape, _kwargs, X_np, _format):

        _IM = IM(**_kwargs)

        _X_base = np.empty((0, _shape[1]), dtype=np.float64)

        if _format == 'np':
            _X_wip = _X_base
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_X_base)
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_X_base)
        elif _format == 'lil_matrix':
            _X_wip = ss.lil_matrix(_X_base)
        else:
            raise Exception


        with pytest.raises(ValueError):
            _IM.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _IM.fit(_X_wip)

        with pytest.raises(ValueError):
            _IM.fit_transform(_X_wip)

        _IM.fit(X_np)

        with pytest.raises(ValueError) as e:
            _IM.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            _IM.inverse_transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('_diff', ('more', 'less', 'same'))
    def test_rejects_bad_num_features(
        self, _X_factory, _shape, _constants, _kwargs, _columns, X_np,
        _format, _diff
    ):
        # ** ** ** **
        # THERE CANNOT BE "BAD NUM FEATURES" FOR fit & fit_transform
        # THE MECHANISM FOR partial_fit & transform IS DIFFERENT FROM inverse_transform
        # partial_fit & transform is handled by _check_n_features
        # inverse_transform has special code
        # ** ** ** **

        # SHOULD RAISE ValueError WHEN COLUMNS DO NOT EQUAL NUMBER OF
        # COLUMNS SEEN ON FIRST FIT

        _new_shape_dict = {
            'same': _shape,
            'less': (_shape[0], _shape[1] - 1),
            'more': (_shape[0], 2 * _shape[1])
        }
        _columns_dict = {
            'same': _columns,
            'less': _columns[:-1],
            'more': np.hstack((_columns, np.char.upper(_columns)))
        }
        _new_constants_dict = {
            'same': _constants,
            'less': {0: 0, _shape[1] - 2: np.nan},
            'more': _constants
        }

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns_dict[_diff],
            _constants=_new_constants_dict[_diff],
            _zeros=0,
            _shape=_new_shape_dict[_diff]
        )

        _IM = IM(**_kwargs)
        _IM.fit(X_np)

        if _diff == 'same':
            _IM.partial_fit(_X_wip)
            _IM.transform(_X_wip)
        else:
            with pytest.raises(ValueError) as e:
                _IM.partial_fit(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            with pytest.raises(ValueError) as e:
                _IM.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)

    # END SHAPE ########################################################


    @pytest.mark.parametrize('_format', ('pd', 'pl'))
    @pytest.mark.parametrize('fst_fit_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    @pytest.mark.parametrize('scd_fit_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    @pytest.mark.parametrize('trfm_columns', ('DF1', 'DF2', 'NO_HDR_DF'))
    def test_except_or_warn_on_different_headers(
        self, _X_factory, _kwargs, _columns, _shape, _format,
        fst_fit_columns, scd_fit_columns, trfm_columns
    ):

        # TEST ValueError WHEN SEES A DF HEADER DIFFERENT FROM FIRST-SEEN HEADER

        _factory_kwargs = {
            '_dupl':None, '_format':_format, '_dtype':'flt',
            '_has_nan':False, '_constants': None, '_shape':_shape
        }

        # np.flip(_columns) is bad columns
        _col_dict = {'DF1': _columns, 'DF2': np.flip(_columns), 'NO_HDR_DF': None}

        fst_fit_X = _X_factory(_columns=_col_dict[fst_fit_columns], **_factory_kwargs)
        scd_fit_X = _X_factory(_columns=_col_dict[scd_fit_columns], **_factory_kwargs)
        trfm_X = _X_factory(_columns=_col_dict[trfm_columns], **_factory_kwargs)

        TestCls = IM(**_kwargs)

        _objs = [fst_fit_columns, scd_fit_columns, trfm_columns]
        # EXCEPT IF 2 DIFFERENT HEADERS ARE SEEN
        pybear_exception = 0
        pybear_exception += bool('DF1' in _objs and 'DF2' in _objs)
        # POLARS ALWAYS HAS A HEADER
        if _format == 'pl':
            pybear_exception += (len(np.unique(_objs)) > 1)
        # IF FIRST FIT WAS WITH PD NO HEADER, THEN ANYTHING GETS THRU ON
        # SUBSEQUENT partial_fits AND transform
        if _format == 'pd':
            pybear_exception -= bool(fst_fit_columns == 'NO_HDR_DF')
        pybear_exception = max(0, pybear_exception)

        # WARN IF HAS-HEADER AND PD NOT-HEADER BOTH PASSED DURING fits/transform
        # POLARS SHOULDNT GET IN HERE, WILL ALWAYS EXCEPT, ALWAYS HAS A HEADER
        pybear_warn = 0
        if not pybear_exception:
            pybear_warn += ('NO_HDR_DF' in _objs)
            # IF NONE OF THEM HAD A HEADER, THEN NO WARNING
            pybear_warn -= ('DF1' not in _objs and 'DF2' not in _objs)
            pybear_warn = max(0, pybear_warn)

        del _objs

        if pybear_exception:
            # this raises in _check_feature_names
            TestCls.partial_fit(fst_fit_X)
            with pytest.raises(ValueError) as e:
                TestCls.partial_fit(scd_fit_X)
                TestCls.transform(trfm_X)
            assert not isinstance(e.value, NotFittedError)
        elif pybear_warn:
            TestCls.partial_fit(fst_fit_X)
            with pytest.warns():
                TestCls.partial_fit(scd_fit_X)
                TestCls.transform(trfm_X)
        else:
            # SHOULD NOT EXCEPT OR WARN
            TestCls.partial_fit(fst_fit_X)
            TestCls.partial_fit(scd_fit_X)
            TestCls.transform(trfm_X)


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestPartialFit:


    @pytest.mark.parametrize('_y',
        (-1,0,1, np.pi, True, False, None, 'trash', [1,2], {1,2}, {'a':1},
        lambda x: x, min)
    )
    def test_fit_partial_fit_accept_Y_equals_anything(self, _kwargs, X_np, _y):
        IM(**_kwargs).partial_fit(X_np, _y)
        IM(**_kwargs).fit(X_np, _y)


    def test_conditional_access_to_partial_fit_and_fit(self, X_np, _kwargs):

        TestCls = IM(**_kwargs)

        # 1) partial_fit() should allow unlimited number of subsequent partial_fits()
        for _ in range(5):
            TestCls.partial_fit(X_np)

        TestCls._reset()

        # 2) one call to fit() should allow subsequent attempts to partial_fit()
        TestCls.fit(X_np)
        TestCls.partial_fit(X_np)

        TestCls._reset()

        # 3) one call to fit() should allow later attempts to fit() (2nd fit will reset)
        TestCls.fit(X_np)
        TestCls.fit(X_np)

        TestCls._reset()

        # 4) a call to fit() after a previous partial_fit() should be allowed
        TestCls.partial_fit(X_np)
        TestCls.fit(X_np)

        TestCls._reset()

        # 5) fit_transform() should allow calls ad libido
        for _ in range(5):
            TestCls.fit_transform(X_np)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'lil_array'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _constants, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=_constants, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        # verify _X_wip does not mutate in partial_fit()
        _IM = IM(**_kwargs).partial_fit(_X_wip)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape
        # need equal_nan because _constants has nans
        if isinstance(_X_wip, np.ndarray):
            # if numpy output, is C order
            assert _X_wip.flags['C_CONTIGUOUS'] is True
            assert np.array_equal(_X_wip_before, _X_wip, equal_nan=True)
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip, 'columns'):  # DATAFRAMES
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(
                _X_wip.toarray(), _X_wip_before.toarray(), equal_nan=True
            )
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    @pytest.mark.parametrize('_keep',
        ('first', 'last', 'random', 'none', 'int', 'lambda', {'Intercept':1})
    )
    def test_many_partial_fits_equal_one_big_fit(
        self, _kwargs, _shape, _constants, X_np, _keep
    ):

        # **** **** **** **** **** **** **** **** **** **** **** **** ****
        # THIS TEST IS CRITICAL FOR VERIFYING THAT transform PULLS THE
        # SAME COLUMN INDICES FOR ALL CALLS TO transform() WHEN
        # keep=='random'
        # **** **** **** **** **** **** **** **** **** **** **** **** ****

        # X_np has no nans

        _rand_keep_idx = random.choice(list(_constants))
        if _keep == 'int':
            _keep = _rand_keep_idx
        elif _keep == 'lambda':
            _keep = lambda x: _rand_keep_idx
        # else:
            # _keep is not changed

        _kwargs['equal_nan'] = True
        _kwargs['keep'] = _keep

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST THAT ONE-SHOT partial_fit/transform == ONE-SHOT fit/transform
        OneShotPartialFitTestCls = IM(**_kwargs).partial_fit(X_np)

        OneShotFullFitTestCls = IM(**_kwargs).fit(X_np)

        # constant_columns are equal -- -- -- --
        _ = OneShotPartialFitTestCls.constant_columns_
        __ = OneShotFullFitTestCls.constant_columns_
        assert np.array_equal(list(_.keys()), list(__.keys()))
        # need to turn to strings because of nans
        # X_np _has_nan=False, but constants have a column of np.nans
        assert np.array_equal(
            list(map(str, _.values())), list(map(str, __.values()))
        )
        del _, __
        # END constant_columns are equal -- -- -- --
        
        ONE_SHOT_PARTIAL_FIT_TRFM_X = \
            OneShotPartialFitTestCls.transform(X_np, copy=True)

        ONE_SHOT_FULL_FIT_TRFM_X = \
            OneShotFullFitTestCls.transform(X_np, copy=True)

        # since keep=='random' can keep different column indices for
        # the different instances (OneShotPartialFitTestCls,
        # OneShotFullFitTestCls), it would probably be better to
        # avoid a mountain of complexity to prove out conditional
        # column equalities between the 2, just assert shape is same.
        assert ONE_SHOT_PARTIAL_FIT_TRFM_X.shape == \
               ONE_SHOT_FULL_FIT_TRFM_X.shape

        if _keep != 'random':
            # this has np.nan in it, convert to str
            assert np.array_equal(
                ONE_SHOT_PARTIAL_FIT_TRFM_X.astype(str),
                ONE_SHOT_FULL_FIT_TRFM_X.astype(str)
            ), f"one shot partial fit trfm X != one shot full fit trfm X"

        del OneShotPartialFitTestCls, OneShotFullFitTestCls
        del ONE_SHOT_PARTIAL_FIT_TRFM_X, ONE_SHOT_FULL_FIT_TRFM_X

        # END TEST THAT ONE-SHOT partial_fit/transform==ONE-SHOT fit/transform
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST PARTIAL FIT CONSTANTS ARE THE SAME WHEN FULL DATA
        # IS partial_fit() 2X
        SingleFitTestClass = IM(**_kwargs).fit(X_np)
        _ = SingleFitTestClass.constant_columns_

        DoublePartialFitTestClass = IM(**_kwargs)
        DoublePartialFitTestClass.partial_fit(X_np)
        __ = DoublePartialFitTestClass.constant_columns_
        DoublePartialFitTestClass.partial_fit(X_np)
        ___ = DoublePartialFitTestClass.constant_columns_

        assert np.array_equal(list(_.keys()), list(__.keys()))
        assert np.array_equal(list(_.keys()), list(___.keys()))
        for k, v in _.items():
            assert np.array_equal(str(v), str(__[k]))
            assert np.array_equal(str(v), str(___[k]))

        del _, __, ___, SingleFitTestClass, DoublePartialFitTestClass

        # END PARTIAL FIT CONSTANTS ARE THE SAME WHEN FULL DATA IS partial_fit() 2X
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **
        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **
        # TEST MANY PARTIAL FITS == ONE BIG FIT

        # STORE CHUNKS TO ENSURE THEY STACK BACK TO THE ORIGINAL X
        _chunks = 5
        X_CHUNK_HOLDER = []
        for row_chunk in range(_chunks):
            _mask_start = row_chunk * _shape[0] // _chunks
            _mask_end = (row_chunk + 1) * _shape[0] // _chunks
            X_CHUNK_HOLDER.append(X_np[_mask_start:_mask_end, :])
        del _mask_start, _mask_end

        assert np.array_equiv(
            np.vstack(X_CHUNK_HOLDER).astype(str), X_np.astype(str)
        ), f"agglomerated X chunks != original X"

        PartialFitTestCls = IM(**_kwargs)
        OneShotFitTransformTestCls = IM(**_kwargs)

        # PIECEMEAL PARTIAL FIT ****************************************
        for X_CHUNK in X_CHUNK_HOLDER:
            PartialFitTestCls.partial_fit(X_CHUNK)

        # PIECEMEAL TRANSFORM ******************************************
        # THIS CANT BE UNDER THE partial_fit LOOP, ALL FITS MUST BE DONE
        # BEFORE DOING ANY TRFMS
        PARTIAL_TRFM_X_HOLDER = []
        for X_CHUNK in X_CHUNK_HOLDER:
            PARTIAL_TRFM_X_HOLDER.append(PartialFitTestCls.transform(X_CHUNK))

        # AGGLOMERATE PARTIAL TRFMS FROM PARTIAL FIT
        FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM = \
            np.vstack(PARTIAL_TRFM_X_HOLDER)

        del PARTIAL_TRFM_X_HOLDER
        # END PIECEMEAL TRANSFORM **************************************

        # DO ONE-SHOT TRANSFORM OF X ON THE PARTIALLY FIT INSTANCE
        FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM = \
            PartialFitTestCls.transform(X_np)

        del PartialFitTestCls


        if _keep != 'random':
            # ONE-SHOT FIT TRANSFORM
            FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM = \
                OneShotFitTransformTestCls.fit_transform(X_np)

            del OneShotFitTransformTestCls

            # ASSERT ALL AGGLOMERATED X TRFMS ARE EQUAL
            assert np.array_equiv(
                FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM.astype(str),
                FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM.astype(str)
            ), f"trfm X from partial fit / partial trfm != one-shot fit/trfm X"

            assert np.array_equiv(
                FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM.astype(str),
                FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM.astype(str)
            ), f"trfm X from partial fits / one-shot trfm != one-shot fit/trfm X"
        elif _keep == 'random':
            assert np.array_equiv(
                FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM.astype(str),
                FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM.astype(str)
            ), (f"trfm X from partial fit / partial trfm != "
             f"trfm X from partial fit / one-shot trfm")

        # TEST MANY PARTIAL FITS == ONE BIG FIT
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (False, 5))
    def test_constant_columns_accuracy_over_many_partial_fits(
        self, _kwargs, _X_factory, _dtype, _has_nan
    ):

        # verify correct progression of reported constants as partial
        # fits are done. rig a set of arrays that have progressively
        # decreasing constants

        _chunk_shape = (50, 20)

        _start_constants = {3: 1, 5: 1, _chunk_shape[1] - 2: 1}

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['equal_nan'] = True

        PartialFitTestCls = IM(**_new_kwargs)

        # build a pool of non-constants to fill the constants in X along the way
        # build a starting data object for first partial fit, using full constants
        # build a y vector
        # do a verification partial_fit, assert reported constants for original X
        # make a holder for all the different _wip_Xs, to do one big fit at the end
        # for however many times u want to do this:
        #   randomly replace one of the constants with non-constant column
        #   partial_fit
        #   assert reported constants - should be one less (the randomly chosen)
        # at the very end, stack all the _wip_Xs, do one big fit, verify constants

        _pool_X = _X_factory(
            _constants=None,  # <============
            _dupl=None, _has_nan=_has_nan, _format='np', _dtype=_dtype,
            _columns=None, _noise=0, _zeros=None, _shape=_chunk_shape
        )

        _wip_X = _X_factory(
            _constants=_start_constants,  # <============
            _dupl=None, _has_nan=_has_nan, _format='np', _dtype=_dtype,
            _columns=None, _noise=0, _zeros=None, _shape=_chunk_shape
        )

        y_np = np.random.randint(0, 2, (_chunk_shape[0]))

        # verify IM sees the constant columns correctly ** * ** * ** *
        # this also sets the original constants columns in PartialFitTestCls
        _constant_columns = \
            PartialFitTestCls.partial_fit(_wip_X, y_np).constant_columns_
        assert len(_constant_columns) == len(_start_constants)
        for idx, v in _start_constants.items():
            if str(v) == 'nan':
                assert str(v) == str(_constant_columns[idx])
            else:
                assert v == _constant_columns[idx]
        del _constant_columns
        # END verify IM sees the constant columns correctly ** * ** * **

        # create a holder for the the original constant column idxs
        _const_pool = list(_start_constants)

        X_HOLDER = []
        X_HOLDER.append(_wip_X)

        # take out only half of the constants (arbitrary) v^v^v^v^v^v^v^
        for trial in range(len(_const_pool)//2):

            random_const_idx = np.random.choice(_const_pool, 1, replace=False)[0]

            # take the random constant of out _start_constants and
            # _const_pool, and take a column out of the X pool to patch
            # the constant in _wip_X
            _start_constants.pop(random_const_idx)
            _const_pool.remove(random_const_idx)

            # column from X should be constant, column from pool shouldnt be
            # but verify anyway ** ** ** ** ** ** ** ** ** ** ** ** **
            _from_X = _wip_X[:, random_const_idx]
            _from_pool = _pool_X[:, random_const_idx]
            assert not np.array_equal(
                _from_X[np.logical_not(nan_mask(_from_X))],
                _from_pool[np.logical_not(nan_mask(_from_pool))]
            )
            del _from_X, _from_pool
            # END verify ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

            _wip_X[:, random_const_idx] = _pool_X[:, random_const_idx]

            X_HOLDER.append(_wip_X)

            # fit PartialFitTestCls on the new _wip_X
            # verify correctly reported constants after this partial_fit
            _constant_columns = \
                PartialFitTestCls.partial_fit(_wip_X, y_np).constant_columns_
            assert len(_constant_columns) == len(_start_constants)
            for idx, v in _start_constants.items():
                if str(v) == 'nan':
                    assert str(v) == str(_constant_columns[idx])
                else:
                    assert v == _constant_columns[idx]
            del _constant_columns

        # END take out only half of the constants (arbitrary) v^v^v^v^v^

        # we now have full X_HOLDER, which holds _wip_Xs with progressively
        # fewer columns of constants
        # and PartialFitTestCls, which was fit sequentially on the _wip_Xs

        _partial_fit_constant_columns = PartialFitTestCls.constant_columns_
        # do a one-shot fit, compare results
        # stack all the _wip_Xs
        OneShotFitTestCls = IM(**_new_kwargs).fit(np.vstack(X_HOLDER), y_np)
        _one_shot_constant_columns = OneShotFitTestCls.constant_columns_
        # remember that _start_constants has constant idxs popped out of it
        # as non-constant columns were put into _wip_X
        assert len(_one_shot_constant_columns) == len(_start_constants)
        assert len(_partial_fit_constant_columns) == len(_start_constants)
        for idx, v in _start_constants.items():
            if str(v) == 'nan':
                assert str(v) == str(_one_shot_constant_columns[idx])
                assert str(v) == str(_partial_fit_constant_columns[idx])
            else:
                assert v == _one_shot_constant_columns[idx]
                assert v == _partial_fit_constant_columns[idx]

    # dont really need to test accuracy, see _partial_fit


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestTransform:


    # - num columns must equal num columns seen during fit
    # - allows nan
    # - output is C contiguous
    # - does not mutate passed X


    @pytest.mark.parametrize('_copy',
        (-1, 0, 1, 3.14, True, False, None, 'junk', [0, 1], (1,), {'a': 1}, min)
    )
    def test_copy_validation(self, X_np, _shape, _kwargs, _copy):

        _IM = IM(**_kwargs)
        _IM.fit(X_np)

        if isinstance(_copy, (bool, type(None))):
            _IM.transform(X_np, copy=_copy)
        else:
            with pytest.raises(TypeError):
                _IM.transform(X_np, copy=_copy)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _constants, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=_constants, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = IM(**_kwargs)
        TestCls.set_output(transform=output_type).fit(_X_wip)
        TRFM_X = TestCls.transform(_X_wip)

        # if output_type is None, should return same type as given
        # if 'default', should return np array no matter what given
        # if 'pandas' or 'polars', should return pd/pl df no matter what given
        _output_type_dict = {
            None: type(_X_wip), 'default': np.ndarray, 'polars': pl.DataFrame,
            'pandas': pd.DataFrame
        }
        assert isinstance(TRFM_X, _output_type_dict[output_type]), \
            (f"X input type {type(_X_wip)}, X output type {type(TRFM_X)}, "
             f"expected output_type {output_type}")


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'lil_array'))
    def test_X_is_not_mutated(
            self, _X_factory, _columns, _shape, _kwargs, _constants, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=_constants, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        _IM = IM(**_kwargs).fit(_X_wip)

        # verify _X_wip does not mutate in transform() with copy=True
        TRFM_X = _IM.transform(_X_wip, copy=True)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip_before, np.ndarray):
            assert np.array_equal(_X_wip_before, _X_wip, equal_nan=True)
            # if numpy output, is C order
            assert _X_wip.flags['C_CONTIGUOUS'] is True
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip_before, 'columns'):    # DATAFRAMES
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(
                _X_wip.toarray(), _X_wip_before.toarray(), equal_nan=True
            )
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csr_array'))
    @pytest.mark.parametrize('X_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('has_nan', (True, False))
    @pytest.mark.parametrize('equal_nan', (True, False))
    @pytest.mark.parametrize('constants',
        ('constants1', 'constants2', 'constants3')
    )
    @pytest.mark.parametrize('keep',
        ('first', 'last', 'random', 'none', 'int', 'string', 'callable',
        {'Intercept': 1})
    )
    def test_accuracy(
        self, _X_factory, _kwargs, _columns, _shape, X_format, X_dtype,
        has_nan, equal_nan, constants, keep
    ):

        # validate the test parameters -------------
        assert keep in ['first', 'last', 'random', 'none'] or \
                    isinstance(keep, (int, dict, str)) or callable(keep)
        assert isinstance(has_nan, bool)
        assert isinstance(equal_nan, bool)
        # dont need to validate X_format, X_factory will do it
        assert X_dtype in ('flt', 'int', 'str', 'obj', 'hybrid')
        # END validate the test parameters -------------

        # skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if X_dtype not in ['flt', 'int'] and X_format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take str")

        if X_format == 'np' and X_dtype == 'int' and has_nan:
            pytest.skip(reason=f"numpy int dtype cant take 'nan'")
        # END skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        if constants == 'constants1':
            constants = None
        elif constants == 'constants2':
            if X_dtype in ('flt', 'int'):
                constants = {0: 1, 2: 1, 9: 1}
            elif X_dtype in ('str', 'obj', 'hybrid'):
                constants = {0: 1, 2: 'a', 9: 'b'}
            else:
                raise Exception
        elif constants == 'constants3':
            if X_dtype in ('flt', 'int'):
                constants = {0: 1, 1: 1, 6: np.nan, 8: 1}
            elif X_dtype in ('str', 'obj', 'hybrid'):
                constants = {0: 'a', 1: 'b', 6: 'nan', 8: '1'}
            else:
                raise Exception
        else:
            raise Exception
        # END set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=has_nan,
            _format=X_format,
            _dtype=X_dtype,
            _columns=_columns,
            _constants=constants,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )

        # retain original dtype(s) v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if isinstance(_X_wip, (pd.DataFrame, pl.DataFrame)):
            # need to adjust the pd/pl dtypes if keep is dict
            if isinstance(keep, dict):
                # in _transform(), when keep is a dict, it looks at whether
                # the dict value is numerical; if so, the dtype of the
                # appended column for a df is float64, if not num then
                # dtype is object. this constructs the appended column,
                # puts it on the df, then gets all the dtypes.

                _key = list(keep.keys())[0]
                _value = keep[_key]
                if isinstance(_X_wip, (pd.DataFrame, pl.DataFrame)):
                    # -----------------
                    try:
                        float(_value)
                        _dtype = {'pd': np.float64, 'pl': pl.Float64}
                    except:
                        _dtype = {'pd': object, 'pl': pl.Object}
                    # -----------------
                    if isinstance(_X_wip, pd.DataFrame):
                        _vector = pd.DataFrame(
                            {_key: np.full(_X_wip.shape[0], _value)}
                        )
                        _og_dtype = pd.concat(
                            (_X_wip, _vector.astype(_dtype[X_format])), axis=1
                        ).dtypes
                    elif isinstance(_X_wip, pl.DataFrame):
                        _vector = np.full((_shape[0], 1), _value)
                        if _dtype['pl'] == pl.Float64:
                            # need to do this so that polars can cast the
                            # dtype. it wont cast it on the numpy array
                            _vector = list(map(float, _vector.ravel()))
                        _vector = pl.DataFrame({_key: _vector})
                        _og_dtype = _X_wip.with_columns(
                            _vector.cast(_dtype['pl'])
                        ).dtypes
                del _key, _value, _vector
            else:
                _og_dtype = _X_wip.dtypes
            # need np.array for pl dtypes
            _og_dtype = np.array(_og_dtype)
        else:
            # if np or ss
            # dont need to worry about keep is dict (appending a column),
            # X will still have one dtype
            _og_dtype = _X_wip.dtype
        # END retain original dtype(s) v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # set keep v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if keep == 'string':
            keep = _columns[0]
        elif keep == 'int':
            if constants:
                keep = sorted(list(constants.keys()))[-1]
            else:
                keep = 0
        elif keep == 'callable':
            if constants:
                keep = lambda x: sorted(list(constants.keys()))[-1]
            else:
                keep = lambda x: 0
        else:
            # keep is not changed
            pass
        # END set keep v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # set _kwargs
        _kwargs['keep'] = keep
        _kwargs['equal_nan'] = equal_nan

        TestCls = IM(**_kwargs)

        # get exp_constants & manage error conditions ------------------
        exp_constants = deepcopy(constants or {})
        if has_nan and not equal_nan:
            exp_constants = {}

        # if there are constants, and any of them are nan-like, but
        # not equal_nan, then that column cant be a constant, so remove
        if not equal_nan and len(exp_constants) and \
                any(nan_mask(np.array(list(exp_constants.values())))):
            exp_constants = \
                {k:v for k,v in exp_constants.items() if str(v) != 'nan'}

        # if data is not pd/pl and user put in keep as feature_str, will raise
        raise_for_no_header_str_keep = False
        if X_format not in ['pd', 'pl'] and isinstance(keep, str) and \
                keep not in ('first', 'last', 'random', 'none'):
            raise_for_no_header_str_keep += 1

        # if data has no constants and
        # user put in keep as feature_str/int/callable, will raise
        raise_for_keep_non_constant = False
        if not exp_constants:
            if callable(keep):
                raise_for_keep_non_constant += 1
            if isinstance(keep, int):
                raise_for_keep_non_constant += 1
            if isinstance(keep, str) and \
                    keep not in ('first', 'last', 'random', 'none'):
                raise_for_keep_non_constant += 1
        # END get exp_constants & manage error conditions --------------

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        if raise_for_no_header_str_keep or raise_for_keep_non_constant:
            with pytest.raises(ValueError):
                TestCls.fit(_X_wip)
            pytest.skip(reason=f"cant do anymore tests without fit")
        else:
            TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        del raise_for_keep_non_constant, raise_for_no_header_str_keep


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # returned format is same as given format
        assert isinstance(TRFM_X, type(_X_wip))

        # if numpy output, is C order
        if isinstance(TRFM_X, np.ndarray):
            assert TRFM_X.flags['C_CONTIGUOUS'] is True

        # returned dtypes are same as given dtypes ** * ** * ** * ** *
        if isinstance(TRFM_X, (pd.DataFrame, pl.DataFrame)):
            MASK = TestCls.column_mask_
            if isinstance(keep, dict):
                # remember that above we stacked a fudged intercept column
                # to the df to get all the dtypes in one shot. so now here
                # we need to adjust column_mask_ to get the extra column
                MASK = np.hstack((MASK, np.array([True], dtype=bool)))

            # dtypes could be shape[1] or (shape[1] + isinstance(keep, dict))
            assert np.array_equal(TRFM_X.dtypes, _og_dtype[MASK])
            del MASK
        elif '<U' in str(_og_dtype):
            # str dtypes are changing in _transform() at
            # _X = np.hstack((_X, _new_column))
            # there does not seem to be an obvious connection between what
            # the dtype of _value is and the resultant dtype (for example,
            # _X with dtype '<U10' when appending float(1.0), the output
            # dtype is '<U21' (???, maybe the floating points on the float?))
            assert '<U' in str(TRFM_X.dtype)
        elif os.name == 'nt' and 'int' in str(_og_dtype).lower():
            # on windows (verified not macos or linux), int dtypes are
            # changing to int64, in _transform() at
            # _X = np.hstack((_X, _new_column))
            assert 'int' in str(TRFM_X.dtype).lower()
        else:
            assert TRFM_X.dtype == _og_dtype
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        _sorted_constant_idxs = sorted(list(exp_constants.keys()))

        # for retained columns, assert they are equal to themselves in
        # the original data. if the column is not retained, then assert
        # the column in the original data is a constant
        _new_idx = -1
        _kept_idxs = np.arange(len(TestCls.column_mask_))[TestCls.column_mask_]

        if len(_sorted_constant_idxs):
            _num_kept_constants = sum([i in _kept_idxs for i in _sorted_constant_idxs])
            if keep == 'first':
                assert _sorted_constant_idxs[0] in _kept_idxs
                assert _num_kept_constants == 1
            elif keep == 'last':
                assert _sorted_constant_idxs[-1] in _kept_idxs
                assert _num_kept_constants == 1
            elif keep == 'random':
                assert _num_kept_constants == 1
            elif isinstance(keep, dict) or keep == 'none':
                assert _num_kept_constants == 0
            del _num_kept_constants
        else:
            # if no constants, all columns are kept
            assert np.array_equal(_kept_idxs, range(_X_wip.shape[1]))


        for _idx in range(_shape[1]):

            if _idx in _kept_idxs:
                _new_idx += 1

            if isinstance(_X_wip, np.ndarray):
                _out_col = TRFM_X[:, [_new_idx]]
                _og_col = _X_wip[:, [_idx]]
            elif isinstance(_X_wip, pd.DataFrame):
                _out_col = TRFM_X.iloc[:, [_new_idx]].to_numpy()
                _og_col = _X_wip.iloc[:, [_idx]].to_numpy()
            elif isinstance(_X_wip, pl.DataFrame):
                _out_col = TRFM_X[:, [_new_idx]].to_numpy()
                _og_col = _X_wip[:, [_idx]].to_numpy()
            else:
                _out_col = TRFM_X.tocsc()[:, [_new_idx]].toarray()
                _og_col = _X_wip.tocsc()[:, [_idx]].toarray()

            try:
                _out_col = _out_col.astype(np.float64)
                _og_col = _og_col.astype(np.float64)
            except:
                pass

            if _idx in _kept_idxs:
                assert _parallel_column_comparer(_out_col, _og_col, 1e-5, 1e-8, True)
            else:
                out = _parallel_constant_finder(_og_col, equal_nan, 1e-5, 1e-8)

                # a uuid would be returned if the column is not constant
                assert not isinstance(out, uuid.UUID)

        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_one_all_nans(self, _X_factory, _kwargs, _shape, _equal_nan):

        # nans are put in manually later
        _X = _X_factory(
            _dupl=None, _has_nan=False, _format='np', _dtype='flt',
            _columns=None, _constants={0:1, 1:2}, _zeros=None,
            _shape=(_shape[0], 3)    # <====== 3 columns
        )

        # set a column to all nans
        _X[:, -1] = np.nan
        # verify last column is all nans
        assert all(nan_mask_numerical(_X[:, -1]))

        # conftest _kwargs 'keep' == 'first'
        _kwargs['equal_nan'] = _equal_nan
        TRFM_X = IM(**_kwargs).fit_transform(_X)

        if _equal_nan:
            # last 2 columns should drop, should have 1 column, not np.nan
            assert TRFM_X.shape[1] == 1
            assert np.array_equal(TRFM_X[:, 0], _X[:, 0])
            assert not any(nan_mask_numerical(TRFM_X[:, -1]))
        elif not _equal_nan:
            # 2nd column should drop, should have 2 columns, last is all np.nan
            assert TRFM_X.shape[1] == 2
            assert np.array_equal(TRFM_X[:, 0], _X[:, 0])
            assert all(nan_mask_numerical(TRFM_X[:, 1]))


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_two_all_nans(self, _X_factory, _kwargs, _shape, _equal_nan):

        # nans are put in manually later
        _X = _X_factory(
            _dupl=None, _has_nan=False, _format='np', _dtype='flt',
            _columns=None, _constants={0:1, 1:2}, _zeros=None,
            _shape=(_shape[0], 4)    # <======== 4 columns
        )

        # set last 2 columns to all nans
        _X[:, [-2, -1]] = np.nan
        # verify last columns are all nans
        assert all(nan_mask_numerical(_X[:, -1]))
        assert all(nan_mask_numerical(_X[:, -2]))

        # conftest _kwargs 'keep'=='first'
        _kwargs['equal_nan'] = _equal_nan
        TRFM_X = IM(**_kwargs).fit_transform(_X)

        if _equal_nan:
            # last 3 columns should drop, should have 1 column, not np.nan
            assert TRFM_X.shape[1] == 1
            assert np.array_equal(TRFM_X[:, 0], _X[:, 0])
            assert not any(nan_mask_numerical(TRFM_X[:, -1]))
        elif not _equal_nan:
            # only 2nd column should drop, should have 3 columns
            assert TRFM_X.shape[1] == 3
            assert np.array_equal(TRFM_X[:, 0], _X[:, 0])
            assert all(nan_mask_numerical(TRFM_X[:, 1]))
            assert all(nan_mask_numerical(TRFM_X[:, 2]))


    @pytest.mark.parametrize('x_format', ('np', 'pd', 'pl', 'coo_array'))
    @pytest.mark.parametrize('keep',
        ('first', 'last', 'random', 'none', 'int', 'string', 'callable', 'dict')
    )
    @pytest.mark.parametrize('same_or_diff', ('_same', '_diff'))
    def test_all_columns_the_same_or_different(
        self, _X_factory, _kwargs, _columns, _shape, _constants, same_or_diff,
        keep, x_format
    ):

        # '_same' also tests when scipy sparse is all zeros

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --
        if keep == 'string' and x_format not in ['pd', 'pl']:
            pytest.skip(reason=f"cant use str keep when not df")
        # END skip impossible conditions -- -- -- -- -- -- -- -- -- -- --

        # set init params ** * ** * ** * ** * ** * ** * ** * ** * ** *
        _wip_constants = deepcopy(_constants)

        if _kwargs['equal_nan'] is False:
            _wip_constants = {
                k: v for k, v in _wip_constants.items() if str(v) != 'nan'
            }

        keep = {
            'string': _columns[list(_wip_constants.keys())[0]], 'dict': {'Bias': np.e},
            'callable': lambda x: list(_wip_constants.keys())[0],
            'int': list(_wip_constants.keys())[0]
        }.get(keep, keep)   # if keep not in dict, keep does not change

        _kwargs['keep'] = keep
        # END set init params ** * ** * ** * ** * ** * ** * ** * ** * **

        TestCls = IM(**_kwargs)

        # BUILD X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # set the constant columns for X_factory
        # if '_same', make all the columns the same constant
        _value = _wip_constants[list(_wip_constants.keys())[0]]
        if same_or_diff == '_same':
            _dupl = [list(range(_shape[1]))]
            _wip_constants = {i: _value for i in range(_shape[1])}
        else:
            _dupl = None
            # _wip_constants stays the same

        TEST_X = _X_factory(
            _dupl=_dupl, _has_nan=False, _format=x_format, _dtype='flt',
            _columns=_columns if x_format in ['pd', 'pl'] else None,
            _constants=_wip_constants, _noise=0, _zeros=None, _shape=_shape
        )
        # END BUILD X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # after making X, finalize _wip_constants to use it as referee
        if _kwargs['equal_nan'] is False and str(_value) == 'nan':
            _wip_constants = {}

        if keep == 'none' and same_or_diff == '_same':
            with pytest.raises(ValueError):
                # raises if all columns will be deleted
                TestCls.fit_transform(TEST_X)
            pytest.skip(reason=f"cant do anymore tests without fit")
        else:
            TRFM_X = TestCls.fit_transform(TEST_X)

        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert TestCls.constant_columns_ == _wip_constants, \
            f"TestCls.constant_columns_ != _wip_constants"

        if keep != 'none' and not isinstance(keep, dict):
            if same_or_diff == '_same':
                # if all are constant, all but 1 column is deleted
                assert TRFM_X.shape[1] == 1
            elif same_or_diff == '_diff':
                assert TRFM_X.shape[1] == _shape[1] - len(_wip_constants) + 1
        elif isinstance(keep, dict):
            if same_or_diff == '_same':
                # if all are constant, all original are deleted, append new
                assert TRFM_X.shape[1] == 1
            elif same_or_diff == '_diff':
                assert TRFM_X.shape[1] == _shape[1] - len(_wip_constants) + 1
        elif keep == 'none':
            if same_or_diff == '_same':
                raise Exception(f"shouldnt be in here")
                # this was tested above under a pytest.raises. should raise
                # because all columns will be removed.
            elif same_or_diff == '_diff':
                assert TRFM_X.shape[1] == _shape[1] - len(_wip_constants)
        else:
            raise Exception(f'algorithm failure')


    @pytest.mark.parametrize('_dtype', ('str', 'obj'))
    def test_transform_floats_as_str_dtypes(
        self, _X_factory, _dtype, _shape, _constants
    ):

        # make an array of floats....
        _wip_X = _X_factory(
            _dupl=None, _has_nan=False, _format='np', _dtype='flt',
            _columns=None, _constants=_constants, _zeros=0, _shape=_shape
        )

        # set dtype
        _wip_X = _wip_X.astype('<U20' if _dtype == 'str' else object)

        _IM = IM(keep='last', equal_nan=True, rtol=1e-5, atol=1e-8)

        out = _IM.fit_transform(_wip_X)

        assert isinstance(out, np.ndarray)

        _ref_column_mask = np.ones((_shape[1],)).astype(bool)
        _ref_column_mask[[i in _constants for i in range(_shape[1])]] = False
        # keep == 'last'!
        _ref_column_mask[sorted(list(_constants))[-1]] = True

        assert np.array_equal(_IM.column_mask_, _ref_column_mask)


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestFitTransform:


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _constants, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=_constants, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = IM(**_kwargs)
        TestCls.set_output(transform=output_type)

        TRFM_X = TestCls.fit_transform(_X_wip)

        # if output_type is None, should return same type as given
        # if  'default', should return np array no matter what given
        # if  'pandas' or 'polars', should return pd/pl df no matter what given
        _output_type_dict = {
            None: type(_X_wip), 'default': np.ndarray, 'polars': pl.DataFrame,
            'pandas': pd.DataFrame
        }
        assert isinstance(TRFM_X, _output_type_dict[output_type]), \
            (f"X input type {type(_X_wip)}, X output type {type(TRFM_X)}, "
             f"expected output_type {output_type}")


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestInverseTransform:


    # - output is C contiguous
    # - num columns must equal num columns in column_mask_


    @pytest.mark.parametrize('_copy',
        (-1, 0, 1, 3.14, True, False, None, 'junk', [0, 1], (1,), {'a': 1}, min)
    )
    def test_copy_validation(self, X_np, _shape, _kwargs, _copy):

        _IM = IM(**_kwargs)
        _IM.fit(X_np)

        if isinstance(_copy, (bool, type(None))):
            _IM.inverse_transform(X_np[:, _IM.column_mask_], copy=_copy)
        else:
            with pytest.raises(TypeError):
                _IM.inverse_transform(X_np[:, _IM.column_mask_], copy=_copy)


    @pytest.mark.parametrize('_format',('np', 'pd', 'pl', 'dok_array'))
    @pytest.mark.parametrize('_keep', ('first', {'Intercept': 1}))
    @pytest.mark.parametrize('_copy', (True, False))
    def test_accuracy(
        self, _X_factory, _columns, _kwargs, _shape, _constants, _format,
        _keep, _copy
    ):

        # CDT.inverse_transform:
        # turns ss into csc, captures og ss dtype
        # passes X and keep into _remove_intercept, removes any intercept
        # that was appended if keep was a dict
        # runs the core _inverse_transform function
        # scipy sparse are changed back to og sparse container

        # we know _remove_intercept and _inverse_transform are accurate
        # from their own tests.
        # just confirm the CDT class inverse_transform method works
        # correctly, and returns containers as given with correct shape.

        # set_output does not control the output container for inverse_transform
        # the output container is always the same as passed

        # build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format=_format,
            _dtype='flt',
            _columns=_columns,
            _constants=_constants,
            _zeros=0,
            _shape=_shape
        )
        # END build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


        _kwargs['keep'] = _keep
        _IM = IM(**_kwargs)
        _IM.fit(_X_wip)
        TRFM_X = _IM.transform(_X_wip, copy=True)
        assert isinstance(TRFM_X, type(_X_wip))
        # confirm that transform actually removed some columns, and
        # inverse_transform will actually do something
        assert TRFM_X.shape[1] < _shape[1]

        # inverse transform v v v v v v v v v v v v v v v
        INV_TRFM_X = _IM.inverse_transform(X=TRFM_X, copy=_copy)
        # inverse transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        # output container is same as passed
        assert isinstance(INV_TRFM_X, type(_X_wip))

        # verify dimension of output
        assert INV_TRFM_X.shape[0] == TRFM_X.shape[0], \
            f"rows in output of inverse_transform() do not match input rows"
        assert INV_TRFM_X.shape[1] == _IM.n_features_in_, \
            (f"num features in output of inverse_transform() do not match "
             f"originally fitted columns")


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_array'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _constants, _format
    ):

        # set_output does not control the output container for inverse_transform
        # the output container is always the same as passed

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=_constants, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()

        # verify _X_wip does not mutate in inverse_transform
        _IM = IM(**_kwargs).fit(_X_wip)
        TRFM_X = _IM.transform(_X_wip, copy=True)
        assert isinstance(TRFM_X, type(_X_wip))
        assert TRFM_X.shape[1] < _X_wip.shape[1]
        INV_TRFM_X = _IM.inverse_transform(TRFM_X, copy=True)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip_before, np.ndarray):
            assert np.array_equal(_X_wip_before, _X_wip, equal_nan=True)
            # if numpy output, is C order
            _X_wip.flags['C_CONTIGUOUS'] is True
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip_before, 'columns'):
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(
                _X_wip.toarray(), _X_wip_before.toarray(), equal_nan=True
            )
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('_diff', ('more', 'less', 'same'))
    def test_rejects_bad_num_features(
        self, _X_factory, _shape, X_np, _kwargs, _master_columns, _format, _diff
    ):

        # num columns must equal num columns in column_mask_

        # ** ** ** **
        # THERE CANNOT BE "BAD NUM FEATURES" FOR fit & fit_transform
        # THE MECHANISM FOR inverse_transform IS DIFFERENT FROM partial_fit & transform
        # ** ** ** **

        # RAISE ValueError WHEN COLUMNS DO NOT EQUAL NUMBER OF
        # COLUMNS RETAINED BY column_mask_

        _IM = IM(**_kwargs)
        _IM.fit(X_np)
        TRFM_X = _IM.transform(X_np)
        assert TRFM_X.shape[1] < X_np.shape[1]

        # rig TRFM_X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        _new_shape_dict = {
            'same': TRFM_X.shape,
            'less': (TRFM_X.shape[0], TRFM_X.shape[1] - 1),
            'more': (TRFM_X.shape[0], 2 * TRFM_X.shape[1])
        }
        _columns_dict = {
            'same': _master_columns.copy()[:TRFM_X.shape[1]],
            'less': _master_columns.copy()[:TRFM_X.shape[1]-1],
            'more': _master_columns.copy()[:2 * TRFM_X.shape[1]]
        }

        _rigged_trfm_X = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format=_format,
            _dtype='flt',
            _columns=_columns_dict[_diff],
            _constants=None,
            _zeros=0,
            _shape=_new_shape_dict[_diff]
        )
        # END rig TRFM_X ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # Test the inverse_transform operation ** ** ** ** ** ** **
        if _diff == 'same':
            _IM.inverse_transform(_rigged_trfm_X)
        else:
            with pytest.raises(ValueError):
                _IM.inverse_transform(_rigged_trfm_X)
        # END Test the inverse_transform operation ** ** ** ** ** ** **






