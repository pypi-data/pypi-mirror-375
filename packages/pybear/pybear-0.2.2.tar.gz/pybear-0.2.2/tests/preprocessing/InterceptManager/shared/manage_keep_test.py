# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import random

import numpy as np

from pybear.preprocessing._InterceptManager._shared._manage_keep import (
    _manage_keep
)


# no scipy sparse are tested here, should be comparable to numpy

class TestManageKeep:


    # callable keep converts X to int, validated against _constant_columns
    # keep feature str converted to int, validated against _constant_columns
    # int keep validated against _constant_columns
    # keep in ('first', 'last', 'random') warns if no constants, otherwise
    #   converted to int
    # keep == 'none', passes through
    # isinstance(_keep, dict), passes through


    # dict v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'))
    @pytest.mark.parametrize('_keep',
        ({'Intercept': 1}, {'innards': 'not validated'})
    )
    @pytest.mark.parametrize('_const_cols', ({}, {0:1, 1:np.nan, 2:0}))
    def test_dict_passes_thru(
        self, _X_factory, _columns, _format, _keep, _const_cols, _shape
    ):

        # dict passes thru. len==1 & key is str validated in _keep_and_columns

        _X = _X_factory(
            _format=_format,
            _dtype='int',
            _columns=_columns,
            _constants=_const_cols,
            _shape=_shape
        )

        _columns = np.array(_X.columns) if _format in ['pd', 'pl'] else None
        _rand_idx = random.choice(list(_const_cols)) if len(_const_cols) else None

        out = _manage_keep(
            _keep=_keep,
            _X=_X,
            _constant_columns=_const_cols,
            _n_features_in=_shape[1],
            _feature_names_in=_columns,
            _rand_idx=_rand_idx
        )

        assert isinstance(out, dict), "_manage_keep dict did not return dict"
        assert out == _keep, f"_manage_keep altered keep dict[str, any]"
    # END dict v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


    # callable v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'dok_array'))
    @pytest.mark.parametrize('_keep', (lambda x: 0, lambda x: 100))
    @pytest.mark.parametrize('_const_cols', ({}, {0:1, 1:np.nan, 2:0}))
    def test_callable(
        self, _X_factory, _columns, _format, _keep, _const_cols, _shape
    ):

        # from _keep_and_columns, we already know that keep callable returns an
        # integer within range of X.shape[1]. just needs to verify the
        # returned idx is actually a column of constants.

        _X = _X_factory(
            _format=_format,
            _dtype='int',
            _columns=_columns,
            _constants=_const_cols,
            _shape=_shape
        )

        _columns = np.array(_X.columns) if _format in ['pd', 'pl'] else None
        _rand_idx = random.choice(list(_const_cols)) if len(_const_cols) else None

        if _keep(_X) in _const_cols:
            out = _manage_keep(
                _keep=_keep,
                _X=_X,
                _constant_columns=_const_cols,
                _n_features_in=_shape[1],
                _feature_names_in=_columns,
                _rand_idx=_rand_idx
            )

            assert isinstance(out, int), \
                f"_manage_keep callable did not return integer"
            assert out == _keep(_X), \
                (f"_manage_keep did not return expected keep callable output. "
                 f"exp {_keep(_X)}, got {out}")

        elif _keep(_X) not in _const_cols:
            with pytest.raises(ValueError):
                _manage_keep(
                    _keep=_keep,
                    _X=_X,
                    _constant_columns=_const_cols,
                    _n_features_in=_shape[1],
                    _feature_names_in=_columns,
                    _rand_idx=_rand_idx
                )
    # END callable v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # feature name str v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @pytest.mark.parametrize('_format', ('pd', 'pl'))
    @pytest.mark.parametrize('_keep', ('column_1', 'column_2', 'column_3'))
    @pytest.mark.parametrize('_const_cols', ({}, {0: 1, 1: np.nan}))
    def test_feature_name_str(
        self, _X_factory, _columns, _format, _keep, _const_cols, _shape
    ):

        # _keep_and_columns caught if keep feature name:
        # - was passed with no header (ie for a numpy array) -
        #       dont need to test np, impossible condition.
        # - is not in the header - dont need to test, impossible condition

        # _manage_keep only validates if __keep not in _const_cols

        X_pd = _X_factory(
            _format=_format,
            _dtype='int',
            _columns=_columns,
            _constants=_const_cols,
            _shape=_shape
        )

        exp_idx = {'column_1': 0, 'column_2': 1, 'column_3': 2}[_keep]

        _keep = _columns[exp_idx]

        _rand_idx = random.choice(list(_const_cols)) if len(_const_cols) else None

        if exp_idx in _const_cols:
            out = _manage_keep(
                _keep=_keep,
                _X=X_pd,
                _constant_columns=_const_cols,
                _n_features_in=_shape[1],
                _feature_names_in=np.array(X_pd.columns),
                _rand_idx=_rand_idx
            )

            assert isinstance(out, int), \
                f"_manage_keep feature name did not return integer"
            assert out == exp_idx, \
                (f"_manage_keep did not return expected keep feature name index "
                 f"exp {exp_idx}, got {out}")

        elif exp_idx not in _const_cols:
            with pytest.raises(ValueError):
                _manage_keep(
                    _keep=_keep,
                    _X=X_pd,
                    _constant_columns=_const_cols,
                    _n_features_in=_shape[1],
                    _feature_names_in=np.array(X_pd.columns),
                    _rand_idx=_rand_idx
                )
    # END feature name str v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


    # literal str v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr_matrix'))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random', 'none'))
    @pytest.mark.parametrize('_const_cols',
        ({}, {0: 1, 1: np.nan, 2: 0}, {7:1, 8:0, 9:np.e}, {4:-1, 3:2})
    )
    def test_literal_str(
        self, _X_factory, _columns, _format, _keep, _const_cols, _shape
    ):

        # what we know:
        # the only possible strings that can get to _manage_keep besides
        # feature names are literals ('first', 'last', 'random', 'none')
        # any other string would except in _keep_and_columns.
        # only need to test the exact cases of the literals.
        # the returned value must be in _constant_columns except when
        # 'keep' is 'none' or _constant_columns is empty,
        # if _constant_columns is empty, returns 'none'.

        _X = _X_factory(
            _format=_format,
            _dtype='int',
            _columns=_columns,
            _constants=_const_cols,
            _shape=_shape
        )

        _columns = np.array(_X.columns) if _format in ['pd', 'pl'] else None
        _rand_idx = random.choice(list(_const_cols)) if len(_const_cols) else None

        out = _manage_keep(
            _keep=_keep,
            _X=_X,
            _constant_columns=_const_cols,
            _n_features_in=_shape[1],
            _feature_names_in=_columns,
            _rand_idx=_rand_idx
        )

        if len(_const_cols) == 0:
            assert out == 'none'
        elif _keep == 'none':
            assert out == 'none'
        elif _keep in ('first', 'last'):
            _sorted_const_cols = sorted(list(_const_cols.keys()))
            if _keep == 'first':
                exp_idx = _sorted_const_cols[0]
            elif _keep == 'last':
                exp_idx = _sorted_const_cols[-1]
            assert out == exp_idx, \
                (f"_manage_keep did not return expected keep literal "
                 f"index, exp {exp_idx}, got {out}")
        elif _keep == 'random':
            assert out in range(_shape[1])
        else:
            raise Exception
    # END literal str v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    # int v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('_keep', (0, 10, 2000, 1_000_000_000))
    @pytest.mark.parametrize('_const_cols', ({}, {0:1, 1:np.nan, 9:0}))
    def test_integer(
        self, _X_factory, _columns, _format, _keep, _const_cols, _shape
    ):

        # from _keep_and_columns, we already know that keep integer is in
        # range(X.shape[1]). just need to verify the idx is actually a
        # column of constants.

        _X = _X_factory(
            _format=_format,
            _dtype='int',
            _columns=_columns,
            _constants=_const_cols,
            _shape=_shape
        )

        _columns = np.array(_X.columns) if _format in ['pd', 'pl'] else None
        _rand_idx = random.choice(list(_const_cols)) if len(_const_cols) else None

        if _keep in _const_cols:
            out = _manage_keep(
                _keep=_keep,
                _X=_X,
                _constant_columns=_const_cols,
                _n_features_in=_shape[1],
                _feature_names_in=_columns,
                _rand_idx=_rand_idx
            )

            assert isinstance(out, int), \
                f"_manage_keep integer did not return integer"
            assert out == _keep, \
                (f"_manage_keep integer did not return expected integer. "
                 f"exp {_keep}, got {out}")

        elif _keep not in _const_cols:
            with pytest.raises(ValueError):
                _manage_keep(
                    _keep=_keep,
                    _X=_X,
                    _constant_columns=_const_cols,
                    _n_features_in=_shape[1],
                    _feature_names_in=_columns,
                    _rand_idx=_rand_idx
                )
    # END int v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v






