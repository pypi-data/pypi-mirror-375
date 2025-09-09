# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.base.mixins._SetParamsMixin import SetParamsMixin
from pybear.base.mixins._GetParamsMixin import GetParamsMixin



@pytest.fixture(scope='function')
def DummyEstimator():

    class Foo(SetParamsMixin, GetParamsMixin):

        def __init__(
            self,
            bananas=True,
            fries='yes',
            ethanol=1,
            apples=[0,1]
        ):

            self._is_fitted = False   # <===== leading under
            self.dum_attr_ = 1  # <===== trailing under
            self.bananas = bananas
            self.fries = fries
            self.ethanol = ethanol
            self.apples = apples


        def reset(self):

            self._is_fitted = False


        def fit(self, X, y=None):
            self.reset()
            self._is_fitted = True   # <===== leading under
            return self


        def score(self, X, y=None):
            return np.random.uniform(0, 1)


        def predict(self, X):

            assert self._is_fitted

            return np.random.randint(0, 2, X.shape[0])


    return Foo  # <====== not initialized


@pytest.fixture(scope='function')
def DummyTransformer():

    class Bar(SetParamsMixin, GetParamsMixin):

        def __init__(
            self,
            tbone=False,
            wings='yes',
            bacon=0,
            sausage=[4, 4],
            hambone=False
        ):

            self._is_fitted = False   #  <==== leading under
            self.this_attr_ = 1  # <====== tralling under
            self.tbone = tbone
            self.wings = wings
            self.bacon = bacon
            self.sausage = sausage
            self.hambone = hambone


        def reset(self):
            try:
                delattr(self, '_fill_value')
            except:
                pass
            self._is_fitted = False


        def fit(self, X):
            self.reset()
            self._fill_value = np.random.uniform(0, 1)
            self._is_fitted = True
            return self


        def transform(self, X):

            assert self._is_fitted

            return np.full(X.shape, self._fill_value)


        def fit_transform(self, X):
            return self.fit(X).transform(X)


    return Bar  # <====== not initialized


@pytest.fixture(scope='function')
def DummyGridSearch():

    class Baz(SetParamsMixin, GetParamsMixin):

        def __init__(
            self,
            estimator,
            param_grid,
            *,
            scoring='balanced_accuracy',
            refit=False
        ):
            self._is_fitted = False   #  <==== leading under
            self.some_attr_ = 1    # <====== tralling under
            self.estimator = estimator
            self.param_grid = param_grid
            self.scoring = scoring
            self.refit = refit


        def reset(self):
            self._is_fitted = False


        def fit(self, X, y=None):

            self.reset()

            self.best_params_ = {}

            for _param in self.param_grid:
                self.best_params_[_param] = \
                    np.random.choice(self.param_grid[_param])

            self._is_fitted = True


        def score(self, X, y):
            return np.random.uniform(0, 1)


    return Baz  # <====== not initialized






