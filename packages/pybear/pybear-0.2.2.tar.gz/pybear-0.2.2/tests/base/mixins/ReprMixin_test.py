# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


from pybear.base.mixins._ReprMixin import ReprMixin
from pybear.base.mixins._GetParamsMixin import GetParamsMixin

import numpy as np

import pytest



class TestReprMixin:


    @staticmethod
    @pytest.fixture(scope='function')
    def DummyTransformer():

        class DummyTransformer(ReprMixin, GetParamsMixin):

            def __init__(self, a=1, b=2):

                self._is_fitted = False

                # these non-underscore assignments must be here for
                # __repr__ to find them
                self.a = a
                self.b = b

            def reset(self):
                try:
                    delattr(self, '_random_fill')
                except:
                    pass

                self._is_fitted = False

            def partial_fit(self, X, y=None):

                self._is_fitted = True

                return self


            def fit(self, X, y=None):
                self.reset()
                return self.partial_fit(X, y)


            def transform(self, X):

                assert self._is_fitted

                return np.full(X.shape, np.e)


        return DummyTransformer  # <====== not initialized



    def test_repr_mixin(self, DummyTransformer):

        a = 12
        b = 24

        cls = DummyTransformer(a=a, b=b)

        X = np.random.randint(0, 10, (20, 13))

        out = str(cls.fit(X))
        exp = f"DummyTransformer(a={a}, b={b})"

        assert out == exp




















