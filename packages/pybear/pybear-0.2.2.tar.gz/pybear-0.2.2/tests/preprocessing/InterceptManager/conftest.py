# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np



@pytest.fixture(scope='module')
def _shape():
    return (20, 10)


@pytest.fixture(scope='module')
def _constants(_shape):
    _rand_idxs = np.random.choice(range(_shape[1]), 3, replace=False).tolist()
    _values = [0, np.nan, 1]
    return dict((zip(_rand_idxs, _values)))


@pytest.fixture(scope='module')
def X_np(_X_factory, _constants, _shape):
    return _X_factory(
        _has_nan=False,
        _dtype='flt',
        _constants=_constants,
        _shape=_shape
    )


@pytest.fixture(scope='module')
def y_np(_shape):
    return np.random.randint(0, 2, _shape[0])


@pytest.fixture(scope='function')
def _kwargs():
    return {
        'keep': 'first',
        'equal_nan': False,   # must be False
        'rtol': 1e-5,
        'atol': 1e-8
    }



