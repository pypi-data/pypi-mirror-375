# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base.mixins._FeatureMixin import FeatureMixin
from pybear.base.exceptions import NotFittedError

import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest



class TestFeatureMixin:


    # the workhorses of this mixin are
    # pybear.base.check_n_features()
    # pybear.base.check_feature_names()
    # pybear.base.get_feature_names_out().
    # those modules are tested in
    # check_n_features_test
    # check_feature_names_test
    # get_feature_names_out_test.
    # only test that the mixin works here.


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_pd(_X_np, _columns):
        return pd.DataFrame(data=_X_np, columns=_columns)


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_pl(_X_np, _columns):
        return pl.DataFrame(data=_X_np, schema=list(_columns))


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_csr(_X_np, _columns):
        return ss.csr_array(_X_np)


    @staticmethod
    @pytest.fixture(scope='function')
    def DummyTransformer():

        class DummyTransformer(FeatureMixin):

            # FeatureMixin should provide
            # get_feature_names_out(input_features)
            # _check_n_features(X, self.n_features_in, reset)
            # _check_feature_names(X, reset)

            # feature axis of X is not altered during transform

            def __init__(self):
                self._is_fitted = False

            def reset(self):
                try:
                    delattr(self, '_random_fill')
                except:
                    pass

                self._is_fitted = False

            def partial_fit(self, X, y=None):

                self._check_n_features(
                    X,
                    reset=not hasattr(self, '_random_fill')
                )

                self._check_feature_names(
                    X,
                    reset=not hasattr(self, '_random_fill')
                )

                self._random_fill = np.random.uniform(0, 1)

                self._is_fitted = True

                return self


            def fit(self, X, y=None):
                self.reset()
                return self.partial_fit(X, y)


            def transform(self, X):

                assert self._is_fitted

                # X must have same n_features as at fit for get_feature_names_out()
                assert X.shape[1] == self.n_features_in

                return np.full(X.shape, self._random_fill)


        return DummyTransformer  # <====== not initialized


    @pytest.mark.parametrize('_input_features_is_passed',
        ('true_valid', 'true_invalid', 'false')
    )
    @pytest.mark.parametrize('_feature_names_are_passed', (True, False))
    @pytest.mark.parametrize('_format', ('pd', 'pl'))
    def test_gfno(
        self, _shape, _columns, _X_np, _X_pd, _X_pl, DummyTransformer,
        _input_features_is_passed, _feature_names_are_passed, _format
    ):

        if _input_features_is_passed == 'true_valid':
            _input_features = _columns.copy()
        elif _input_features_is_passed == 'true_invalid':
            _input_features = [str(uuid.uuid4)[:5] for _ in range(_shape[1])]
        elif _input_features_is_passed == 'false':
            _input_features = None
        else:
            raise Exception

        if _feature_names_are_passed:
            _X_wip = _X_pd if _format == 'pd' else _X_pl if _format == 'pl' else None
        else:
            if _format == 'pd':
                _X_wip = pd.DataFrame(data=_X_np, columns=None)
            elif _format == 'pl':
                _X_wip = pl.from_numpy(_X_np)


        TestClass = DummyTransformer()

        # excepts when not fitted yet
        with pytest.raises(NotFittedError):
            TestClass.get_feature_names_out(input_features=_input_features)

        TestClass.fit(_X_wip)

        if _feature_names_are_passed:
            if _input_features_is_passed == 'true_invalid':
                # should raise an exception after fit if invalid feature names
                # are passed to input_features when first fit saw feature names
                with pytest.raises(ValueError):
                    TestClass.get_feature_names_out(input_features=_input_features)
                pytest.skip(reason=f"cant do anymore tests after exception")
            else:
                out = TestClass.get_feature_names_out(input_features=_input_features)
        elif not _feature_names_are_passed:
            # polars always has str header, and the only thing that should pass
            # is if input_features is not passed
            if _format == 'pl' and _input_features_is_passed != 'false':
                with pytest.raises(ValueError):
                    TestClass.get_feature_names_out(input_features=_input_features)
                pytest.skip(reason=f"cant do anymore tests after exception")
            else:   # _format is pd, can pass anything if didnt have a header
                out = TestClass.get_feature_names_out(input_features=_input_features)

        assert isinstance(out, np.ndarray)
        assert out.dtype == object

        if _feature_names_are_passed:
            if _input_features_is_passed == 'true_valid':
                assert np.array_equal(out, _columns)
            elif _input_features_is_passed == 'false':
                assert np.array_equal(out, _columns)
        elif not _feature_names_are_passed:
            if _input_features_is_passed == 'true_valid':
                assert np.array_equal(out, _columns)
            elif _input_features_is_passed == 'true_invalid':
                assert np.array_equal(out, _input_features)
            elif _input_features_is_passed == 'false':
                if _format == 'pd':
                    boilerplate = [f'x{i}' for i in range(_shape[1])]
                elif _format == 'pl':
                    boilerplate = [f'column_{i}' for i in range(_shape[1])]
                else:
                    raise Exception
                ref = np.array(boilerplate, dtype=object)
                assert np.array_equal(out, ref)


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csr'))
    def test_n_features_in_(
        self, DummyTransformer, X_format, _X_np, _X_pd, _X_pl, _X_csr, _shape
    ):

        TestClass = DummyTransformer()

        # excepts when not fitted yet
        with pytest.raises(AttributeError):
            getattr(TestClass, 'n_features_in_')

        if X_format == 'np':
            TestClass.fit(_X_np)
        elif X_format == 'pd':
            TestClass.fit(_X_pd)
        elif X_format == 'pl':
            TestClass.fit(_X_pl)
        elif X_format == 'csr':
            TestClass.fit(_X_csr)
        else:
            raise Exception

        # n_features_in_ should always be exposed no matter what valid container
        assert getattr(TestClass, 'n_features_in_') == _shape[1]


    @pytest.mark.parametrize('X_format',
        ('np', 'pd_w_header', 'pd_no_header', 'pl_w_header', 'pl_no_header', 'csr')
    )
    def test_features_names_in_(
        self, DummyTransformer, X_format, _X_np, _X_pd, _X_pl, _X_csr, _columns
    ):

        TestClass = DummyTransformer()

        # excepts when not fitted yet
        with pytest.raises(AttributeError):
            getattr(TestClass, 'feature_names_in_')

        if X_format == 'np':
            TestClass.fit(_X_np)
        elif X_format == 'pd_w_header':
            TestClass.fit(_X_pd)
        elif X_format == 'pd_no_header':
            TestClass.fit(pd.DataFrame(data=_X_np))
        elif X_format == 'pl_w_header':
            TestClass.fit(_X_pl)
        elif X_format == 'pl_no_header':
            TestClass.fit(pl.from_numpy(_X_np))
        elif X_format == 'csr':
            TestClass.fit(_X_csr)
        else:
            raise Exception

        # feature_names_in_ should only be exposed for container with valid header
        if X_format in ['pd_w_header', 'pl_w_header', 'pl_no_header']:
            out = getattr(TestClass, 'feature_names_in_')
            assert isinstance(out, np.ndarray)
            assert out.dtype == object
            if X_format == 'pl_no_header':
                _exp_out = [f'column_{i}' for i in range(len(_columns))]
                assert np.array_equal(out, _exp_out)
            else:
                assert np.array_equal(out, _columns)
        else:
            with pytest.raises(AttributeError):
                getattr(TestClass, 'feature_names_in_')




