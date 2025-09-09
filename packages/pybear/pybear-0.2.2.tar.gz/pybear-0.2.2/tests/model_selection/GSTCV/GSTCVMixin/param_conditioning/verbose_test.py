# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._verbose \
    import _cond_verbose



class TestCondVerbose:


    @pytest.mark.parametrize('_bool', (True, False))
    def test_bools(self, _bool):

        _og_bool = deepcopy(_bool)

        if _bool is True:
            assert _cond_verbose(_bool) == 10
        elif _bool is False:
            assert _cond_verbose(_bool) == 0

        assert _bool is _og_bool


    def test_floats(self):
        assert _cond_verbose(0.124334) == 0
        assert _cond_verbose(3.14) == 3

        _verbose = 8.8888
        _og_verbose = deepcopy(_verbose)
        assert _cond_verbose(_verbose) == 9
        assert _verbose == _og_verbose


    @pytest.mark.parametrize('good_int', (0, 1, 5, 200))
    def test_ints(self, good_int):

        _og_good_int = deepcopy(good_int)
        assert _cond_verbose(good_int) == min(good_int, 10)
        assert good_int == _og_good_int




