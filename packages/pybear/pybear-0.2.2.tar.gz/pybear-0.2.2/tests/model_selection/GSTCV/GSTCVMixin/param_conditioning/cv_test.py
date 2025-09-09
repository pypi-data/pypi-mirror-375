# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import inspect

import numpy as np

from sklearn.model_selection import KFold as sk_KFold

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._cv \
    import _cond_cv



class TestCondCV:


    def test_None_returns_default(self):
        _cv = None
        _og_cv = deepcopy(_cv)
        out = _cond_cv(_cv)
        assert isinstance(out, int)
        assert out == 5
        assert _cv is _og_cv


    @pytest.mark.parametrize(f'good_int', (2,3,4,5))
    def test_good_int(self, good_int):

        _og_good_int = deepcopy(good_int)
        out = _cond_cv(good_int)
        assert isinstance(out, int)
        assert out == good_int
        assert good_int == _og_good_int


    @pytest.mark.parametrize(f'junk_iter',
        ([1,2,3], [[1,2,3], [1,2,3], [2,3,4]], (True, False), list('abcde'))
    )
    def test_rejects_junk_iter(self, junk_iter):
        with pytest.raises((TypeError, ValueError)):
            _cond_cv(junk_iter)


    def test_rejects_empties(self):

        with pytest.raises(ValueError):
            _cond_cv([()])


        with pytest.raises(ValueError):
            _cond_cv((_ for _ in range(0)))


    def test_accepts_good_sk_iter(self, standard_cv_int, X_np, y_np):

        good_iter = sk_KFold(n_splits=standard_cv_int).split(X_np, y_np)
        # TypeError: cannot pickle 'generator' object
        ref_iter = sk_KFold(n_splits=standard_cv_int).split(X_np, y_np)

        out = _cond_cv(good_iter)
        assert isinstance(out, list)
        assert inspect.isgenerator(good_iter)

        assert inspect.isgenerator(ref_iter)
        ref_iter_as_list = list(ref_iter)
        assert isinstance(ref_iter_as_list, list)

        for idx in range(standard_cv_int):
            for X_y_idx in range(2):
                assert np.array_equiv(
                    out[idx][X_y_idx],
                    ref_iter_as_list[idx][X_y_idx]
                )



