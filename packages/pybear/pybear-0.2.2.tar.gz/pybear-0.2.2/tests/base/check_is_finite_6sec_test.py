# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_is_finite import check_is_finite
from pybear.utilities._inf_masking import inf_mask
from pybear.utilities._nan_masking import nan_mask

import math
import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest


# def check_is_finite(
#     X,
#     allow_nan: bool = True,
#     allow_inf: bool = True,
#     cast_inf_to_nan: bool = True,
#     standardize_nan: bool = True,
#     copy_X: bool = True
# ) -> None:



# fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.fixture()
def _X_np_clean(_X_np):

    return _X_np


@pytest.fixture()
def _X_np_nan_and_inf(_X_factory, _shape):

    _X_np_loaded = _X_factory(
        _dupl=None,
        _constants=None,
        _format='np',
        _columns=None,
        _dtype='flt',
        _zeros=None,
        _shape=_shape,
        _has_nan=_shape[0]//5,
    )

    for c_idx in range(_shape[1]):

        r_idxs = np.random.choice(
            list(range(_shape[0])),
            _shape[0]//5,
            replace=False
        )

        values = np.random.choice(
            [np.inf, -np.inf, math.inf, -math.inf, float('inf'), float('-inf')],
            len(r_idxs),
            replace=True
        )

        _X_np_loaded[r_idxs, c_idx] = values


    #  verify this thing is loaded before sending it out
    assert np.any(nan_mask(_X_np_loaded))
    assert np.any(inf_mask(_X_np_loaded))

    return _X_np_loaded


# END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


class TestCheckIsFiniteValidation:

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # X - - - - - - - - - - - - - - - - - -
    @pytest.mark.parametrize('X_builtin', ([0,1,2], (0,1,2), {0,1,2}))
    def test_rejects_X_python_builtin(self, X_builtin):

        with pytest.raises(TypeError):
            check_is_finite(
                X_builtin,
                allow_nan=False,
                allow_inf=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                copy_X=False
            )


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csr', 'coo'))
    def test_accepts_good_X(self, _X_factory, X_format, _shape):

        good_X = _X_factory(
            _dupl=None,
            _constants=None,
            _format=X_format,
            _columns=None,
            _dtype='flt',
            _zeros=None,
            _shape=_shape,
            _has_nan=False,
        )

        out = check_is_finite(
            good_X,
            allow_nan=False,
            allow_inf=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            copy_X=False
        )

        assert isinstance(out, type(good_X))

    # END X - - - - - - - - - - - - - - - -

    @pytest.mark.parametrize('_param',
        ('allow_nan', 'allow_inf', 'cast_inf_to_nan', 'standardize_nan', 'copy_X')
    )
    @pytest.mark.parametrize('_junk',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_bool_params_junk(self, _X_np_clean, _param, _junk):

        with pytest.raises(TypeError):
            check_is_finite(
                _X_np_clean,
                allow_nan=_junk if _param == 'allow_nan' else False,
                allow_inf=_junk if _param == 'allow_inf' else False,
                cast_inf_to_nan=_junk if _param == 'cast_inf_to_nan' else False,
                standardize_nan=_junk if _param == 'standardize_nan' else False,
                copy_X=_junk if _param == 'copy_X' else False,
            )


    @pytest.mark.parametrize('_param',
        ('all_false', 'allow_nan', 'allow_inf', 'cast_inf_to_nan',
         'standardize_nan', 'copy_X')
    )
    def test_bool_params_good(self, _X_np_clean, _param):

        # this also tests:
        # if 'allow_nan' is False then 'standardize_nan' must also be False
        # if 'allow_inf' is False then 'cast_inf_to_nan' must also be False

        if _param == 'standardize_nan':
            # then standardize_nan will be True but allow_nan will be False,
            # this should raise ValueError
            with pytest.raises(ValueError):
                check_is_finite(
                    _X_np_clean,
                    allow_nan=(_param == 'allow_nan'),
                    allow_inf=(_param == 'allow_inf'),
                    cast_inf_to_nan=(_param == 'cast_inf_to_nan'),
                    standardize_nan=(_param == 'standardize_nan'),
                    copy_X=(_param == 'copy_X')
                )
        elif _param == 'cast_inf_to_nan':
            # then cast_inf_to_nan will be True but allow_inf will be False,
            # this should raise ValueError
            with pytest.raises(ValueError):
                check_is_finite(
                    _X_np_clean,
                    allow_nan=(_param == 'allow_nan'),
                    allow_inf=(_param == 'allow_inf'),
                    cast_inf_to_nan=(_param == 'cast_inf_to_nan'),
                    standardize_nan=(_param == 'standardize_nan'),
                    copy_X=(_param == 'copy_X')
                )
        else:
            out = check_is_finite(
                _X_np_clean,
                allow_nan=(_param=='allow_nan'),
                allow_inf=(_param=='allow_inf'),
                cast_inf_to_nan=(_param=='cast_inf_to_nan'),
                standardize_nan=(_param=='standardize_nan'),
                copy_X=(_param=='copy_X')
            )

            assert isinstance(out, np.ndarray)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



@pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csc', 'csr', 'dia'))
class TestCheckIsFiniteAccuracy:


    @staticmethod
    @pytest.fixture()
    def _X_loaded(_X_np_nan_and_inf, X_format):

        if X_format == 'np':
            _X_loaded = _X_np_nan_and_inf
        elif X_format == 'pd':
            _X_loaded = pd.DataFrame(_X_np_nan_and_inf)
        elif X_format == 'pl':
            _X_loaded = pl.from_numpy(_X_np_nan_and_inf)
        elif X_format == 'csr':
            _X_loaded = ss._csr.csr_array(_X_np_nan_and_inf)
        elif X_format == 'csc':
            _X_loaded = ss._csc.csc_array(_X_np_nan_and_inf)
        elif X_format == 'coo':
            _X_loaded = ss._coo.coo_array(_X_np_nan_and_inf)
        elif X_format == 'dia':
            _X_loaded = ss._dia.dia_array(_X_np_nan_and_inf)
        elif X_format == 'lil':
            _X_loaded = ss._lil.lil_array(_X_np_nan_and_inf)
        elif X_format == 'dok':
            _X_loaded = ss._dok.dok_array(_X_np_nan_and_inf)
        elif X_format == 'bsr':
            _X_loaded = ss._bsr.bsr_array(_X_np_nan_and_inf)
        else:
            raise Exception

        return _X_loaded


    @staticmethod
    @pytest.fixture()
    def _X_clean(_X_np_clean, X_format):

        if X_format == 'np':
            _X_clean = _X_np_clean
        elif X_format == 'pd':
            _X_clean = pd.DataFrame(_X_np_clean)
        elif X_format == 'pl':
            _X_clean = pl.from_numpy(_X_np_clean)
        elif X_format == 'csr':
            _X_clean = ss._csr.csr_array(_X_np_clean)
        elif X_format == 'csc':
            _X_clean = ss._csc.csc_array(_X_np_clean)
        elif X_format == 'coo':
            _X_clean = ss._coo.coo_array(_X_np_clean)
        elif X_format == 'dia':
            _X_clean = ss._dia.dia_array(_X_np_clean)
        elif X_format == 'lil':
            _X_clean = ss._lil.lil_array(_X_np_clean)
        elif X_format == 'dok':
            _X_clean = ss._dok.dok_array(_X_np_clean)
        elif X_format == 'bsr':
            _X_clean = ss._bsr.bsr_array(_X_np_clean)
        else:
            raise Exception

        return _X_clean


    # 1
    # if allowing everything and not changing anything, just return original
    def test_accuracy_1(self, _X_loaded):

        out = check_is_finite(
            _X_loaded,
            allow_nan=True,
            allow_inf=True,
            cast_inf_to_nan=False,
            standardize_nan=False,
            copy_X=True
        )

        assert isinstance(out, type(_X_loaded))

        if hasattr(_X_loaded, 'toarray'):
            _X_loaded = _X_loaded.toarray()
            out = out.toarray()
        elif isinstance(_X_loaded, (pd.DataFrame, pl.DataFrame)):
            _X_loaded = _X_loaded.to_numpy()
            out = out.to_numpy()
        elif isinstance(_X_loaded, np.ndarray):
            pass
        else:
            raise Exception

        # this has nans in it, so would need to use equal_nan=True,
        # but equal_nan is not seeing inf-like, so convert to str
        assert np.array_equal(
            out.astype(str),
            _X_loaded.astype(str)
        )


    # 2
    # if X is clean, then there is nothing to do, just return original
    @pytest.mark.parametrize('_allow_nan', (True, False))
    @pytest.mark.parametrize('_allow_inf', (True, False))
    @pytest.mark.parametrize('_cast_inf_to_nan', (True, False))
    @pytest.mark.parametrize('_standardize_nan', (True, False))
    @pytest.mark.parametrize('_copy_X', (True, False))
    def test_accuracy_2(
        self, _X_clean, _allow_nan, _allow_inf, _cast_inf_to_nan,
        _standardize_nan, _copy_X
    ):

        if _allow_nan is False and _standardize_nan is True:
            pytest.skip(reason=f"disallowed condition")

        if _allow_inf is False and _cast_inf_to_nan is True:
            pytest.skip(reason=f"disallowed condition")

        out = check_is_finite(
            _X_clean,
            allow_nan=_allow_nan,
            allow_inf=_allow_inf,
            cast_inf_to_nan=_cast_inf_to_nan,
            standardize_nan=_standardize_nan,
            copy_X=_copy_X
        )

        assert isinstance(out, type(_X_clean))

        if hasattr(_X_clean, 'toarray'):
            _X_clean = _X_clean.toarray()
            out = out.toarray()
        elif isinstance(_X_clean, (pd.DataFrame, pl.DataFrame)):
            _X_clean = _X_clean.to_numpy()
            out = out.to_numpy()
        elif isinstance(_X_clean, np.ndarray):
            pass
        else:
            raise Exception

        assert np.array_equal(out, _X_clean)


    # 3
    # if has_nan and not allow_nan:
    #     raise ValueError(f"'X' has nan-like values but are disallowed")
    @pytest.mark.parametrize('_allow_inf', (True, False))
    @pytest.mark.parametrize('_cast_inf_to_nan', (True, False))
    @pytest.mark.parametrize('_standardize_nan', (True, False))
    @pytest.mark.parametrize('_copy_X', (True, False))
    def test_accuracy_3(
        self, _X_loaded, _allow_inf, _cast_inf_to_nan, _standardize_nan,
        _copy_X
    ):

        with pytest.raises(ValueError):
            check_is_finite(
                _X_loaded,
                allow_nan=False,
                allow_inf=_allow_inf,
                cast_inf_to_nan=_cast_inf_to_nan,
                standardize_nan=_standardize_nan,
                copy_X=_copy_X
            )


    # 4
    # if has_inf and not allow_inf:
    #     raise ValueError(f"'X' has infinity-like values but are disallowed")
    @pytest.mark.parametrize('_allow_nan', (True, False))
    @pytest.mark.parametrize('_cast_inf_to_nan', (True, False))
    @pytest.mark.parametrize('_standardize_nan', (True, False))
    @pytest.mark.parametrize('_copy_X', (True, False))
    def test_accuracy_4(
        self, _X_loaded, _allow_nan, _cast_inf_to_nan, _standardize_nan,
        _copy_X
    ):

        with pytest.raises(ValueError):
            check_is_finite(
                _X_loaded,
                allow_nan=_allow_nan,
                allow_inf=False,
                cast_inf_to_nan=_cast_inf_to_nan,
                standardize_nan=_standardize_nan,
                copy_X=_copy_X
            )


    # 5
    # if has_nan and standardize_nan
    def test_accuracy_5(self, _X_loaded):

        out = check_is_finite(
            _X_loaded,
            allow_nan=True,
            allow_inf=True,
            cast_inf_to_nan=False,
            standardize_nan=True,  # <===========
            copy_X=True
        )

        assert isinstance(out, type(_X_loaded))

        if hasattr(_X_loaded, 'toarray'):
            _X_loaded = _X_loaded.toarray()
            out = out.toarray()
        elif isinstance(_X_loaded, (pd.DataFrame, pl.DataFrame)):
            _X_loaded = _X_loaded.to_numpy()
            out = out.to_numpy()
        elif isinstance(_X_loaded, np.ndarray):
            pass
        else:
            raise Exception

        NAN_MASK_IN = nan_mask(_X_loaded)
        INF_MASK_IN = inf_mask(_X_loaded)

        assert not np.array_equal(NAN_MASK_IN, INF_MASK_IN)

        NAN_MASK_OUT = nan_mask(out)

        assert np.array_equal(NAN_MASK_OUT, NAN_MASK_IN)

        outputted_nans = out[NAN_MASK_IN].ravel()

        # if all nans are set to np.nan, all of those values should be np.float64
        assert all(map(
            isinstance, outputted_nans, (np.float64 for _ in outputted_nans)
        ))
        # np.nan when converted to str should repr as 'nan'
        assert all(map(lambda x: x=='nan', list(map(str, outputted_nans))))


    # 6
    # if has_inf and cast_inf_to_nan
    def test_accuracy_6(self, _X_loaded):

        out = check_is_finite(
            _X_loaded,
            allow_nan=True,
            allow_inf=True,
            cast_inf_to_nan=True,  # <===========
            standardize_nan=False,
            copy_X=True
        )

        assert isinstance(out, type(_X_loaded))

        if hasattr(_X_loaded, 'toarray'):
            _X_loaded = _X_loaded.toarray()
            out = out.toarray()
        elif isinstance(_X_loaded, (pd.DataFrame, pl.DataFrame)):
            _X_loaded = _X_loaded.to_numpy()
            out = out.to_numpy()
        elif isinstance(_X_loaded, np.ndarray):
            pass
        else:
            raise Exception

        NAN_MASK_IN = nan_mask(_X_loaded)
        INF_MASK_IN = inf_mask(_X_loaded)

        NAN_MASK_OUT = nan_mask(out)

        assert np.array_equal(
            NAN_MASK_OUT,
            (NAN_MASK_IN + INF_MASK_IN).astype(bool)
        )

        outputted_infs = out[INF_MASK_IN].ravel()

        # if all infs are set to np.nan, all of those values should be np.float64
        assert all(map(
            isinstance, outputted_infs, (np.float64 for _ in outputted_infs)
        ))
        # np.nan when converted to str should repr as 'nan'
        assert all(map(lambda x: x=='nan', list(map(str, outputted_infs))))






