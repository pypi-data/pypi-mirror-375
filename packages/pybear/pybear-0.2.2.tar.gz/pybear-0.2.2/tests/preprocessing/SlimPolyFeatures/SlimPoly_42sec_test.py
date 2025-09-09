# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers
import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.preprocessing import SlimPolyFeatures as SPF

from pybear.base.exceptions import NotFittedError

from pybear.utilities import nan_mask


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
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_keep', ('rubbish', 'trash', 'garbage'))
    def test_bad_keep(self, X_np, _kwargs, bad_keep):

        _kwargs['keep'] = bad_keep

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_keep', ('first', 'last', 'random'))
    def test_good_keep(self, X_np, _columns, _kwargs, good_keep):

        _kwargs['keep'] = good_keep
        SPF(**_kwargs).fit_transform(X_np)
    # END keep ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # equal_nan ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_junk',
        (-1, 0, 1, np.pi, None, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_non_bool_equal_nan(self, X_np, _kwargs, _junk):

        _kwargs['equal_nan'] = _junk

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_equal_nan_accepts_bool(self, X_np, _kwargs, _equal_nan):

        _kwargs['equal_nan'] = _equal_nan

        SPF(**_kwargs).fit_transform(X_np)
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
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_bad', (-np.pi, -2, -1, True, False))
    def test_bad_rtol_atol(self, X_np, _kwargs, _param, _bad):

        _kwargs[_param] = _bad

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('_param', ('rtol', 'atol'))
    @pytest.mark.parametrize('_good', (1e-5, 1e-6, 1e-1, 1_000_000))
    def test_good_rtol_atol(self, X_np, _kwargs, _param, _good):

        _kwargs[_param] = _good

        SPF(**_kwargs).fit_transform(X_np)
    # END rtol & atol ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # degree ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_degree',
        (None, [1,2], {1,2}, (1,2), {'a':1}, lambda x: x)
    )
    def test_junk_degree(self, X_np, _kwargs, junk_degree):

        _kwargs['degree'] = junk_degree

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_degree', (-1, 1, np.pi, True, False))
    def test_bad_degree(self, X_np, _kwargs, bad_degree):

        # degree lower bound of 2 is hard coded, so 1 is bad

        _kwargs['degree'] = bad_degree

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_degree', (2,3))
    def test_good_degree(self, X_np, _columns, _kwargs, good_degree):

        _kwargs['degree'] = good_degree

        SPF(**_kwargs).fit_transform(X_np)
    # END degree ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # min_degree ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_min_degree',
        (None, [1,2], {1,2}, (1,2), {'a':1}, lambda x: x)
    )
    def test_junk_min_degree(self, X_np, _kwargs, junk_min_degree):

        _kwargs['min_degree'] = junk_min_degree

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_min_degree', (-1, 0, np.pi, True, False))
    def test_bad_min_degree(self, X_np, _kwargs, bad_min_degree):

        # min_degree lower bound of 1 is hard coded, so 0 is bad

        _kwargs['min_degree'] = bad_min_degree

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_min_degree', (2,3,4))
    def test_good_min_degree(self, X_np, _kwargs, good_min_degree):

        _kwargs['min_degree'] = good_min_degree
        _kwargs['degree'] = good_min_degree + 1

        SPF(**_kwargs).fit_transform(X_np)
    # END min_degree ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # interaction_only ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_interaction_only',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', (0,1), [1,2], {'a':1}, lambda x: x)
    )
    def test_junk_interaction_only(self, X_np, _kwargs, junk_interaction_only):

        _kwargs['interaction_only'] = junk_interaction_only

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_interaction_only', (True, False))
    def test_good_interaction_only(
        self, X_np, _columns, _kwargs, good_interaction_only
    ):

        _kwargs['interaction_only'] = good_interaction_only

        SPF(**_kwargs).fit_transform(X_np)
    # END interaction_only ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # scan_X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_scan_X',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', (0,1), [1,2], {'a':1}, lambda x: x)
    )
    def test_junk_scan_X(self, X_np, _kwargs, junk_scan_X):

        _kwargs['scan_X'] = junk_scan_X

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_scan_X', (True, False))
    def test_good_scan_X(self, X_np, _columns, _kwargs, good_scan_X):

        _kwargs['scan_X'] = good_scan_X

        SPF(**_kwargs).fit_transform(X_np)
    # END scan_X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # sparse_output ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('junk_sparse_output',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', (0,1), [1,2], {'a':1}, lambda x: x)
    )
    def test_junk_sparse_output(self, X_np, _kwargs, junk_sparse_output):

        _kwargs['sparse_output'] = junk_sparse_output

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_sparse_output', (True, False))
    def test_good_sparse_output(
        self, X_np, _columns, _kwargs, good_sparse_output
    ):

        _kwargs['sparse_output'] = good_sparse_output

        SPF(**_kwargs).fit_transform(X_np)
    # END sparse_output ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # feature_name_combiner ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # can be Literal['as_indices', 'as_feature_names']
    # or Callable[[Sequence[str], tuple[int,...]], str]

    @pytest.mark.parametrize('junk_feature_name_combiner',
        (-2.7, -1, 0, 1, 2.7, True, False, None, (0,1), [1,2], {1,2}, {'a':1})
    )
    def test_junk_feature_name_combiner(
        self, X_np, _kwargs, junk_feature_name_combiner
    ):

        _kwargs['feature_name_combiner'] = junk_feature_name_combiner

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_feature_name_combiner', ('junk', 'trash'))
    def test_bad_feature_name_combiner(
        self, X_np, _kwargs, bad_feature_name_combiner
    ):

        _kwargs['feature_name_combiner'] = bad_feature_name_combiner

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_feature_name_combiner',
        ('as_indices', 'as_feature_names', lambda x, y: str(uuid.uuid4())[:5])
    )
    def test_good_feature_name_combiner(
        self, X_np, _columns, _kwargs, good_feature_name_combiner
    ):

        _kwargs['feature_name_combiner'] = good_feature_name_combiner

        SPF(**_kwargs).fit_transform(X_np)
    # END feature_name_combiner ** * ** * ** * ** * ** * ** * ** * ** *


    # n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_n_jobs',
        (-2.7, 2.7, True, False, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_junk_n_jobs(self, X_np, _kwargs, junk_n_jobs):

        _kwargs['n_jobs'] = junk_n_jobs

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_n_jobs', (-3, -2, 0))
    def test_bad_n_jobs(self, X_np, _kwargs, bad_n_jobs):

        _kwargs['n_jobs'] = bad_n_jobs

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_n_jobs', (-1, 1, 2, None))
    def test_good_n_jobs(self, X_np, _kwargs, good_n_jobs):

        _kwargs['n_jobs'] = good_n_jobs

        SPF(**_kwargs).fit_transform(X_np)

    # END n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # job_size ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('junk_job_size',
        (-2.7, 2.7, True, False, 'trash', [1, 2], {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_junk_job_size(self, X_np, _kwargs, junk_job_size):

        _kwargs['job_size'] = junk_job_size

        with pytest.raises(TypeError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('bad_job_size', (-1, 0))
    def test_bad_job_size(self, X_np, _kwargs, bad_job_size):

        _kwargs['job_size'] = bad_job_size

        with pytest.raises(ValueError):
            SPF(**_kwargs).fit_transform(X_np)


    @pytest.mark.parametrize('good_job_size', (2, 20))
    def test_good_job_size(self, X_np, _kwargs, good_job_size):

        _kwargs['job_size'] = good_job_size

        SPF(**_kwargs).fit_transform(X_np)

    # END job_size ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

# END test input validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestX:

    # - accepts ndarray, pd.DataFrame, pl.DataFrame, and all ss
    # - cannot be None
    # - must be 2D
    # - must have at least 1 or 2 columns, depending on interaction_only
    # - must have at least 1 sample
    # - allows nan
    # - partial_fit/transform num columns must equal num columns seen during first fit


    # CONTAINERS #######################################################
    @pytest.mark.parametrize('_junk_X',
        (-1, 0, 1, 3.14, None, 'junk', [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_X(self, _kwargs, X_np, _junk_X):

        TestCls = SPF(**_kwargs)

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


    @pytest.mark.parametrize('_format', ('py_list', 'py_tuple'))
    def test_rejects_invalid_container(self, X_np, _columns, _kwargs, _format):

        assert _format in ('py_list', 'py_tuple')

        TestCls = SPF(**_kwargs)

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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dok_matrix'))
    def test_good_X_container(
        self, _X_factory, _columns, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )


        _SPF = SPF(**_kwargs)

        _SPF.partial_fit(_X_wip)

        _SPF.fit(_X_wip)

        _SPF.fit_transform(_X_wip)

        _SPF.transform(_X_wip)

    # END CONTAINERS ###################################################


    # SHAPE ############################################################
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    def test_rejects_1D(self, X_np, _kwargs, _format):

        # validation order is
        # 1) check_fitted (for transform & inv_transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits, transform & inv_transform, 1D will always catch first

        _SPF = SPF(**_kwargs)

        if _format == 'np':
            _X_wip = X_np[:, 0]
        elif _format == 'pd':
            _X_wip = pd.Series(X_np[:, 0])
        elif _format == 'pl':
            _X_wip = pl.Series(X_np[:, 0])
        else:
            raise Exception

        with pytest.raises(ValueError):
            _SPF.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _SPF.fit(_X_wip)

        with pytest.raises(ValueError):
            _SPF.transform(_X_wip)

        _SPF.fit(X_np)

        with pytest.raises(ValueError) as e:
            _SPF.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_num_cols', (0, 1, 2))
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_matrix'))
    @pytest.mark.parametrize('_intx_only', (True, False))
    def test_X_2D_number_of_columns(
        self, X_np, _kwargs, _columns, _format, _intx_only, _num_cols
    ):

        # validation order is
        # 1) check_fitted (for transform)
        # 2) base.validate_data, which catches dim & min columns
        # 3) _check_n_features in transform
        # so for the fits & transform, validate_data will catch
        # min columns depends on interaction_only. if True, must be 2+
        # columns; if False, can be 1 column.

        _base_X = X_np[:, :_num_cols]
        if _format == 'np':
            _X_wip = _base_X
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_base_X, columns=_columns[:_num_cols])
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_base_X, schema=list(_columns[:_num_cols]))
        elif _format == 'csc_matrix':
            _X_wip = ss.csc_matrix(_base_X)
        else:
            raise Exception

        assert len(_X_wip.shape) == 2
        assert _X_wip.shape[1] == _num_cols

        _kwargs['interaction_only'] = _intx_only

        _SPF = SPF(**_kwargs)

        if _num_cols == 0 or (_intx_only and _num_cols < 2):
            with pytest.raises(ValueError):
                _SPF.partial_fit(_X_wip)
            with pytest.raises(ValueError):
                _SPF.fit(_X_wip)
            with pytest.raises(ValueError):
                _SPF.fit_transform(_X_wip)
            _SPF.fit(X_np)
            with pytest.raises(ValueError):
                _SPF.transform(_X_wip)
        else:
            _SPF.partial_fit(_X_wip)
            _SPF.fit(_X_wip)
            _SPF.fit_transform(_X_wip)
            _SPF.transform(_X_wip)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'bsr_matrix'))
    def test_rejects_no_samples(self, _shape, _kwargs, X_np, _format):

        _SPF = SPF(**_kwargs)

        _X_base = np.empty((0, _shape[1]), dtype=np.float64)

        if _format == 'np':
            _X_wip = _X_base
        elif _format == 'pd':
            _X_wip = pd.DataFrame(_X_base)
        elif _format == 'pl':
            _X_wip = pl.from_numpy(_X_base)
        elif _format == 'bsr_matrix':
            _X_wip = ss.coo_array(_X_base)
        else:
            raise Exception


        with pytest.raises(ValueError):
            _SPF.partial_fit(_X_wip)

        with pytest.raises(ValueError):
            _SPF.fit(_X_wip)

        with pytest.raises(ValueError):
            _SPF.fit_transform(_X_wip)

        _SPF.fit(X_np)

        with pytest.raises(ValueError) as e:
            _SPF.transform(_X_wip)
        assert not isinstance(e.value, NotFittedError)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'lil_matrix'))
    @pytest.mark.parametrize('_diff', ('more', 'less', 'same'))
    def test_rejects_bad_num_features(
        self, _X_factory, _shape, _kwargs, _columns, X_np,
        _format, _diff
    ):
        # ** ** ** **
        # THERE CANNOT BE "BAD NUM FEATURES" FOR fit & fit_transform
        # partial_fit & transform is handled by _check_n_features
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

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns_dict[_diff],
            _constants=None,
            _zeros=0,
            _shape=_new_shape_dict[_diff]
        )

        _SPF = SPF(**_kwargs)
        _SPF.fit(X_np)

        if _diff == 'same':
            _SPF.partial_fit(_X_wip)
            _SPF.transform(_X_wip)
        else:
            with pytest.raises(ValueError) as e:
                _SPF.partial_fit(_X_wip)
            assert not isinstance(e.value, NotFittedError)
            with pytest.raises(ValueError) as e:
                _SPF.transform(_X_wip)
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

        TestCls = SPF(**_kwargs)

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
        SPF(**_kwargs).partial_fit(X_np, _y)
        SPF(**_kwargs).fit(X_np, _y)


    def test_conditional_access_to_partial_fit_and_fit(self, X_np, _kwargs):

        TestCls = SPF(**_kwargs)

        # 1) partial_fit() should allow unlimited number of subsequent partial_fits()
        for _ in range(5):
            TestCls.partial_fit(X_np)

        TestCls.reset()

        # 2) one call to fit() should allow subsequent attempts to partial_fit()
        TestCls.fit(X_np)
        TestCls.partial_fit(X_np)

        TestCls.reset()

        # 3) one call to fit() should allow later attempts to fit() (2nd fit will reset)
        TestCls.fit(X_np)
        TestCls.fit(X_np)

        TestCls.reset()

        # 4) a call to fit() after a previous partial_fit() should be allowed
        TestCls.partial_fit(X_np)
        TestCls.fit(X_np)

        TestCls.reset()

        # 5) fit transform() should allow calls ad libido
        for _ in range(5):
            TestCls.fit_transform(X_np)


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'bsr_array'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
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
        SPF(**_kwargs).partial_fit(_X_wip)


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
        self, _kwargs, _shape, _keep
    ):

        # **** **** **** **** **** **** **** **** **** **** **** **** ****
        # THIS TEST IS CRITICAL FOR VERIFYING THAT transform PULLS THE
        # SAME COLUMN INDICES FOR ALL CALLS TO transform() WHEN
        # keep=='random'
        # **** **** **** **** **** **** **** **** **** **** **** **** ****

        # rig X to have columns that will create duplicates when expanded
        _X_np = np.array(
            [
                [1, 0, 0],
                [1, 0, 0],
                [1, 0, 0],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 0]
            ], dtype=np.uint8
        )

        _kwargs['keep'] = _keep

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST THAT ONE-SHOT partial_fit/transform == ONE-SHOT fit/transform
        OneShotPartialFitTestCls = SPF(**_kwargs).partial_fit(_X_np)

        OneShotFullFitTestCls = SPF(**_kwargs).fit(_X_np)

        # poly_combinations_ are equal -- -- -- --
        if _keep != 'random':
            _ = OneShotPartialFitTestCls.poly_combinations_
            __ = OneShotFullFitTestCls.poly_combinations_
            assert _ == __
            del _, __
        # END poly_combinations_ are equal -- -- -- --

        ONE_SHOT_PARTIAL_FIT_TRFM_X = \
            OneShotPartialFitTestCls.transform(_X_np)

        ONE_SHOT_FULL_FIT_TRFM_X = \
            OneShotFullFitTestCls.transform(_X_np)

        # this should be true for all 'keep', including random
        # (random too only because of the special design of X)
        assert np.array_equal(
            ONE_SHOT_PARTIAL_FIT_TRFM_X,
            ONE_SHOT_FULL_FIT_TRFM_X
        ), f"one shot partial fit trfm X != one shot full fit trfm X"

        del OneShotPartialFitTestCls, OneShotFullFitTestCls
        del ONE_SHOT_PARTIAL_FIT_TRFM_X, ONE_SHOT_FULL_FIT_TRFM_X

        # END TEST THAT ONE-SHOT partial_fit/transform==ONE-SHOT fit/transform
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **
        # TEST PARTIAL FIT KEPT COMBINATIONS ARE THE SAME WHEN FULL DATA
        # IS partial_fit() 2X
        SingleFitTestClass = SPF(**_kwargs).fit(_X_np)
        _ = SingleFitTestClass.poly_combinations_

        DoublePartialFitTestClass = SPF(**_kwargs)
        DoublePartialFitTestClass.partial_fit(_X_np)
        __ = DoublePartialFitTestClass.poly_combinations_
        DoublePartialFitTestClass.partial_fit(_X_np)
        ___ = DoublePartialFitTestClass.poly_combinations_

        if _keep != 'random':
            assert _ == __
            assert _ == ___

        assert np.array_equal(
            SingleFitTestClass.transform(_X_np),
            DoublePartialFitTestClass.transform(_X_np)
        )

        del _, __, ___, SingleFitTestClass, DoublePartialFitTestClass

        # END PARTIAL FIT CONSTANTS ARE THE SAME WHEN FULL DATA IS partial_fit() 2X
        # ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **
        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **
        # TEST MANY PARTIAL FITS == ONE BIG FIT

        # STORE CHUNKS TO ENSURE THEY STACK BACK TO THE ORIGINAL X
        _chunks = 3
        X_CHUNK_HOLDER = []
        for row_chunk in range(_chunks):
            _mask_start = row_chunk * _X_np.shape[0] // _chunks
            _mask_end = (row_chunk + 1) * _X_np.shape[0] // _chunks
            X_CHUNK_HOLDER.append(_X_np[_mask_start:_mask_end, :])
        del _mask_start, _mask_end

        assert np.array_equiv(
            np.vstack(X_CHUNK_HOLDER), _X_np
        ), f"agglomerated X chunks != original X"

        PartialFitTestCls = SPF(**_kwargs)
        OneShotFitTransformTestCls = SPF(**_kwargs)

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
            PartialFitTestCls.transform(_X_np)

        del PartialFitTestCls


        # ONE-SHOT FIT TRANSFORM
        FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM = \
            OneShotFitTransformTestCls.fit_transform(_X_np)

        del OneShotFitTransformTestCls

        # ASSERT ALL AGGLOMERATED X TRFMS ARE EQUAL
        assert np.array_equiv(
                FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM,
                FULL_TRFM_X_FROM_PARTIAL_FIT_PARTIAL_TRFM
            ), f"trfm X from partial fit / partial trfm != one-shot fit/trfm X"

        assert np.array_equiv(
                FULL_TRFM_X_ONE_SHOT_FIT_TRANSFORM,
                FULL_TRFM_X_FROM_PARTIAL_FIT_ONESHOT_TRFM
            ), f"trfm X from partial fits / one-shot trfm != one-shot fit/trfm X"

        # TEST MANY PARTIAL FITS == ONE BIG FIT
        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **
        # ** ** ** ** ** ** ** ** ** ** **# ** ** ** ** ** ** ** ** **


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestTransform:

    #     def transform(
    #         self,
    #         X: XContainer
    #     ) -> XContainer:

    # - output is C contiguous


    # @pytest.mark.parametrize('_copy',
    #     (-1, 0, 1, 3.14, True, False, None, 'junk', [0, 1], (1,), {'a': 1}, min)
    # )
    # def test_copy_validation(self, X_np, _shape, _kwargs, _copy):
    #     pass


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dok_array'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = SPF(**_kwargs)
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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_matrix'))
    def test_X_is_not_mutated(
        self, _X_factory, _columns, _shape, _kwargs, _format
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns, _constants=None, _noise=0, _zeros=None,
            _shape=_shape
        )

        if _format == 'np':
            assert _X_wip.flags['C_CONTIGUOUS'] is True

        try:
            _X_wip_before = _X_wip.copy()
        except:
            _X_wip_before = _X_wip.clone()


        _SPF = SPF(**_kwargs).fit(_X_wip)

        # verify _X_wip does not mutate in transform()
        TRFM_X = _SPF.transform(_X_wip)


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


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'coo_array'))
    @pytest.mark.parametrize('min_degree', (1, 2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_accuracy(
        self, _X_factory, _kwargs, _columns, _shape, X_format, min_degree,
        intx_only
    ):

        # this does basic tests for container, dtype, and also
        # properties of the original X part of the output. the lions
        # share of tests for the poly part are in build_poly tests

        # validate the test parameters -------------
        assert isinstance(min_degree, numbers.Integral)
        assert isinstance(intx_only, bool)
        # dont need to validate X_format, X_factory will do it
        # END validate the test parameters -------------

        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format=X_format,
            _dtype='flt',
            _columns=_columns,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )

        # retain original dtype(s) v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if isinstance(_X_wip, (pd.DataFrame, pl.DataFrame)):
            # need np.array for pl dtypes
            _og_dtype = np.array(_X_wip.dtypes)
        else:
            # if np or ss
            _og_dtype = _X_wip.dtype
        # END retain original dtype(s) v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


        # set _kwargs
        _kwargs['min_degree'] = min_degree
        _kwargs['degree'] = 2
        _kwargs['interaction_only'] = intx_only

        TestCls = SPF(**_kwargs)

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # returned format is same as given format
        assert isinstance(TRFM_X, type(_X_wip))

        # if numpy output, is C order
        if isinstance(TRFM_X, np.ndarray):
            assert TRFM_X.flags['C_CONTIGUOUS'] is True

        # shape
        assert TRFM_X.shape[0] == _X_wip.shape[0]
        if min_degree == 1:
            assert TRFM_X.shape[1] > _X_wip.shape[1]

        # returned dtypes are same as given dtypes ** * ** * ** * ** *
        if min_degree == 1:

            # need to get dtypes in 2 chunks, from the original X, and
            # poly should always be float64/Float64
            if isinstance(TRFM_X, (pd.DataFrame, pl.DataFrame)):
                _og_dtypes = np.array(list(_X_wip.dtypes))
                _trfm_dtypes = np.array(list(TRFM_X.dtypes))
                for idx in range(TRFM_X.shape[1]):
                    if idx in range(_X_wip.shape[1]):
                        # the og X part
                        assert _trfm_dtypes[idx] == _og_dtypes[idx]
                    else:
                        # the poly part
                        if isinstance(TRFM_X, pd.DataFrame):
                            assert _trfm_dtypes[idx] == np.float64
                        elif isinstance(TRFM_X, pl.DataFrame):
                            assert _trfm_dtypes[idx] == pl.Float64
            else:
                assert TRFM_X.dtype == _X_wip.dtype

        else:
            # min_degree > 1, only the poly part
            if isinstance(TRFM_X, (pd.DataFrame, pl.DataFrame)):
                _trfm_dtypes = np.array(list(TRFM_X.dtypes))
                for idx in range(TRFM_X.shape[1]):
                    if isinstance(TRFM_X, pd.DataFrame):
                        assert _trfm_dtypes[idx] == np.float64
                    elif isinstance(TRFM_X, pl.DataFrame):
                        assert _trfm_dtypes[idx] == pl.Float64
            else:
                assert TRFM_X.dtype == _X_wip.dtype
        # END returned dtypes are same as given dtypes ** * ** * ** * **

         # if min_degree is 1, assert that part equals the original
        if min_degree == 1:
            if isinstance(TRFM_X, np.ndarray):
                assert np.array_equal(TRFM_X[:, :_X_wip.shape[1]], _X_wip)
            elif isinstance(TRFM_X, pd.DataFrame):
                assert _X_wip.equals(TRFM_X.iloc[:, :_X_wip.shape[1]])
            elif isinstance(TRFM_X, pl.DataFrame):
                assert np.array_equal(TRFM_X[:, :_X_wip.shape[1]], _X_wip)
            elif hasattr(TRFM_X, 'toarray'):
                assert np.array_equal(
                    TRFM_X.tocsc()[:, :_X_wip.shape[1]].toarray(),
                    _X_wip.toarray()
                )
            else:
                raise Exception
        # else:
        #     min_degree >= 2, tested that poly exists, in the correct
        #     container, and that it has the correct dtypes. actual
        #     accuracy tests are too complicated, and redundant with
        #     _build_poly
        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_one_all_nans(self, _kwargs, X_np, _shape, _equal_nan):

        # create 2 columns, one of them is all nans

        # if equal_nan, then SlimPoly should see the nans as a column of
        # constants in X, and transform() should always be a no-op

        # if not equal_nan, then it wont be a column of constants in X,
        # the poly component should have 3 columns.
        #   1) column 1 squared
        #   2) column 2 squared, which should be nans
        #   3) the interaction term, and that should be all nans
        # should return the original 2 columns and the 3 poly columns

        # nans are put in manually later
        _X = X_np[:, :2].copy()

        # set a column to all nans
        _X[:, -1] = np.nan
        # verify last column is all nans
        assert all(nan_mask(_X[:, -1]))

        # do this with interaction_only = False
        _kwargs['interaction_only'] = False
        # scan_X must be True! or SlimPoly wont find the constants in X
        _kwargs['scan_X'] = True
        _kwargs['equal_nan'] = _equal_nan
        TestCls = SPF(**_kwargs).fit(_X)

        if _equal_nan:
            with pytest.warns():
                out = TestCls.transform(_X)
            assert out is None
        elif not _equal_nan:
            out = TestCls.transform(_X)
            assert out.shape == (_shape[0], 5)
            assert np.array_equal(out[:, 0], _X[:, 0])
            assert all(nan_mask(out[:, 1]))
            assert np.array_equal(out[:, 2], np.power(_X[:, 0], 2), equal_nan=True)
            assert all(nan_mask(out[:, 3]))
            assert all(nan_mask(out[:, 4]))


    def test_all_ones_in_X(self, _kwargs, X_np):

        # this should always end in a degenerate state that causes no-ops
        # this tests whether SPF can handle the intermediate degenerate
        # states that exist when the constant in X is 1.

        # do this with interaction_only = False
        _kwargs['interaction_only'] = False

        # scan_X must be True! or SlimPoly wont find the constants in X
        _kwargs['scan_X'] = True

        # create 2 columns, one of them is all ones

        # SlimPoly should see the ones as a column of constants
        # in X, and transform() should always be a no-op

        _X = X_np[:, :2].copy()

        # set a column to all ones
        _X[:, -1] = 1

        TestCls = SPF(**_kwargs).fit(_X)

        with pytest.warns():
            out = TestCls.transform(_X)
        assert out is None


    def test_all_zeros_in_X(self, _kwargs, X_np):

        # this should always end in a degenerate state that causes no-ops
        # this tests whether SPF can handle the intermediate degenerate
        # states that exist when the constant in X is 0.

        # do this with interaction_only = False
        _kwargs['interaction_only'] = False

        # scan_X must be True! or SlimPoly wont find the constants in X
        _kwargs['scan_X'] = True

        # create 2 columns, one of them is all zeros

        # SlimPoly should see the zeros as a column of constants
        # in X, and transform() should always be a no-op

        _X = X_np[:, :2].copy()

        # set a column to all zeros
        _X[:, -1] = 0

        TestCls = SPF(**_kwargs).fit(_X)

        with pytest.warns():
            out = TestCls.transform(_X)
        assert out is None


    @pytest.mark.parametrize('_equal_nan', (True, False))
    def test_intx_creates_all_nans(self, _kwargs, _equal_nan):

        # rig X to have 2 columns that multiply to all nans

        _X = np.array(
            [
                [1, np.nan],
                [2, np.nan],
                [np.nan, 3],
                [np.nan, 4],
            ],
            dtype=np.float64
        )

        # do this with interaction_only = True
        _kwargs['interaction_only'] = True

        _kwargs['equal_nan'] = _equal_nan

        # if equal_nan, then SlimPoly should see the output as a column of
        # constants and not append it.

        # if not equal_nan, then it wont be a column of constants in POLY,
        # the expansion should be 1 column, a column of all nans.
        # should return the original 2 columns and the 1 poly

        TestCls = SPF(**_kwargs).fit(_X)

        if _equal_nan:
            out = TestCls.transform(_X)
            assert np.array_equal(out, _X, equal_nan=True)
        elif not _equal_nan:
            out = TestCls.transform(_X)

            assert out.shape == (_X.shape[0], 3)

            assert np.array_equal(out[:, 0], _X[:, 0], equal_nan=True)
            assert np.array_equal(out[:, 1], _X[:, 1], equal_nan=True)
            assert all(nan_mask(out[:, 2]))


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('_dtype',
         ('int8', 'int16', 'int32', 'int64', 'float64', '<U10', 'object')
    )
    @pytest.mark.parametrize('_has_nan', (True, False))
    @pytest.mark.parametrize('_min_degree', (1, 2))
    def test_dtype_handling(
        self, _X_factory, _shape, _columns, _kwargs, _format, _dtype,
        _has_nan, _min_degree
    ):

        # poly is always created as float64 and if/when merged, the
        # original data is also converted to float64.

        # _dtype '<U10' and 'object' test when numerical data is passed
        # with these formats

        # degree is always set to 2
        # when min_degree == 1, tests mashup of original data and poly
        # when min_degree == 2, tests poly only

        # skip impossible scenarios
        if  _has_nan and _dtype in ('int8', 'int16', 'int32', 'int64'):
            pytest.skip(reason='cant have nans in int dtype')

        if _format == 'csr_matrix' and _dtype in ('<U10', 'object'):
            pytest.skip(
                reason='cant have str or object dtype for scipy sparse'
            )

        if _format == 'pl' and _dtype in ('<U10', 'object'):
            pytest.skip(
                reason='polars cant cast strs to numbers, even if theyre numbers'
            )
        # END skip impossible scenarios

        # build X - - - - - - - - - - - - - - - - - - - - - -
        _X_wip = _X_factory(
            _format=_format,
            _dtype={
                'int8':'int', 'int16':'int', 'int32':'int', 'int64':'int',
                'float64':'flt', '<U10':'flt', 'object':'flt'
            }[_dtype],
            _dupl=None,
            _has_nan=_has_nan,
            _columns=_columns,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )

        # convert all nans to np.nan
        if _has_nan:
            if hasattr(_X_wip, 'toarray'):
                _X_wip.data[nan_mask(_X_wip.data)] = np.nan
            elif isinstance(_X_wip, pl.DataFrame):
                pass
                # _X_wip[nan_mask(_X_wip)] = None
            else:
                _X_wip[nan_mask(_X_wip)] = np.nan

        _non_pl_dtype_dict = {
            'int8': np.int8, 'int16': np.int16, 'int32': np.int32,
            'int64': np.int64, 'float64': np.float64, '<U10': str,
            'object': object
        }

        _pl_dtype_dict = {
            'int8': pl.Int8, 'int16': pl.Int16, 'int32': pl.Int32,
            'int64': pl.Int64, 'float64': pl.Float64, '<U10': pl.Object,
            'object': pl.Object
        }

        try:
            _X_wip = _X_wip.astype(_non_pl_dtype_dict[_dtype])
        except:
            _X_wip = _X_wip.cast(_pl_dtype_dict[_dtype])

        # validate dtype of _X_wip -- -- -- -- -- --
        if _format == 'pd':
            for __dtype in _X_wip.dtypes:
                if '<U' in _dtype:
                    assert __dtype == 'O'
                else:
                    assert __dtype == _non_pl_dtype_dict[_dtype]
        elif _format == 'pl':
            for __dtype in _X_wip.dtypes:
                if '<U' in _dtype:
                    assert __dtype == pl.Object
                else:
                    assert __dtype == _pl_dtype_dict[_dtype]
        elif hasattr(_X_wip, 'toarray'):
            # can only be numeric
            assert _X_wip.dtype == _non_pl_dtype_dict[_dtype]
        else:
            # np
            if '<U' in _dtype:
                assert '<U' in str(_X_wip.dtype)
            else:
                assert _X_wip.dtype == _non_pl_dtype_dict[_dtype]
        # END validate dtype of _X_wip -- -- -- -- -- --
        # END build X - - - - - - - - - - - - - - - - - - - -


        _kwargs['degree'] = 2
        _kwargs['min_degree'] = _min_degree
        _kwargs['scan_X'] = False
        _kwargs['sparse_output'] = False
        _kwargs['equal_nan'] = True

        TestCls = SPF(**_kwargs)

        if _dtype == '<U10':
            # no longer coercing numbers passed as str to float
            with pytest.raises(TypeError):
                TestCls.fit_transform(_X_wip)
            pytest.skip(reason=f"cannot do more tests after except")
        else:
            out = TestCls.fit_transform(_X_wip)


        if _format == 'pd':
            for _c_idx, _out_dtype in enumerate(out.dtypes):
                assert _out_dtype == np.float64
        elif _format == 'pl':
            for _c_idx, _out_dtype in enumerate(out.dtypes):
                assert _out_dtype == pl.Float64
        else:
            assert out.dtype == np.float64


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('_sparse_output', (True, False))
    def test_sparse_output(
        self, _X_factory, _columns, _shape, _kwargs, _format, _sparse_output
    ):

        _X_wip = _X_factory(
            _dupl=None,
            _format=_format,
            _dtype='flt',
            _has_nan=False,
            _columns=_columns,
            _constants=None,
            _noise=0,
            _shape=_shape
        )

        _kwargs['sparse_output'] = _sparse_output

        TestCls = SPF(**_kwargs)

        out = TestCls.fit_transform(_X_wip)

        # when 'sparse_output' is False, return in the original container
        # when True, always return as ss csr, no matter what input container
        if _sparse_output:
            assert isinstance(out, (ss.csr_matrix, ss.csr_array))
        elif not _sparse_output:
            assert isinstance(out, type(_X_wip))


@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestFitTransform:


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'bsr_array'))
    @pytest.mark.parametrize('output_type', (None, 'default', 'pandas', 'polars'))
    def test_output_types(
        self, _X_factory, _columns, _shape, _kwargs, _format,
        output_type
    ):

        _X_wip = _X_factory(
            _dupl=None, _has_nan=False, _format=_format, _dtype='flt',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        TestCls = SPF(**_kwargs)
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


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'coo_matrix'))
    @pytest.mark.parametrize('_sparse_output', (True, False))
    def test_sparse_output(
        self, _X_factory, _columns, _shape, _kwargs, _format, _sparse_output
    ):

        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format=_format,
            _dtype='flt',
            _columns=_columns,
            _constants=None,
            _zeros=0,
            _shape=_shape
        )

        _kwargs['sparse_output'] = _sparse_output

        TestCls = SPF(**_kwargs)

        out = TestCls.fit_transform(_X_wip)

        # when 'sparse_output' is False, return in the original container
        # when True, always return as ss csr, no matter what input container
        if _sparse_output:
            assert isinstance(out, (ss.csr_matrix, ss.csr_array))
        elif not _sparse_output:
            assert isinstance(out, type(_X_wip))





