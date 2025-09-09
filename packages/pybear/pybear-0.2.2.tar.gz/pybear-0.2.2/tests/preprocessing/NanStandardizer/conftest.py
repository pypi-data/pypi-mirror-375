# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np



@pytest.fixture(scope='session')
def _shape():
    return (37, 13)


@pytest.fixture(scope='session')
def X_np(_shape):
    return np.random.randint(0, 10, _shape)


@pytest.fixture(scope='session')
def _X_num(_shape):

    # make sure all columns get at least one nan
    __ = np.random.randint(0, 3, _shape).astype(np.float64)
    for _c_idx in range(_shape[1]):
        _rand_r_idx = int(np.random.choice(_shape[0]))
        __[_rand_r_idx, _c_idx] = np.nan

    return __


@pytest.fixture(scope='session')
def _X_str(_shape):

    # make sure all columns get at least one nan
    __ = np.random.choice(list('abcde'), _shape, replace=True).astype('<U3')
    for _c_idx in range(_shape[1]):
        _rand_r_idx = np.random.choice(_shape[0])
        __[_rand_r_idx, _c_idx] = 'nan'

    return __