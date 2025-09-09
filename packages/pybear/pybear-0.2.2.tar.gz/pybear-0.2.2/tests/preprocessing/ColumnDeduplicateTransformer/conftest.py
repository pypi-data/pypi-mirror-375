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
def _dupls(_shape):
    # _dupl must be intermingled like [[0,8],[1,9]], not [[0,1],[8,9]]
    # for TestManyPartialFitsEqualOneBigFit to catch 'random' putting
    # out different columns over a sequence of transforms

    while True:
        _dupls1 = np.random.choice(range(_shape[1]), (2,))
        _dupls2 = np.random.choice(range(_shape[1]), (2,))
        _ctr = 0
        _ctr += _dupls1[0] < _dupls1[1]
        _ctr += _dupls1[0] < _dupls2[0]
        _ctr += _dupls1[1] < _dupls2[1]
        _ctr += _dupls2[0] < _dupls2[1]
        if _ctr == 4:
            return [list(map(int, _dupls1)), list(map(int, _dupls2))]


@pytest.fixture(scope='module')
def X_np(_X_factory, _dupls, _shape):
    return _X_factory(
        _dupl=_dupls,
        _has_nan=False,
        _dtype='flt',
        _shape=_shape
    )


@pytest.fixture(scope='module')
def y_np(_shape):
    return np.random.randint(0, 2, _shape[0])


@pytest.fixture(scope='function')
def _kwargs():
    return {
        'keep': 'first',
        'do_not_drop': None,
        'conflict': 'raise',
        'rtol': 1e-5,
        'atol': 1e-8,
        'equal_nan': False,
        'n_jobs': 1,     # leave set at 1 because of confliction
        'job_size': 20
    }




