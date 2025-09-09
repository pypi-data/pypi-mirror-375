# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing.__shared._validation. _n_jobs import _val_n_jobs



class TestValNJobs:


    @pytest.mark.parametrize('_n_jobs',
        (-2.718, 3.141, True, False, 'junk', [1], (1,), {1, 2}, {'a':1},
         lambda x: x)
    )
    def test_typeerror_junk_n_jobs(self, _n_jobs):
        with pytest.raises(TypeError):
            _val_n_jobs(_n_jobs)


    @pytest.mark.parametrize('_n_jobs', (-2, 0))
    def test_valueerror_n_jobs(self, _n_jobs):
        with pytest.raises(ValueError):
            _val_n_jobs(_n_jobs)


    @pytest.mark.parametrize('_n_jobs', (None, -1, 1, 4))
    def test_accepts_good_n_jobs(self, _n_jobs):
        assert _val_n_jobs(_n_jobs) is None





