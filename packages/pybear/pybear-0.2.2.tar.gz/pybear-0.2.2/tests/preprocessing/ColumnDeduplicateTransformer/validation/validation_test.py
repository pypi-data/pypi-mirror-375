# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._ColumnDeduplicator._validation._validation \
    import _validation



class TestValidation:


    @pytest.mark.parametrize('_conflict', ('raise', 'ignore'))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    @pytest.mark.parametrize('_rtol', (1e-6, 1e-1))
    @pytest.mark.parametrize('_atol', (1e-6, 1))
    @pytest.mark.parametrize('_equal_nan', (True, False))
    @pytest.mark.parametrize('_n_jobs', (None, -1, 1))
    @pytest.mark.parametrize('_job_size', (3, 15))
    def test_accepts_good(
        self, _X_factory, _columns, _conflict, _keep, _rtol, _atol,
        _equal_nan, _n_jobs, _job_size, _shape
    ):

        _validation(
            _X=_X_factory(_format='np', _shape=_shape),
            _columns=_columns,
            _conflict=_conflict,
            _do_not_drop=list(
                np.random.choice(range(_shape[1]), _shape[1]//10, replace=False)
            ),
            _keep=_keep,
            _rtol=_rtol,
            _atol=_atol,
            _equal_nan=_equal_nan,
            _n_jobs=_n_jobs,
            _job_size=_job_size
        )





