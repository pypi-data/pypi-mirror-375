# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base.mixins._FitTransformMixin import FitTransformMixin


import numpy as np

import pytest



class TestFitTransformMixin:

    # only test that the mixin works here.


    @staticmethod
    @pytest.fixture(scope='function')
    def DummyTransformer():


        class DummyTransformer(FitTransformMixin):

            def __init__(self):
                self.is_fitted = False

            def fit(self, X, y=None, adder: bool = False):
                self.fill_value = np.random.uniform(0, 1)
                if adder:
                    self.fill_value += 1
                if y is not None:
                    self.fill_value += 10
                self.is_fitted = True
                return self

            def transform(self, X):
                assert self.is_fitted
                return np.full(X.shape, self.fill_value)


        return DummyTransformer()  # <====== initialize here!



    @pytest.mark.parametrize('arity', (1, 2))
    @pytest.mark.parametrize('_fit_params_is_passed', (True, False))
    def test_fit_transform_mixin(
        self, _shape, DummyTransformer, arity, _fit_params_is_passed
    ):

        if _fit_params_is_passed:
            fit_params = {'adder': True}
        else:
            fit_params = {}


        # notice that the expected output values vary based on whether
        # y was passed and fit_params were used.
        # this enables to verify that things are being passed correctly.

        X = np.random.randint(0, 10, _shape)

        if arity == 1:

            out = DummyTransformer.fit_transform(X, **fit_params)

            assert isinstance(out, np.ndarray)
            assert out.shape == _shape

            # y is not passed, so values arent shifted for that
            if _fit_params_is_passed:
                assert np.min(out) >= 1 and np.max(out) <= 2
            elif not _fit_params_is_passed:
                assert np.min(out) >= 0 and np.max(out) <= 1

        elif arity == 2:
            y = np.random.randint(0, 2, _shape[0])

            out = DummyTransformer.fit_transform(X, y, **fit_params)

            assert isinstance(out, np.ndarray)
            assert out.shape == _shape

            # y is passed, so values are shifted!
            if _fit_params_is_passed:
                assert np.min(out) >= 11 and np.max(out) <= 12
            elif not _fit_params_is_passed:
                assert np.min(out) >= 10 and np.max(out) <= 11





