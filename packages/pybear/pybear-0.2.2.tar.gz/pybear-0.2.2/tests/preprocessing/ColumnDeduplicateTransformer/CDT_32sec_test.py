# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import itertools

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.preprocessing._ColumnDeduplicator.ColumnDeduplicator import \
    ColumnDeduplicator as CDT

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
        (-1,0,1, np.pi, True, False, None, [1,2], {1,2}, {'a':1}, lambda x: x)
    )
    def test_junk_keep(self, X_np, _kwargs, junk_keep):

        _kwargs['keep'] = junk_keep

        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_keep', ('trash', 'garbage', 'waste'))
    def test_bad_keep(self, X_np, _kwargs, bad_keep):

        _kwargs['keep'] = bad_keep

        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_keep', ('first', 'last', 'random'))
    def test_good_keep(self, X_np, _kwargs, good_keep):

        _kwargs['keep'] = good_keep
        CDT(**_kwargs).fit_transform(X_np)
    # END keep ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # equal_nan ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_junk',
        (-1, 0, 1, np.pi, None, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_non_bool_equal_nan(self, X_np, _kwargs, _junk):

        _kwargs['equal_nan'] = _junk

        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_equal_nan', [True, False])
    def test_equal_nan_accepts_bool(self, X_np, _kwargs, _equal_nan):

        _kwargs['equal_nan'] = _equal_nan

        CDT(**_kwargs).fit_transform(X_np)
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
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_bad', (-np.pi, -2, -1, True, False))
    def test_bad_rtol_atol(self, X_np, _kwargs, _param, _bad):

        _kwargs[_param] = _bad

        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_good', (1e-5, 1e-6, 1e-1, 1_000_000))
    def test_good_rtol_atol(self, X_np, _kwargs, _param, _good):

        _kwargs[_param] = _good

        CDT(**_kwargs).fit_transform(X_np)
    # END rtol & atol ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # do_not_drop ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_dnd',
        (-1, 0, 1, np.pi, True, False, 'trash', {'a': 1}, lambda x: x, min)
    )
    def test_rejects_not_list_like_or_none(self, _kwargs, X_np, junk_dnd):

        _kwargs['do_not_drop'] = junk_dnd
        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_dnd',
        ([True, min, 3.14], [min, max, float], [2.718, 3.141, 8.834])
    )
    def test_rejects_bad_list(self, X_np, _kwargs, bad_dnd):

        _kwargs['do_not_drop'] = bad_dnd
        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_dnd_str_handing(
        self, _X_factory, _shape, _kwargs, _columns, _format
    ):

        assert _format in ('np', 'pd', 'pl')

        _X_wip = _X_factory(
            _format=_format,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _shape=_shape
        )

        _kwargs['conflict'] = 'ignore'

        _kwargs['do_not_drop'] = [v for i, v in enumerate(_columns) if i % 2 == 0]
        if _format == 'np':
            # rejects str when no header
            with pytest.raises(TypeError):
                CDT(**_kwargs).fit_transform(_X_wip)
        elif _format in ['pd', 'pl']:
            # accepts good str always
            _kwargs['do_not_drop'] = [v for i, v in enumerate(_columns) if i % 2 == 0]
            CDT(**_kwargs).fit_transform(_X_wip)

        _kwargs['do_not_drop'] = ['a', 'b']
        if _format == 'np':
            # rejects str when no header
            with pytest.raises(TypeError):
                CDT(**_kwargs).fit_transform(_X_wip)
        elif _format in ['pd', 'pl']:
            # rejects bad str when header
            with pytest.raises(ValueError):
                CDT(**_kwargs).fit_transform(_X_wip)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_dnd_int_none_handling(
        self, _X_factory, _shape, _kwargs, _columns, _format
    ):

        assert _format in ('np', 'pd', 'pl')

        _X_wip = _X_factory(
            _format=_format,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _shape=_shape
        )

        # accepts good int always
        _kwargs['do_not_drop'] = [0, 1]
        CDT(**_kwargs).fit_transform(_X_wip)

        # rejects bad int always - 1
        _kwargs['do_not_drop'] = [-1, 1]
        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(_X_wip)

        # rejects bad int always - 2
        _kwargs['do_not_drop'] = [0, _X_wip.shape[1]]
        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(_X_wip)

        # accepts None always
        _kwargs['do_not_drop'] = None
        CDT(**_kwargs).fit_transform(_X_wip)
    # END do_not_drop ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # conflict  ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_conflict',
        (-1, 0, np.pi, True, None, [1, 2], {1, 2}, {'a': 1}, lambda x: x, min)
    )
    def test_junk_conflict(self, X_np, _kwargs, junk_conflict):

        _kwargs['conflict'] = junk_conflict

        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_conflict', ('trash', 'garbage', 'waste'))
    def test_bad_conflict(self, X_np, _kwargs, bad_conflict):

        _kwargs['conflict'] = bad_conflict

        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_conflict', ('raise', 'ignore'))
    def test_good_conflict(self, X_np, _kwargs, good_conflict):

        _kwargs['conflict'] = good_conflict

        CDT(**_kwargs).fit_transform(X_np)
    # END conflict ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_n_jobs',
        (-2.7, 2.7, True, False, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_junk_n_jobs(self, X_np, _kwargs, junk_n_jobs):

        _kwargs['n_jobs'] = junk_n_jobs

        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_n_jobs', (-3, -2, 0))
    def test_bad_n_jobs(self, X_np, _kwargs, bad_n_jobs):

        _kwargs['n_jobs'] = bad_n_jobs

        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_n_jobs', (-1, 1, 2, None))
    def test_good_n_jobs(self, X_np, _kwargs, good_n_jobs):

        _kwargs['n_jobs'] = good_n_jobs

        CDT(**_kwargs).fit_transform(X_np)

    # END n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # job_size ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('junk_job_size',
        (-2.7, 2.7, True, False, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_junk_job_size(self, X_np, _kwargs, junk_job_size):

        _kwargs['job_size'] = junk_job_size

        with pytest.raises(TypeError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_job_size', (-1, 0))
    def test_bad_job_size(self, X_np, _kwargs, bad_job_size):

        _kwargs['job_size'] = bad_job_size

        with pytest.raises(ValueError):
            CDT(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_job_size', (2, 20))
    def test_good_job_size(self, X_np, _kwargs, good_job_size):

        _kwargs['job_size'] = good_job_size

        CDT(**_kwargs).fit_transform(X_np)

    # END job_size ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

# END test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestX:

    # - accepts ndarray, pd.DataFrame, pl.DataFrame, and all ss
    # - cannot be None
    # - must be 2D
    # - must have at least 2 columns
    # - must have at least 1 sample
    # - allows nan
    # - partial_fit/transform num columns must equal num columns seen during first fit


    # CONTAINERS #######################################################
    @pytest.mark.parametrize('_junk_X',
        (-1, 0, 1, 3.14, None, 'junk', [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_X(self, _kwargs, X_np, _junk_X):

        TestCls = CDT(**_kwargs)

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

        TestCls = CDT(**_kwargs)

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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_array'))
    def test_good_X_container(
        self, _X_factory, _columns, _shape, _kwargs, _dupls, _format
    ):

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )


        _CDT = CDT(**_kwargs)

        _CDT.partial_fit(_X_wip)

        _CDT.fit(_X_wip)

        _CDT.fit_transform(_X_wip)

        TRFM_X = _CDT.transform(_X_wip)

        _CDT.inverse_transform(TRFM_X)

    # END CONTAINERS ###################################################


    # SHAPE ############################################################
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_rejects_1D(self, X_np, _kwargs, _format):

        # validation order is
        # 1) check_fitted (for transform & inv_transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits, transform & inv_transform, 1D will always catch first

        _CDT = CDT(**_kwargs)

        if _format == 'np':
            _X_wip = X_np[:, 0]
        elif _format == 'pd':
            _X_wip = pd.Series(X_np[:, 0])
        elif _format == 'pl':
            _X_wip = pl.Series(X_np[:, 0])
        else:
            raise Exception

        with pytest.raises(ValueError):
            _CDT.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _CDT.fit(_X_wip)

        with pytest.raises(ValueError):
            _CDT.fit_transform(_X_wip)

        _CDT.fit(X_np)

        with pytest.raises(ValueError) as e:
            _CDT.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            _CDT.inverse_transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_num_cols', (0, 1, 2))
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dia_matrix'))
    def test_X_2D_number_of_columns(
        self, X_np, _kwargs, _columns, _format, _num_cols
    ):

        # validation order is
        # 1) check_fitted (for transform & inv_transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits, transform & inv_transform, validate_data will catch
        # for inverse_transform, min is 1 column, everything else is 2

        _base_X = X_np[:, :_num_cols]
        if _format == 'np':
            _X_wip = _base_X
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_base_X, columns=_columns[:_num_cols])
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_base_X, schema=list(_columns[:_num_cols]))
        elif _format == 'dia_matrix':
            _X_wip = ss.dia_matrix(_base_X)
        else:
            raise Exception

        assert len(_X_wip.shape) == 2
        assert _X_wip.shape[1] == _num_cols

        _CDT = CDT(**_kwargs)

        # inverse_transform can take 1, everything else needs >= 2
        if _num_cols in [0, 1]:
            with pytest.raises(ValueError):
                _CDT.partial_fit(_X_wip)
            with pytest.raises(ValueError):
                _CDT.fit(_X_wip)
            with pytest.raises(ValueError):
                _CDT.fit_transform(_X_wip)
            _CDT.fit(X_np)
            with pytest.raises(ValueError) as e:
                _CDT.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            if _num_cols == 0:
                _CDT.fit(X_np)
                with pytest.raises(ValueError) as e:
                    _CDT.inverse_transform(_X_wip)
                assert not isinstance(e.value, NotFittedError)
            elif _num_cols == 1:
                try:
                    # when type is ndarray it wont allow create like this
                    # kick out and just hstack since _base_X is np
                    _new_X_wip = type(_X_wip)(np.hstack((_base_X, _base_X)))
                except:
                    _new_X_wip = np.hstack((_base_X, _base_X))
                _CDT.fit(_new_X_wip)
                TRFM_X = _CDT.transform(_new_X_wip)
                _CDT.inverse_transform(TRFM_X)
        else:
            _CDT.partial_fit(_X_wip)
            _CDT.fit(_X_wip)
            _CDT.fit_transform(_X_wip)
            TRFM_X = _CDT.transform(_X_wip)
            _CDT.inverse_transform(TRFM_X)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_array'))
    def test_rejects_no_samples(self, _shape, _kwargs, X_np, _format):

        _CDT = CDT(**_kwargs)

        _X_base = np.empty((0, _shape[1]), dtype=np.float64)

        if _format == 'np':
            _X_wip = _X_base
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_X_base)
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_X_base)
        elif _format == 'coo_array':
            _X_wip = ss.coo_array(_X_base)
        else:
            raise Exception


        with pytest.raises(ValueError):
            _CDT.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _CDT.fit(_X_wip)

        with pytest.raises(ValueError):
            _CDT.fit_transform(_X_wip)

        _CDT.fit(X_np)

        with pytest.raises(ValueError) as e:
            _CDT.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)

        with pytest.raises(ValueError) as e:
            _CDT.inverse_transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('_diff', ('more', 'less', 'same'))
    def test_rejects_bad_num_features(
        self, _X_factory, _shape, _dupls, _kwargs, _columns, X_np,
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
        _new_dupls_dict = {
            'same': _dupls,
            'less': [[0,_shape[1]-2], [1, _shape[1]-2]],
            'more': _dupls
        }

        _X_wip = _X_factory(
            _dupl=_new_dupls_dict[_diff],
            _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns_dict[_diff],
            _constants=None, _zeros=0,
            _shape=_new_shape_dict[_diff]
        )

        _CDT = CDT(**_kwargs)
        _CDT.fit(X_np)

        if _diff == 'same':
            _CDT.partial_fit(_X_wip)
            _CDT.transform(_X_wip)
        else:
            with pytest.raises(ValueError) as e:
                _CDT.partial_fit(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            with pytest.raises(ValueError) as e:
                _CDT.transform(_X_wip)
            assert not isinstance(e.value, NotFittedError)

    # END SHAPE #############################################################


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

        TestCls = CDT(**_kwargs)

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
        CDT(**_kwargs).partial_fit(X_np, _y)
        CDT(**_kwargs).fit(X_np, _y)


    def test_conditional_access_to_partial_fit_and_fit(self, X_np, _kwargs):

        TestCls = CDT(**_kwargs)

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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'bsr_array'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _dupls, _format
    ):

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        # verify _X_wip does not mutate in partial_fit()
        _CDT = CDT(**_kwargs).partial_fit(_X_wip)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip, np.ndarray):
            # if numpy output, is C order
            assert _X_wip.flags['C_CONTIGUOUS'] is True
            assert np.array_equal(_X_wip_before, _X_wip)
            assert _X_wip.dtype == _X_wip_before.dtype
        elif hasattr(_X_wip, 'columns'):  # DATAFRAMES
            assert _X_wip.equals(_X_wip_before)
            assert np.array_equal(_X_wip.dtypes, _X_wip_before.dtypes)
        elif hasattr(_X_wip_before, 'toarray'):
            assert np.array_equal(_X_wip.toarray(), _X_wip_before.toarray())
            assert _X_wip.dtype == _X_wip_before.dtype
        else:
            raise Exception


    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_many_partial_fits_equal_one_big_fit(
        self, _kwargs, _shape, X_np, _keep
    ):

        # **** **** **** **** **** **** **** **** **** **** **** **** ****
        # THIS TEST IS CRITICAL FOR VERIFYING THAT transform PULLS THE
        # SAME COLUMN INDICES FOR ALL CALLS TO transform() WHEN
        # keep=='random'
        # **** **** **** **** **** **** **** **** **** **** **** **** ****

         # X_np has no nans

        _kwargs['keep'] = _keep

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST THAT ONE-SHOT partial_fit/transform == ONE-SHOT fit/transform
        OneShotPartialFitTestCls = CDT(**_kwargs).partial_fit(X_np)

        OneShotFullFitTestCls = CDT(**_kwargs).fit(X_np)

        # duplicates are equal -- -- -- --
        _ = OneShotPartialFitTestCls.duplicates_
        __ = OneShotFullFitTestCls.duplicates_
        assert len(_) == len(__)
        for idx in range(len(_)):
            assert np.array_equal(_[idx], __[idx])
        del _, __
        # END duplicates are equal -- -- -- --

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
            assert np.array_equal(
                ONE_SHOT_PARTIAL_FIT_TRFM_X,
                ONE_SHOT_FULL_FIT_TRFM_X
            ), f"one shot partial fit trfm X != one shot full fit trfm X"

        del OneShotPartialFitTestCls, OneShotFullFitTestCls
        del ONE_SHOT_PARTIAL_FIT_TRFM_X, ONE_SHOT_FULL_FIT_TRFM_X

        # END TEST THAT ONE-SHOT partial_fit/transform==ONE-SHOT fit/transform
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST PARTIAL FIT DUPLS ARE THE SAME WHEN FULL DATA
        # IS partial_fit() 2X
        SingleFitTestClass = CDT(**_kwargs).fit(X_np)
        _ = SingleFitTestClass.duplicates_

        DoublePartialFitTestClass = CDT(**_kwargs)
        DoublePartialFitTestClass.partial_fit(X_np)
        __ = DoublePartialFitTestClass.duplicates_
        DoublePartialFitTestClass.partial_fit(X_np)
        ___ = DoublePartialFitTestClass.duplicates_

        assert len(_) == len(__) == len(___)
        for idx in range(len(_)):
            assert np.array_equal(_[idx], __[idx])
            assert np.array_equal(_[idx], ___[idx])

        del _, __, ___, SingleFitTestClass, DoublePartialFitTestClass

        # END PARTIAL FIT DUPLS ARE THE SAME WHEN FULL DATA IS partial_fit() 2X
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

        PartialFitTestCls = CDT(**_kwargs)
        OneShotFitTransformTestCls = CDT(**_kwargs)

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
    def test_dupl_accuracy_over_many_partial_fits(
        self, _kwargs, _X_factory, _dtype, _has_nan
    ):

        # verify correct progression of reported duplicates as partial
        # fits are done. rig a set of arrays that have progressively
        # decreasing duplicates

        _chunk_shape = (50, 20)  # must have at least 10 columns for dupls to work

        _start_dupl = [[0, 7], [2, 4, _chunk_shape[1] - 1], [3, 5, _chunk_shape[1] - 2]]

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['equal_nan'] = True

        PartialFitTestCls = CDT(**_new_kwargs)

        # build a pool of non-dupls to fill the dupls in X along the way
        # build a starting data object for first partial fit, using full dupls
        # build a y vector
        # do a verification partial_fit, assert reported dupls for original X
        # make a holder for all the different _wip_Xs, to do one big fit at the end
        # for however many times u want to do this:
        #   randomly replace one of the dupls with non-dupl column
        #   partial_fit
        #   assert reported dupls - should be one less (the randomly chosen)
        # at the very end, stack all the _wip_Xs, do one big fit, verify dupls

        _pool_X = _X_factory(
            _dupl=None,  # <============
            _has_nan=_has_nan, _format='np', _dtype=_dtype,
            _columns=None, _zeros=None, _shape=_chunk_shape
        )

        _wip_X = _X_factory(
            _dupl=_start_dupl,  # <============
            _has_nan=_has_nan, _format='np', _dtype=_dtype,
            _columns=None, _zeros=None, _shape=_chunk_shape
        )

        y_np = np.random.randint(0, 2, (_chunk_shape[0]))

        # verify IM sees the dupl columns correctly ** * ** * ** *
        # this also sets the original dupl columns in PartialFitTestCls
        _dupl_columns = \
            PartialFitTestCls.partial_fit(_wip_X, y_np).duplicates_
        assert len(_dupl_columns) == len(_start_dupl)
        for idx in range(len(_start_dupl)):
            assert np.array_equal(
                _dupl_columns[idx],
                _start_dupl[idx]
            )
        del _dupl_columns
        # END verify IM sees the dupl columns correctly ** * ** * ** *

        # create a holder for the the original dupl column idxs
        _dupl_pool = list(itertools.chain(*_start_dupl))

        X_HOLDER = []
        X_HOLDER.append(_wip_X)

        # take out only half of the dupls (arbitrary) v^v^v^v^v^v^v^v^v^
        for trial in range(len(_dupl_pool)//2):

            random_dupl = np.random.choice(_dupl_pool, 1, replace=False)[0]

            # take the random dupl of out _start_dupl and _dupl_pool,
            # and take a column out of the X pool to patch the dupl in _wip_X
            for _idx, _set in enumerate(reversed(_start_dupl)):
                try:
                    _start_dupl[_idx].remove(random_dupl)
                    if len(_start_dupl[_idx]) == 1:
                        # gotta take that dangling dupl out of dupl pool!
                        _dupl_pool.remove(_start_dupl[_idx][0])
                        # and out of _start_dupl by deleting the whole set
                        del _start_dupl[_idx]
                    break
                except:
                    continue
            else:
                raise Exception(f"could not find dupl idx in _start_dupl")

            _dupl_pool.remove(random_dupl)

            # now that random_dupl has been taken out of _start_dupl,
            # it may have been in the first position of a set which would
            # change the sorting of the sets. so re-sort the sets
            _start_dupl = sorted(_start_dupl, key=lambda x: x[0])

            # column from X is a doppleganger, column from pool shouldnt be
            # but verify anyway ** ** ** ** ** ** ** ** ** ** ** ** **
            _from_X = _wip_X[:, random_dupl]
            _from_pool = _pool_X[:, random_dupl]
            assert not np.array_equal(
                _from_X[np.logical_not(nan_mask(_from_X))],
                _from_pool[np.logical_not(nan_mask(_from_pool))]
            )
            del _from_X, _from_pool
            # END verify ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

            _wip_X[:, random_dupl] = _pool_X[:, random_dupl]

            X_HOLDER.append(_wip_X)

            # fit PartialFitTestCls on the new _wip_X
            # verify correctly reported dupls after this partial_fit
            _dupl_columns = \
                PartialFitTestCls.partial_fit(_wip_X, y_np).duplicates_
            assert len(_dupl_columns) == len(_start_dupl)
            for idx in range(len(_start_dupl)):
                assert np.array_equal(_dupl_columns[idx], _start_dupl[idx]), \
                    f"{_dupl_columns=}, {_start_dupl=}"

        # END take out only half of the dupls (arbitrary) v^v^v^v^v^v^v^

        # we now have full X_HOLDER, which holds _wip_Xs with progressively
        # fewer duplicate columns
        # and PartialFitTestCls, which was fit sequentially on the _wip_Xs

        _partial_fit_dupl_columns = PartialFitTestCls.duplicates_
        # do a one-shot fit, compare results
        # stack all the _wip_Xs
        OneShotFitTestCls = CDT(**_new_kwargs).fit(np.vstack(X_HOLDER), y_np)
        _one_shot_dupl_columns = OneShotFitTestCls.duplicates_
        # remember that _start_dupls has dupl idxs popped out of it
        # as non-dupl columns were put into _wip_X
        assert len(_one_shot_dupl_columns) == len(_start_dupl)
        assert len(_partial_fit_dupl_columns) == len(_start_dupl)
        for idx, group in enumerate(_start_dupl):
            assert np.array_equal(_one_shot_dupl_columns[idx], group)
            assert np.array_equal(_partial_fit_dupl_columns[idx], group)

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

        _CDT = CDT(**_kwargs)
        _CDT.fit(X_np)

        if isinstance(_copy, (bool, type(None))):
            _CDT.transform(X_np, copy=_copy)
        else:
            with pytest.raises(TypeError):
                _CDT.transform(X_np, copy=_copy)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dia_array'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _dupls, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = CDT(**_kwargs)
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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_matrix'))
    def test_X_is_not_mutated(
            self, _X_factory, _columns, _shape, _kwargs, _dupls, _format
    ):

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        _CDT = CDT(**_kwargs).fit(_X_wip)

        # verify _X_wip does not mutate in transform() with copy=True
        TRFM_X = _CDT.transform(_X_wip, copy=True)


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
    @pytest.mark.parametrize('dupls', (None, [[0, 2, 9]], [[0, 6], [1, 8]]))
    @pytest.mark.parametrize('keep', ('first', 'last', 'random'))
    @pytest.mark.parametrize('do_not_drop', (None, [0, 5], 'pd')) #, 'pl'))
    @pytest.mark.parametrize('conflict', ('raise', 'ignore'))
    @pytest.mark.parametrize('equal_nan', (True, False))
    def test_accuracy(
        self, _X_factory, _kwargs, X_format, X_dtype, has_nan,
        dupls, keep, do_not_drop, conflict, _columns, equal_nan, _shape
    ):

        # validate the test parameters -------------
        assert keep in ['first', 'last', 'random']
        assert isinstance(do_not_drop, (list, type(None), str))
        assert conflict in ['raise', 'ignore']
        assert isinstance(equal_nan, bool)
        # END validate the test parameters -------------

        # skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if X_dtype not in ['flt', 'int'] and X_format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take str")

        if X_format == 'np' and X_dtype == 'int' and has_nan:
            pytest.skip(reason=f"numpy int dtype cant take 'nan'")

        if do_not_drop in ['pd', 'pl']:
            if X_format not in ['pd', 'pl']:
                pytest.skip(
                    reason=f"impossible condition, str dnd and format is not pd"
                )
        # END skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _X_wip = _X_factory(
            _dupl=dupls,
            _has_nan=has_nan,
            _format=X_format,
            _dtype=X_dtype,
            _columns=_columns,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )
        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # set do_not_drop as list of strings for dfs (vs None or list of ints)
        if do_not_drop in ['pd', 'pl']:
            do_not_drop = list(map(str, [_columns[0], _columns[3], _columns[7]]))
        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # set _kwargs
        _kwargs['keep'] = keep
        _kwargs['do_not_drop'] = do_not_drop
        _kwargs['conflict'] = conflict
        _kwargs['rtol'] = 1e-5
        _kwargs['atol'] = 1e-8
        _kwargs['equal_nan'] = equal_nan

        TestCls = CDT(**_kwargs)

        # get exp_dupls & manage error conditions ----------------------
        exp_dupls = deepcopy(dupls or [])
        if has_nan and not equal_nan:
            exp_dupls = []

        _conflict_condition = (dupls is not None) and (do_not_drop is not None) \
                            and (keep == 'last') and not (has_nan and not equal_nan)
        # only because all non-None dupls and non-None do_not_drop
        # have zeros in them
        # END get exp_dupls & manage error conditions ------------------

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        if _conflict_condition and conflict == 'raise':
            with pytest.raises(ValueError):
                TestCls.fit_transform(_X_wip)
            pytest.skip(reason=f"dont do remaining tests")
        else:
            TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # returned format is same as given format
        assert isinstance(TRFM_X, type(_X_wip))

        # if numpy output, is C order
        if isinstance(TRFM_X, np.ndarray):
            assert TRFM_X.flags['C_CONTIGUOUS'] is True

        # returned dtypes are same as given dtypes
        if isinstance(TRFM_X, (pd.DataFrame, pl.DataFrame)):
            assert np.array_equal(
                np.array(list(TRFM_X.dtypes)),
                np.array(list(_X_wip.dtypes))[TestCls.column_mask_]
            )
        else:
            assert TRFM_X.dtype == _X_wip.dtype

        # assure all columns that werent duplicates are in the output
        __all_dupls = list(itertools.chain(*deepcopy(exp_dupls)))
        for col_idx in range(_shape[1]):
            if col_idx not in __all_dupls:
                assert TestCls.column_mask_[col_idx] is np.True_

        # for retained columns, assert they are equal to themselves in
        # the original data
        _kept_idxs = np.arange(len(TestCls.column_mask_))[TestCls.column_mask_]
        _kept_idxs = list(map(int, _kept_idxs))
        for _new_idx, _kept_idx in enumerate(_kept_idxs, 0):

            if isinstance(_X_wip, np.ndarray):
                _out_col = TRFM_X[:, [_new_idx]]
                _og_col = _X_wip[:, [_kept_idx]]
            elif isinstance(_X_wip, pd.DataFrame):
                _out_col = TRFM_X.iloc[:, [_new_idx]].to_numpy()
                _og_col = _X_wip.iloc[:, [_kept_idx]].to_numpy()
            elif isinstance(_X_wip, pl.DataFrame):
                _out_col = TRFM_X[:, [_new_idx]].to_numpy()
                _og_col = _X_wip[:, [_kept_idx]].to_numpy()
            else:
                _out_col = TRFM_X.tocsc()[:, [_new_idx]].toarray()
                _og_col = _X_wip.tocsc()[:, [_kept_idx]].toarray()

            assert _parallel_column_comparer(
                _out_col,
                _og_col,
                _rtol=1e-5,
                _atol=1e-8,
                _equal_nan=True
            )

        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_one_all_nans(self, _X_factory, _kwargs, _shape, _equal_nan):

        # nans are put in manually later
        _X = _X_factory(
            _dupl=[[0,1]], _has_nan=False, _format='np', _dtype='flt',
            _columns=None, _constants=None, _zeros=None,
            _shape=(_shape[0], 3)    # <====== 3 columns
        )

        # set a column to all nans
        _X[:, -1] = np.nan
        # verify last column is all nans
        assert all(nan_mask_numerical(_X[:, -1]))

        # conftest _kwargs 'keep' == 'first'
        _kwargs['equal_nan'] = _equal_nan
        TRFM_X = CDT(**_kwargs).fit_transform(_X)

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
            _dupl=[[0,1]], _has_nan=False, _format='np', _dtype='flt',
            _columns=None, _zeros=None,
            _shape=(_shape[0], 4)    # <======== 4 columns
        )

        # set last 2 columns to all nans
        _X[:, [-2, -1]] = np.nan
        # verify last columns are all nans
        assert all(nan_mask_numerical(_X[:, -1]))
        assert all(nan_mask_numerical(_X[:, -2]))

        # conftest _kwargs 'keep'=='first'
        _kwargs['equal_nan'] = _equal_nan
        TRFM_X = CDT(**_kwargs).fit_transform(_X)

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


    @pytest.mark.parametrize('x_format', ('np', 'pd', 'pl', 'dok_matrix'))
    @pytest.mark.parametrize('keep', ('first', 'last', 'random'))
    @pytest.mark.parametrize('same_or_diff', ('_same', '_diff'))
    def test_all_columns_the_same_or_different(
        self, _X_factory, _kwargs, _columns, _shape, same_or_diff,
        keep, x_format
    ):

        # set init params ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if same_or_diff == '_same':
            _dupl = [list(range(_shape[1]))]
        elif same_or_diff == '_diff':
            _dupl = None
        # END set init params ** * ** * ** * ** * ** * ** * ** * ** * **

        TestCls = CDT(**_kwargs)

        # BUILD X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        TEST_X = _X_factory(
            _dupl=_dupl, _has_nan=False, _format=x_format, _dtype='flt',
            _columns=_columns if x_format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=0,  _shape=_shape
        )
        # END BUILD X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        TRFM_X = TestCls.fit_transform(TEST_X)

        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if _dupl is not None:
            assert len(TestCls.duplicates_) == len(_dupl)
            assert np.array_equal(list(TestCls.duplicates_[0]), _dupl[0]), \
                f"TestCls.duplicates_ != _dupl"

        if same_or_diff == '_same':
            # if all are duplicates, all but 1 column is deleted
            assert TRFM_X.shape[1] == 1
        elif same_or_diff == '_diff':
            assert TRFM_X.shape[1] == _shape[1]


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestFitTransform:


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _dupls, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = CDT(**_kwargs)
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

        _CDT = CDT(**_kwargs)
        _CDT.fit(X_np)

        if isinstance(_copy, (bool, type(None))):
            _CDT.inverse_transform(X_np[:, _CDT.column_mask_], copy=_copy)
        else:
            with pytest.raises(TypeError):
                _CDT.inverse_transform(X_np[:, _CDT.column_mask_], copy=_copy)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'bsr_matrix'))
    @pytest.mark.parametrize('_copy', (True, False))
    def test_accuracy(
        self, _X_factory, _columns, _kwargs, _shape, _dupls, _format, _copy
    ):

        # CDT.inverse_transform doesnt do much beyond run the core
        # _inverse_transform function, which we know is accurate from its
        # own test. scipy are changed to csc and back to original container.
        # just confirm the CDT class inverse_transform method works
        # correctly, and returns containers as given with correct shape.

        # set_output does not control the output container for inverse_transform
        # the output container is always the same as passed

        # build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        _X_wip = _X_factory(
            _dupl=_dupls,
            _has_nan=False,
            _format=_format,
            _dtype='flt',
            _columns=_columns,
            _constants=None,
            _zeros=0,
            _shape=_shape
        )
        # END build X ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


        _CDT = CDT(**_kwargs)
        _CDT.fit(_X_wip)
        TRFM_X = _CDT.transform(_X_wip, copy=True)
        assert isinstance(TRFM_X, type(_X_wip))
        # confirm that transform actually removed some columns, and
        # inverse_transform will actually do something
        assert TRFM_X.shape[1] < _shape[1]

        # inverse transform v v v v v v v v v v v v v v v
        INV_TRFM_X = _CDT.inverse_transform(X=TRFM_X, copy=_copy)
        # inverse transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        # output container is same as passed
        assert isinstance(INV_TRFM_X, type(_X_wip))

        # verify dimension of output
        assert INV_TRFM_X.shape[0] == TRFM_X.shape[0], \
            f"rows in output of inverse_transform() do not match input rows"
        assert INV_TRFM_X.shape[1] == _CDT.n_features_in_, \
            (f"num features in output of inverse_transform() do not match "
             f"originally fitted columns")


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_matrix'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _dupls, _format
    ):

        # set_output does not control the output container for inverse_transform
        # the output container is always the same as passed

        _X_wip = _X_factory(
            _dupl=_dupls, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()

        # verify _X_wip does not mutate in inverse_transform
        _CDT = CDT(**_kwargs).fit(_X_wip)
        TRFM_X = _CDT.transform(_X_wip, copy=True)
        assert isinstance(TRFM_X, type(_X_wip))
        assert TRFM_X.shape[1] < _X_wip.shape[1]
        INV_TRFM_X = _CDT.inverse_transform(X=TRFM_X, copy=True)


        # ASSERTIONS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        assert isinstance(_X_wip, type(_X_wip_before))
        assert _X_wip.shape == _X_wip_before.shape

        if isinstance(_X_wip_before, np.ndarray):
            assert np.array_equal(_X_wip_before, _X_wip, equal_nan=True)
            # if numpy output, is C order
            assert INV_TRFM_X.flags['C_CONTIGUOUS'] is True
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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_array'))
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

        _CDT = CDT(**_kwargs)
        _CDT.fit(X_np)
        TRFM_X = _CDT.transform(X_np)
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
            _CDT.inverse_transform(_rigged_trfm_X)
        else:
            with pytest.raises(ValueError):
                _CDT.inverse_transform(_rigged_trfm_X)
        # END Test the inverse_transform operation ** ** ** ** ** ** **






