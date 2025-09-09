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


@pytest.fixture(scope='module')
def X_np(_shape):
    return np.random.randint(0, 10, _shape).astype(np.float64)










