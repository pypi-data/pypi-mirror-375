# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._validate_data import validate_data
from pybear.utilities._nan_masking import nan_mask
from pybear.utilities._inf_masking import inf_mask

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss
import math


import pytest





class Fixtures:


    @staticmethod
    @pytest.fixture()
    def _good_accept_sparse():
        return ('csr', 'csc', 'coo')


    @staticmethod
    @pytest.fixture()
    def _X_np_nan_and_inf(_X_factory, _shape):

        _X_np_loaded = _X_factory(
            _dupl=None,
            _constants=None,
            _format='np',
            _columns=None,
            _dtype='flt',
            _zeros=None,
            _shape=_shape,
            _has_nan=_shape[0]//5,
        )

        for c_idx in range(_shape[1]):

            r_idxs = np.random.choice(
                list(range(_shape[0])),
                _shape[0]//5,
                replace=False
            )

            values = np.random.choice(
                [np.inf, -np.inf, math.inf, -math.inf, float('inf'), float('-inf')],
                len(r_idxs),
                replace=True
            )

            _X_np_loaded[r_idxs, c_idx] = values


        #  verify this thing is loaded before sending it out
        assert np.any(nan_mask(_X_np_loaded))
        assert np.any(inf_mask(_X_np_loaded))

        return _X_np_loaded


class TestValidateData_ParamValidation(Fixtures):


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # no validation for X, the entire module is for validating X!

    @pytest.mark.parametrize('_param',
        ('copy_X', 'cast_to_ndarray', 'require_all_finite',
        'cast_inf_to_nan', 'standardize_nan', 'ensure_2d')
    )
    @pytest.mark.parametrize('junk',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_junk_bool_params(self, _X_np, _good_accept_sparse, _param, junk):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=junk if _param=='copy_X' else False,
                cast_to_ndarray=junk if _param=='cast_to_ndarray' else False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=junk if _param=='require_all_finite' else False,
                cast_inf_to_nan=junk if _param=='cast_inf_to_nan' else False,
                standardize_nan=junk if _param=='standardize_nan' else False,
                allowed_dimensionality=(1,2),
                ensure_2d=junk if _param=='ensure_2d' else False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('_param',
        ('copy_X', 'cast_to_ndarray', 'require_all_finite',
        'cast_inf_to_nan', 'standardize_nan', 'ensure_2d')
    )
    def test_good_bool_params(self, _X_np, _good_accept_sparse, _param):

        out = validate_data(
            _X_np,
            copy_X=(_param=='copy_X'),
            cast_to_ndarray=(_param=='cast_to_ndarray'),
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=(_param=='require_all_finite'),
            cast_inf_to_nan=(_param=='cast_inf_to_nan'),
            standardize_nan=(_param=='standardize_nan'),
            allowed_dimensionality=(1, 2),
            ensure_2d=(_param=='ensure_2d'),
            order='C',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)


    def test_require_all_finite_conditionals(
        self, _X_np, _good_accept_sparse
    ):

        # f"if :param: require_all_finite is True, then :param: "
        # f"standardize_nan must be False."

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=True,
                cast_inf_to_nan=True,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )

        # f"if :param: require_all_finite is True, then :param: "
        # f"cast_inf_to_nan must be False."

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=True,
                cast_inf_to_nan=False,
                standardize_nan=True,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    # accept_sparse -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk',
        (-2.7, -1, 0, 1, 2.7, 'junk', [['csc','csr']], {'A':1}, lambda x: x)
    )
    def test_rejects_junk_accept_sparse(self, _X_np, junk):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=junk,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('bad', (['love', 'happiness'], {'junk', 'trash'}))
    def test_rejects_bad_accept_sparse(self, _X_np, bad):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=bad,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good',
        (None, False, ('csc', 'csr', 'coo'), {'bsr', 'dia'}, ('lil', 'dok'))
    )
    def test_good_accept_sparse(self, _X_np, good):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=good,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)

    # END accept_sparse -- -- -- -- -- -- -- -- --


    # dtype -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_dtype',
        (-2.7, -1, 0, 1, 2.7, [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_rejects_junk_dtype(self, _X_np, _good_accept_sparse, junk_dtype):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype=junk_dtype,
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('bad_dtype', ('love', 'happiness', 'junk', 'trash'))
    def test_rejects_bad_dtype(self, _X_np, _good_accept_sparse, bad_dtype):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype=bad_dtype,
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good_dtype', ('numeric', 'any'))
    def test_good_dtype(self, _X_np, _good_accept_sparse, good_dtype):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype=good_dtype,
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)

    # END dtype -- -- -- -- -- -- -- -- -- -- --


    # allowed_dimensionality -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_a_d',
        (-2.7, 2.7, True, False, None, 'trash', (True, False), {'A':1}, lambda x: x)
    )
    def test_rejects_junk_a_d(self, _X_np, _good_accept_sparse, junk_a_d):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=junk_a_d,
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('bad_a_d',
        (-1, 0, (-1, 0), [0, 1], {2, 3, 4})
    )
    def test_rejects_bad_a_d(self, _X_np, _good_accept_sparse, bad_a_d):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=bad_a_d,
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good_a_d', (1, 2, (1, ), [1, 2], {2, }))
    def test_good_a_d(self, _X_np, _good_accept_sparse, good_a_d):

        _X_shape_should_raise = False
        if isinstance(good_a_d, int):
            if len(_X_np.shape) != good_a_d:
                _X_shape_should_raise = True
        else:
            if len(_X_np.shape) not in good_a_d:
                _X_shape_should_raise = True

        if _X_shape_should_raise:
            with pytest.raises(ValueError):
                validate_data(
                    _X_np,
                    copy_X=False,
                    cast_to_ndarray=True,
                    accept_sparse=_good_accept_sparse,
                    dtype='any',
                    require_all_finite=False,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=good_a_d,
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=1,
                    ensure_max_features=None,
                    ensure_min_samples=1,
                    sample_check=None
                )
        else:
            out = validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=True,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=good_a_d,
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )

            assert isinstance(out, np.ndarray)

    # END allowed_dimensionality -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # order -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_order',
        (-2.7, -1, 0, 1, 2.7, True, None, [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_rejects_junk_order(self, _X_np, _good_accept_sparse, junk_order):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order=junk_order,
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('bad_order', ('q', 'r', 'S', 'T'))
    def test_rejects_bad_order(self, _X_np, _good_accept_sparse, bad_order):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order=bad_order,
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good_order', ('c', 'C', 'f', 'F'))
    def test_good_order(self, _X_np, _good_accept_sparse, good_order):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order=good_order,
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)
    # order -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # ensure_min_features -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_min_features',
        (-2.7, 2.7, True, False, None, [0,1], (0,1), {'A':1}, lambda x: x, min)
    )
    def test_rejects_junk_min_features(
        self, _X_np, _good_accept_sparse, junk_min_features
    ):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=junk_min_features,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    def test_rejects_bad_min_features(self, _X_np, _good_accept_sparse):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=-1,   # <============
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good_min_features', (0, 1, 2))
    def test_good_min_features(self, _X_np, _good_accept_sparse, good_min_features):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=good_min_features,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)
    # END ensure_min_features -- -- -- -- -- -- -- -- -- -- -- --

    # ensure_max_features -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_max_features',
        (-2.7, 2.7, True, False, None, [0,1], (0,1), {'A':1}, lambda x: x, min)
    )
    def test_rejects_junk_max_features(
        self, _X_np, _good_accept_sparse, junk_max_features
    ):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=0,
                ensure_max_features=junk_max_features,
                ensure_min_samples=1,
                sample_check=False
            )


    @pytest.mark.parametrize('min_features, max_features',
        ((-2, -1), (0, -1), (2, 1))
    )
    def test_rejects_bad_max_features(
        self, _X_np, _good_accept_sparse, min_features, max_features
    ):

        # test max_features < 0 and max_features < min_features

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=min_features,
                ensure_max_features=max_features,
                ensure_min_samples=1,
                sample_check=None
            )


    @pytest.mark.parametrize('good_max_features', (0, 1, 2))
    def test_good_max_features(self, _X_np, _good_accept_sparse, good_max_features):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=0,
            ensure_max_features=_X_np.shape[1] + good_max_features,
            ensure_min_samples=1,
            sample_check=None
        )

        assert isinstance(out, np.ndarray)
    # END ensure_max_features -- -- -- -- -- -- -- -- -- -- -- --

    # ensure_min_samples -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_min_samples',
        (-2.7, 2.7, True, False, None, [0,1], (0,1), {'A':1}, lambda x: x, min)
    )
    def test_rejects_junk_min_samples(
        self, _X_np, _good_accept_sparse, junk_min_samples
    ):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=junk_min_samples
            )


    def test_rejects_bad_min_samples(self, _X_np, _good_accept_sparse):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=-1  # <===========
            )


    @pytest.mark.parametrize('good_min_samples', (0, 1, 2))
    def test_good_min_samples(self, _X_np, _good_accept_sparse, good_min_samples):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_min_samples=good_min_samples
        )

        assert isinstance(out, np.ndarray)
    # END ensure_min_samples -- -- -- -- -- -- -- -- -- -- -- -- --

    # sample_check -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_sample_check',
        (-2.7, 2.7, True, False, [0,1], (0,1), {'A':1}, lambda x: x, min)
    )
    def test_rejects_sample_check(
        self, _X_np, _good_accept_sparse, junk_sample_check
    ):

        with pytest.raises(TypeError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=1,
                sample_check=junk_sample_check
            )


    def test_rejects_bad_sample_check(self, _X_np, _good_accept_sparse):

        with pytest.raises(ValueError):
            validate_data(
                _X_np,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=0,
                sample_check=-1
            )


    def test_good_sample_check(self, _X_np, _good_accept_sparse):

        out = validate_data(
            _X_np,
            copy_X=False,
            cast_to_ndarray=True,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=_X_np.shape[0]
        )

        assert isinstance(out, np.ndarray)
    # END ensure_min_samples -- -- -- -- -- -- -- -- -- -- -- -- --

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *







class TestValidateDataAccuracy(Fixtures):


    @pytest.mark.parametrize('_X_format', ('list', 'tuple', 'set'))
    @pytest.mark.parametrize('_cast_to_ndarray', (True, False))
    def test_X_rejects_builtins(self, _X_format, _cast_to_ndarray):

        # caught in _cast_to_ndarray() for being a python builtin if
        #       cast_to_ndarray is True
        # caught in _check_shape() for not having 'shape' attribute if
        #       cast_to_ndarray is False


        if _X_format == 'list':
            _X_wip = list(range(10))
        elif _X_format == 'tuple':
            _X_wip = tuple(range(10))
        elif _X_format == 'set':
            _X_wip = set(range(10))
        else:
            raise Exception


        with pytest.raises(ValueError):

            validate_data(
                _X_wip,
                copy_X=False,
                cast_to_ndarray=_cast_to_ndarray,
                accept_sparse=False,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=1
            )


    @pytest.mark.parametrize('_X_format', ('np', 'pd', 'pl', 'csr', 'csc', 'coo'))
    @pytest.mark.parametrize('_cast_to_ndarray', (True, False))
    @pytest.mark.parametrize('_has_nan', (True, False))
    @pytest.mark.parametrize('_order', ('C', 'F'))
    def test_cast_to_nd_array_and_order(
        self, _X_factory, _X_format, _good_accept_sparse, _cast_to_ndarray,
        _has_nan, _order
    ):

        # order doesnt matter if not returning np
        # np wont be returned if not given np and not casting to np

        # dont worry about 1D (C and F should both always be True),
        # testing 2D order should be enough

        # this also tests that funky pd nan-likes are cast to ndarray.
        # cast_to_ndarray is robust to funky nans because no dtype
        # constraint is imposed. cast_to_ndarray is not forcing the data
        # over to np.float64, and any funky nans will coerce dtype over
        # to object.


        _X_wip = _X_factory(
            _dupl=None,
            _format=_X_format,
            _dtype='flt',
            _has_nan=_has_nan,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=(20, 10)
        )

        out = validate_data(
            _X_wip,
            copy_X=False,
            cast_to_ndarray=_cast_to_ndarray,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order=_order,
            ensure_min_features=1,
            ensure_min_samples=1
        )

        if _cast_to_ndarray:
            assert isinstance(out, np.ndarray)
            if _order == 'C':
                assert out.flags['C_CONTIGUOUS'] is True
            if _order == 'F':
                assert out.flags['F_CONTIGUOUS'] is True
        elif not _cast_to_ndarray:
            assert isinstance(out, type(_X_wip))
            if isinstance(out, np.ndarray):
                if _order == 'C':
                    assert out.flags['C_CONTIGUOUS'] is True
                if _order == 'F':
                    assert out.flags['F_CONTIGUOUS'] is True


    @pytest.mark.parametrize('_X_format', ('np', 'pd', 'pl', 'csc', 'csr'))
    @pytest.mark.parametrize('_accept_sparse', (False, None, ('csc', 'dia', 'coo')))
    def test_accept_sparse(self, _X_factory, _X_format, _accept_sparse):


        _X_wip = _X_factory(
            _dupl=None,
            _format=_X_format,
            _dtype='flt',
            _has_nan=False,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=(20, 10)
        )

        if hasattr(_X_wip, 'toarray'):

            if _accept_sparse in [None, False] or _X_format not in _accept_sparse:

                with pytest.raises(TypeError):

                    validate_data(
                        _X_wip,
                        copy_X=False,
                        cast_to_ndarray=True,
                        accept_sparse=_accept_sparse,
                        dtype='any',
                        require_all_finite=False,
                        cast_inf_to_nan=False,
                        standardize_nan=False,
                        allowed_dimensionality=(1, 2),
                        ensure_2d=False,
                        order='C',
                        ensure_min_features=1,
                        ensure_min_samples=1
                    )

            else:
                out = validate_data(
                    _X_wip,
                    copy_X=False,
                    cast_to_ndarray=True,
                    accept_sparse=_accept_sparse,
                    dtype='any',
                    require_all_finite=False,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=(1, 2),
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=1,
                    ensure_min_samples=1
                )

                assert isinstance(out, np.ndarray)


    @pytest.mark.parametrize('_X_format', ('np',  'pd', 'pl', 'csr', 'csc', 'coo'))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj'))
    @pytest.mark.parametrize('_shape', ((10, ), (1, 10), (10, 1), (10, 10)))
    @pytest.mark.parametrize('_allowed_dimensionality', ((1,), (2,), (1,2)))
    def test_allowed_dimensionality(
        self, _X_format, _dtype, _shape, _good_accept_sparse,
        _allowed_dimensionality
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if len(_shape)==1 and _X_format in ['csr', 'csc', 'coo']:
            pytest.skip(reason=f"impossible condition, scipy must be 2D")

        if _X_format not in ['np', 'pd', 'pl'] and _dtype in ['str', 'obj']:
            pytest.skip(reason=f"scipy can only be numeric")

        # END skip impossible conditons -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype == 'flt':
            _base_X = np.random.uniform(0, 1, _shape)
        elif _dtype == 'int':
            _base_X = np.random.randint(0, 1, _shape)
        elif _dtype == 'str':
            _base_X = np.random.choice(list('abcde'), _shape, replace=True)
            _base_X = _base_X.astype('<U1')
        elif _dtype == 'obj':
            _base_X = np.random.choice(list('abcde'), _shape, replace=True)
            _base_X = _base_X.astype(object)
        else:
            raise Exception

        if _X_format == 'np':
            _X_wip = _base_X
        elif _X_format == 'pd':
            if len(_base_X.shape)==1:
                _X_wip = pd.Series(_base_X)
            elif len(_base_X.shape)==2:
                _X_wip = pd.DataFrame(_base_X)
            else:
                raise Exception
        elif _X_format == 'pl':
            if len(_base_X.shape)==1:
                _X_wip = pl.Series(_base_X)
            elif len(_base_X.shape)==2:
                _X_wip = pl.from_numpy(_base_X)
            else:
                raise Exception
        elif _X_format == 'csr':
            _X_wip = ss.csr_array(_base_X)
        elif _X_format == 'csc':
            _X_wip = ss.csc_array(_base_X)
        elif _X_format == 'coo':
            _X_wip = ss.coo_array(_base_X)
        else:
            raise Exception

        disallowed_dimensions = False
        if len(_shape) == 1 and _allowed_dimensionality == (2,):
            disallowed_dimensions = True
        if len(_shape) == 2 and _allowed_dimensionality == (1,):
            disallowed_dimensions = True

        if disallowed_dimensions:
            with pytest.raises(ValueError):
                validate_data(
                    _X_wip,
                    copy_X=True,
                    cast_to_ndarray=False,
                    accept_sparse=_good_accept_sparse,
                    dtype='any',
                    require_all_finite=False,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=_allowed_dimensionality,
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=1,
                    ensure_min_samples=1
                )
        else:
            out = validate_data(
                _X_wip,
                copy_X=True,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=_allowed_dimensionality,
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=1
            )

            assert isinstance(out, type(_X_wip))
            assert out.shape == _X_wip.shape


    @pytest.mark.parametrize('_X_format', ('np', 'pd', 'pl', 'csr', 'csc', 'coo'))
    @pytest.mark.parametrize('_start_dim', ('1D', '2D'))
    @pytest.mark.parametrize('_ensure_2D', (True, False))
    def test_ensure_2D(
        self, _X_np, _good_accept_sparse, _X_format, _start_dim, _ensure_2D
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _start_dim == '1D' and _X_format in ['csr', 'csc', 'coo']:
            pytest.skip(reason=f"impossible condition, scipy must be 2D")

        # END skip impossible conditons -- -- -- -- -- -- -- -- -- -- -- -- --


        if _start_dim == '1D':
            if _X_format == 'np':
                _X_wip = _X_np.copy()[:, 0].ravel()
            elif _X_format == 'pd':
                _X_wip = pd.Series(_X_np[:, 0])
            elif _X_format == 'pl':
                _X_wip = pl.Series(_X_np[:, 0])
            else:
                raise Exception
        elif _start_dim == '2D':
            if _X_format == 'np':
                _X_wip = _X_np.copy()
            elif _X_format == 'pd':
                _X_wip = pd.DataFrame(_X_np)
            elif _X_format == 'pl':
                _X_wip = pl.DataFrame(_X_np)
            elif _X_format == 'csr':
                _X_wip = ss.csr_array(_X_np)
            elif _X_format == 'csc':
                _X_wip = ss.csc_array(_X_np)
            elif _X_format == 'coo':
                _X_wip = ss.coo_array(_X_np)
            else:
                raise Exception
        else:
            raise Exception


        out = validate_data(
            _X_wip,
            copy_X=True,
            cast_to_ndarray=False,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(1,2),
            ensure_2d=_ensure_2D,
            order='C',
            ensure_min_features=1,
            ensure_min_samples=1
        )

        if _ensure_2D:
            if _start_dim == '1D':
                if _X_format == 'np':
                    assert isinstance(out, np.ndarray)
                    assert out.shape == (_X_np.shape[0], 1)
                elif _X_format == 'pd':
                    assert isinstance(out, pd.DataFrame)
                    assert out.shape == (_X_np.shape[0], 1)
                elif _X_format == 'pl':
                    assert isinstance(out, pl.DataFrame)
                    assert out.shape == (_X_np.shape[0], 1)
                else:
                    # scipy sparse should skip above
                    raise Exception
            elif _start_dim == '2D':
                assert isinstance(out, type(_X_wip))
                assert out.shape == _X_wip.shape
        elif not _ensure_2D:
            assert isinstance(out, type(_X_wip))
            assert out.shape == _X_wip.shape



    @pytest.mark.parametrize('_X_format', ('np', 'pd', 'pl', 'csc', 'csr'))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_allowed_dtype', ('numeric', 'any'))
    def test_dtype(
        self, _X_factory, _good_accept_sparse, _X_format, _dtype, _allowed_dtype
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype in ('str', 'obj', 'hybrid') and _X_format not in ('np', 'pd', 'pl'):
            pytest.skip(reason=f"impossible condition, scipy must be numeric")

        # END skip impossible conditons -- -- -- -- -- -- -- -- -- -- -- -- --

        _X_wip = _X_factory(
            _dupl=None,
            _format=_X_format,
            _dtype=_dtype,
            _has_nan=False,
            _columns=None,
            _constants=None,
            _zeros=None,
            _shape=(20, 10)
        )

        if _allowed_dtype == 'any':

            out = validate_data(
                _X_wip,
                copy_X=False,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype=_allowed_dtype,
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=1
            )

            assert isinstance(out, type(_X_wip))

        elif _allowed_dtype == 'numeric':
            if _dtype in ['flt', 'int']:
                out = validate_data(
                    _X_wip,
                    copy_X=False,
                    cast_to_ndarray=False,
                    accept_sparse=_good_accept_sparse,
                    dtype=_allowed_dtype,
                    require_all_finite=False,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=(1, 2),
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=1,
                    ensure_min_samples=1
                )

                assert isinstance(out, type(_X_wip))

            elif _dtype in ['str', 'obj', 'hybrid']:

                with pytest.raises(TypeError):
                    validate_data(
                        _X_wip,
                        copy_X=False,
                        cast_to_ndarray=False,
                        accept_sparse=_good_accept_sparse,
                        dtype=_allowed_dtype,
                        require_all_finite=False,
                        cast_inf_to_nan=False,
                        standardize_nan=False,
                        allowed_dimensionality=(1, 2),
                        ensure_2d=False,
                        order='C',
                        ensure_min_features=1,
                        ensure_min_samples=1
                    )

            else:
                raise Exception
        else:
            raise Exception


    @pytest.mark.parametrize('_state', ('clean', 'dirty'))
    @pytest.mark.parametrize('_require_all_finite', (True, False))
    def test_require_all_finite(
        self, _X_np, _good_accept_sparse, _X_np_nan_and_inf, _state,
        _require_all_finite
    ):

        if _state == 'clean':
            _X_wip = _X_np
        elif _state == 'dirty':
            _X_wip = _X_np_nan_and_inf
        else:
            raise Exception

        if _require_all_finite and _state == 'dirty':
            with pytest.raises(ValueError):
                validate_data(
                    _X_wip,
                    copy_X=True,
                    cast_to_ndarray=False,
                    accept_sparse=_good_accept_sparse,
                    dtype='any',
                    require_all_finite=_require_all_finite,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=(1, 2),
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=1,
                    ensure_min_samples=1
                )
        else:
            out = validate_data(
                _X_wip,
                copy_X=True,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=_require_all_finite,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_min_samples=1
            )

            assert isinstance(out, type(_X_wip))


    def test_cast_inf_to_nan(self, _X_np_nan_and_inf, _good_accept_sparse):

        _X_wip = _X_np_nan_and_inf.copy()

        NAN_MASK_IN = nan_mask(_X_wip)
        INF_MASK_IN = inf_mask(_X_wip)

        out = validate_data(
            _X_wip,
            copy_X=True,
            cast_to_ndarray=False,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=True,
            standardize_nan=False,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_min_samples=1
        )

        assert isinstance(out, type(_X_wip))

        # nan_mask and inf_mask should start out different
        # but after cast to nan, nan_mask should equal inf_mask + nan_mask

        assert not np.array_equal(NAN_MASK_IN, INF_MASK_IN)

        NAN_MASK_OUT = nan_mask(out)

        assert np.array_equal(
            NAN_MASK_OUT,
            (NAN_MASK_IN + INF_MASK_IN).astype(bool)
        )

        outputted_nans = out[NAN_MASK_IN].ravel()

        # if all nans are set to np.nan, all of those values should be np.float64
        assert all(map(
            isinstance, outputted_nans, (np.float64 for _ in outputted_nans)
        ))
        # np.nan when converted to str should repr as 'nan'
        assert all(map(lambda x: x=='nan', list(map(str, outputted_nans))))


    def test_standardize_nan(self, _X_np_nan_and_inf, _good_accept_sparse):

        _X_wip = _X_np_nan_and_inf.copy()

        NAN_MASK_IN = nan_mask(_X_wip)
        INF_MASK_IN = inf_mask(_X_wip)

        out = validate_data(
            _X_wip,
            copy_X=True,
            cast_to_ndarray=False,
            accept_sparse=_good_accept_sparse,
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=True,
            allowed_dimensionality=(1, 2),
            ensure_2d=False,
            order='C',
            ensure_min_features=1,
            ensure_min_samples=1
        )

        assert not np.array_equal(NAN_MASK_IN, INF_MASK_IN)

        NAN_MASK_OUT = nan_mask(out)

        assert np.array_equal(NAN_MASK_OUT, NAN_MASK_IN)

        outputted_nans = out[NAN_MASK_IN].ravel()

        # if all nans are set to np.nan, all of those values should be np.float64
        assert all(map(
            isinstance, outputted_nans, (np.float64 for _ in outputted_nans)
        ))
        # np.nan when converted to str should repr as 'nan'
        assert all(map(lambda x: x=='nan', list(map(str, outputted_nans))))


    @pytest.mark.parametrize('_X_format', ('np', 'pd', 'pl', 'csr', 'csc', 'coo'))
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj'))
    @pytest.mark.parametrize('_shape',
        ((1, ), (10, ), (1, 10), (10, 1), (2, 10), (10, 2), (10, 10))
    )
    @pytest.mark.parametrize('_min_features', (0, 1))
    @pytest.mark.parametrize('_max_features', (1, 2, None))
    @pytest.mark.parametrize('_min_samples', (0, 1))
    @pytest.mark.parametrize('_sample_check', (None, 0, 1))
    def test_features_and_samples(
        self, _X_factory, _X_format, _dtype, _shape, _min_features,
        _max_features, _min_samples, _sample_check, _good_accept_sparse
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if len(_shape)==1 and _X_format in ['csr', 'csc', 'coo']:
            pytest.skip(reason=f"impossible condition, scipy must be 2D")

        if _X_format not in ['np', 'pd', 'pl'] and _dtype in ['str', 'obj']:
            pytest.skip(reason=f"scipy can only be numeric")

        # END skip impossible conditons -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype == 'flt':
            _base_X = np.random.uniform(0, 1, _shape)
        elif _dtype == 'int':
            _base_X = np.random.randint(0, 1, _shape)
        elif _dtype == 'str':
            _base_X = np.random.choice(list('abcde'), _shape, replace=True)
            _base_X = _base_X.astype('<U1')
        elif _dtype == 'obj':
            _base_X = np.random.choice(list('abcde'), _shape, replace=True)
            _base_X = _base_X.astype(object)
        else:
            raise Exception

        if _X_format == 'np':
            _X_wip = _base_X
        elif _X_format == 'pd':
            if len(_base_X.shape)==1:
                _X_wip = pd.Series(_base_X)
            elif len(_base_X.shape)==2:
                _X_wip = pd.DataFrame(_base_X)
            else:
                raise Exception
        elif _X_format == 'pl':
            if len(_base_X.shape)==1:
                _X_wip = pl.Series(_base_X)
            elif len(_base_X.shape)==2:
                _X_wip = pl.DataFrame(_base_X)
            else:
                raise Exception
        elif _X_format == 'csr':
            _X_wip = ss.csr_array(_base_X)
        elif _X_format == 'csc':
            _X_wip = ss.csc_array(_base_X)
        elif _X_format == 'coo':
            _X_wip = ss.coo_array(_base_X)
        else:
            raise Exception

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        except_for_max_features_lt_min_features = False
        if _max_features and _max_features < _min_features:
            except_for_max_features_lt_min_features = True
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        except_for_too_few_features = False
        if len(_X_wip.shape) == 1:
            # n_features == 1
            if _min_features > 1:
                except_for_too_few_features = True
        elif len(_X_wip.shape) == 2:
            if _X_wip.shape[1] < _min_features:
                except_for_too_few_features = True
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        except_for_too_many_features = False
        if _max_features:
            if len(_X_wip.shape) == 1:
                # n_features == 1
                if _max_features < 1:
                    except_for_too_many_features = True
            elif len(_X_wip.shape) == 2:
                if _X_wip.shape[1] > _max_features:
                    except_for_too_many_features = True
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        except_for_too_few_samples = False
        if _sample_check is None and _X_wip.shape[0] < _min_samples:
            except_for_too_few_samples = True
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        except_for_sample_check = False
        if _sample_check and _sample_check != 0:
            # look at the formulas where sample_check is passed to see
            # how this is being tested.
            # it is X.shape[0] + sample_check, and sample check is 0 or
            # 1, so 0 should pass and 1 should fail
            except_for_sample_check = True
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        value_error = 0
        value_error += except_for_max_features_lt_min_features
        value_error += except_for_too_few_features
        value_error += except_for_too_many_features
        value_error += except_for_too_few_samples
        value_error += except_for_sample_check

        if value_error:
            with pytest.raises(ValueError):
                validate_data(
                    _X_wip,
                    copy_X=True,
                    cast_to_ndarray=False,
                    accept_sparse=_good_accept_sparse,
                    dtype='any',
                    require_all_finite=False,
                    cast_inf_to_nan=False,
                    standardize_nan=False,
                    allowed_dimensionality=(1, 2),
                    ensure_2d=False,
                    order='C',
                    ensure_min_features=_min_features,
                    ensure_max_features=_max_features,
                    ensure_min_samples=_min_samples,
                    sample_check= \
                        _X_wip.shape[0] + _sample_check if _sample_check else None
                )
        else:
            out = validate_data(
                _X_wip,
                copy_X=True,
                cast_to_ndarray=False,
                accept_sparse=_good_accept_sparse,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=_min_features,
                ensure_max_features=_max_features,
                ensure_min_samples=_min_samples,
                sample_check= \
                    _X_wip.shape[0] + _sample_check if _sample_check else None
            )

            assert isinstance(out, type(_X_wip))

























