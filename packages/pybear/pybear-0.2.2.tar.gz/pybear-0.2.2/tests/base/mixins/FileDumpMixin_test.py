# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence
)

import io
import glob
import os
import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest
from unittest.mock import patch

from pybear.base.mixins._FileDumpMixin import FileDumpMixin
from pybear.base.mixins._FitTransformMixin import FitTransformMixin
from pybear.base.mixins._FeatureMixin import FeatureMixin



class TestFileDumpMixin:


    # fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    @staticmethod
    @pytest.fixture(scope='function')
    def _ClsTemplate():

        class Cls(FeatureMixin, FitTransformMixin):


            def __init__(self, fill:bool=True):

                self._is_fitted = False
                self.fill = fill


            def __pybear_is_fitted__(self):
                return getattr(self, '_is_fitted', None) is True


            def reset(self):
                self._is_fitted = False

                return self


            def _validate(self, OBJ, name):
                if not isinstance(
                    OBJ, (Sequence, set, np.ndarray, pd.DataFrame, pl.DataFrame)
                ) and not hasattr(OBJ, 'toarray'):

                    raise TypeError(
                        f"'{name}' must be a python built-in, numpy array, pandas "
                        f"series/dataframe, or polars series/dataframe."
                    )


            def fit(self, X, y=None):

                self._validate(X, 'X')
                if y is not None:
                    self._validate(y, 'y')

                self.n_features_in_ = X.shape[1]

                if hasattr(X, 'columns'):
                    self.feature_names_in_ = np.array(X.columns, dtype=object)

                self.fill_value = np.random.randint(1, 10)

                self._is_fitted = True

                return self


            def transform(self, X):

                return np.full(X.shape if hasattr(X, 'shape') else (5,5), self.fill)


        return Cls


    @staticmethod
    @pytest.fixture(scope='function')
    def MockTransformer(_ClsTemplate):

        class Foo(_ClsTemplate, FileDumpMixin):

            pass

        return Foo


    @staticmethod
    @pytest.fixture(scope='module')
    def _dum_X(_shape):
        return np.random.choice(list('abcdefghi'), _shape)


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_factory(_shape):

        def foo(
            _dim: Literal[1, 2],
            _dtype: Literal['str', 'num'],
            _format: Literal['list', 'tuple', 'set', 'np', 'pd', 'pl']
        ):

            assert _dim in [1, 2]

            if _dim == 2 and _format == 'set':
                raise Exception(f"cant have 2D sets")

            if _dtype == 'str':
                _data = np.random.choice(list('abcdefghijklm'), _shape)
            elif _dtype == 'num':
                _data = np.random.randint(0, 10, _shape)
            else:
                raise Exception

            if _format == 'list':
                if _dim == 1:
                    return list(_data[:, 0])
                elif _dim == 2:
                    return list(map(list, _data))
            elif _format == 'tuple':
                if _dim == 1:
                    return tuple(_data[:, 0])
                elif _dim == 2:
                    return tuple(map(tuple, _data))
            elif _format == 'set':
                if _dim == 1:
                    return set(list(_data[:, 0]))
                elif _dim == 2:
                    raise Exception(f"should have been blocked above")
            elif _format == 'np':
                if _dim == 1:
                    return _data[:, 0]
                elif _dim == 2:
                    return _data
            elif _format == 'pd':
                __ = pd.DataFrame(
                    _data,
                    columns=[str(uuid.uuid4())[:5] for _ in range(_shape[1])]
                )
                if _dim == 1:
                    return __.iloc[:, 0].squeeze()
                elif _dim == 2:
                    return __
            elif _format == 'pl':
                if _dim == 1:
                    return pl.Series(_data[:, 0])
                elif _dim == 2:
                    return pl.DataFrame(
                        _data,
                        schema=[str(uuid.uuid4())[:5] for _ in range(_shape[1])]
                    )
            else:
                raise Exception


        return foo

    # END fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    # X validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # since both dump_to_csv & dump_to_txt are nested in the same decorator,
    # and the decorator has the validation, only need to test one.

    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', {'a':1}, lambda x: x)
    )
    def test_rejects_junk_X(self, junk_X, MockTransformer, _dum_X):

        trfm = MockTransformer().fit(_dum_X)
        with pytest.raises(TypeError):
            trfm.dump_to_csv(junk_X)


    @pytest.mark.parametrize('bad_X', ('csr', 'csc'))
    def test_rejects_bad_X(self, bad_X, MockTransformer, _shape):

        _X_np = np.random.randint(0, 10, _shape)

        if bad_X == 'csr':
            bad_X = ss.csr_array(_X_np)
        elif bad_X == 'csc':
            bad_X = ss.csc_matrix(_X_np)
        else:
            raise Exception

        trfm = MockTransformer().fit(_X_np)
        with pytest.raises(TypeError):
            trfm.dump_to_csv(bad_X)


    @pytest.mark.parametrize('dim', (1,2))
    @pytest.mark.parametrize('format', ('list', 'tuple', 'set', 'np', 'pd', 'pl'))
    def test_rejects_num(
        self, _X_factory, MockTransformer, _dum_X, format, dim
    ):

        # cant take numeric

        if format == 'set' and dim == 2:
            pytest.skip(reason=f"set cant be 2D")


        bad_X = _X_factory(_dim=dim, _dtype='num', _format=format)

        trfm = MockTransformer().fit(_dum_X)
        with pytest.raises(ValueError):
            trfm.dump_to_csv(bad_X)

    # END X validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_format', ('list', 'tuple', 'set', 'np', 'pd', 'pl'))
    def test_accuracy_dump_to_csv(
        self, _X_factory, MockTransformer, _dum_X, _dim, _format
    ):

        if _format == 'set' and _dim == 2:
            pytest.skip(reason=f"cant have 2D sets")

        _X = _X_factory(_dim=_dim, _dtype='str', _format=_format)

        if _dim == 2:
            if isinstance(_X, pd.DataFrame):
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X.values)))
            elif isinstance(_X, pl.DataFrame):
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X.rows())))
            else:
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X)))
        else:
            ref_X = list(map(str, _X))

        # transformer 1 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        trfm1 = MockTransformer().fit(_dum_X)

        user_inputs = f"testfile_{_format}\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            trfm1.dump_to_csv(_X)

        _files = glob.glob(os.path.join(os.curdir, "*.*"))
        assert any(map(lambda x: f"testfile_{_format}.csv" in x, _files))
        del _files

        try:
            df = pd.read_csv(f'testfile_{_format}.csv')
            assert df.shape[0] == len(_X)
            for _idx, _line in enumerate(df.squeeze()):
                assert _line == ref_X[_idx]
            os.remove(f'testfile_{_format}.csv')
        except Exception as e:
            os.remove(f'testfile_{_format}.csv')
            raise e

        _files = glob.glob(os.path.join(os.curdir, "*.*"))
        assert not any(map(lambda x: f"testfile_{_format}.csv" in x, _files))
        del _files


    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_format', ('list', 'tuple', 'set', 'np', 'pd', 'pl'))
    def test_accuracy_dump_to_txt(
        self, _X_factory, MockTransformer, _dum_X, _dim, _format
    ):

        if _format == 'set' and _dim == 2:
            pytest.skip(reason=f"cant have 2D sets")

        _X = _X_factory(_dim=_dim, _dtype='str', _format=_format)

        if _dim == 2:
            if isinstance(_X, pd.DataFrame):
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X.values)))
            elif isinstance(_X, pl.DataFrame):
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X.rows())))
            else:
                ref_X = list(map(" ".join, map(lambda x: map(str, x), _X)))
        else:
            ref_X = list(map(str, _X))

        # transformer 1 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        trfm1 = MockTransformer().fit(_dum_X)

        user_inputs = f"testfile_{_format}\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            trfm1.dump_to_txt(_X)

        _files = glob.glob(os.path.join(os.curdir, "*.*"))
        assert any(map(lambda x: f"testfile_{_format}.txt" in x, _files))
        del _files

        try:
            with open(f"testfile_{_format}.txt", 'r') as f:
                _text = []
                for line in f:
                    _text.append(line)
                f.close()

                assert len(_text) == len(_X)
                for _idx, _line in enumerate(_text):
                    assert _line == f"{ref_X[_idx]}\n"
                os.remove(f'testfile_{_format}.txt')
        except Exception as e:
            os.remove(f'testfile_{_format}.txt')
            raise e

        _files = glob.glob(os.path.join(os.curdir, "*.*"))
        assert not any(map(lambda x: f"testfile_{_format}.txt" in x, _files))
        del _files





