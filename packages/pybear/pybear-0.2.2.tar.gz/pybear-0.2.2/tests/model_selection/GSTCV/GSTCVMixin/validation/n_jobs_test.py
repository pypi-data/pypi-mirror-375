# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCVMixin._validation._n_jobs import \
    _val_n_jobs



class TestNJobs:


    @pytest.mark.parametrize('junk_njobs',
        (float('inf'), True, False, 'trash', min, [0,1], (0,1), {0,1},
         {'a':1}, lambda x: x)
    )
    def test_rejects_non_int_non_None(self, junk_njobs):

        with pytest.raises(TypeError):
            _val_n_jobs(junk_njobs)


    @pytest.mark.parametrize('bad_njobs', (-2, 0, 3.14))
    def test_rejects_bad_int(self, bad_njobs):

        with pytest.raises(ValueError):
            _val_n_jobs(bad_njobs)


    @pytest.mark.parametrize('good_njobs', (None, -1, 1, 5, 10))
    def test_good_returns_None(self, good_njobs):
        assert _val_n_jobs(good_njobs) is None





