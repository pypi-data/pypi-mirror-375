# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np

from sklearn.model_selection import KFold as sk_KFold

from pybear.model_selection.GSTCV._GSTCVMixin._validation._cv import _val_cv



class TestValCV:


    @pytest.mark.parametrize('junk_cv',
        (2.718, 3.1416, True, False, 'trash', min, {'a': 1}, lambda x: x)
    )
    def test_rejects_not_None_iter_int(self, junk_cv):
        with pytest.raises(TypeError):
            _val_cv(junk_cv)


    @pytest.mark.parametrize('bad_cv', (-1, 0, 1))
    def test_value_error_int_less_than_2(self, bad_cv):
        with pytest.raises(ValueError):
            _val_cv(bad_cv, _can_be_int=True)

    # rejects ^ ^ ^ ^
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # accepts v v v v

    @pytest.mark.parametrize('None_or_int', (None, 2,3,4,5))
    @pytest.mark.parametrize('_can_be_None', (True, False))
    @pytest.mark.parametrize('_can_be_int', (True, False))
    def test_None_and_good_int(
        self, None_or_int, _can_be_None, _can_be_int
    ):

        if isinstance(None_or_int, numbers.Integral) and not _can_be_int:
            with pytest.raises(TypeError):
                _val_cv(
                    None_or_int,
                    _can_be_None=_can_be_None,
                    _can_be_int=_can_be_int
                )
        elif None_or_int is None and not _can_be_None:
            with pytest.raises(TypeError):
                _val_cv(
                    None_or_int,
                    _can_be_None=_can_be_None,
                    _can_be_int=_can_be_int
                )
        else:
            assert _val_cv(
                    None_or_int,
                    _can_be_None=_can_be_None,
                    _can_be_int=_can_be_int
            ) is None


    @pytest.mark.parametrize('_n_splits', (3,4,5))
    @pytest.mark.parametrize('_container', (tuple, list, np.ndarray))
    def test_accepts_good_sk_iter(self, _n_splits, _container, X_np, y_np):

        good_iter = sk_KFold(n_splits=_n_splits).split(X_np, y_np)

        if _container in [tuple, list]:
            good_iter2 = _container(map(
                tuple,
                sk_KFold(n_splits=_n_splits).split(X_np,y_np)
            ))
        elif _container is np.ndarray:
            good_iter2 = np.array(
                list(map(
                    tuple,
                    sk_KFold(n_splits=_n_splits).split(X_np,y_np)
                )),
                dtype=object
            )
        else:
            raise Exception


        assert _val_cv(good_iter) is None
        assert _val_cv(good_iter2) is None



