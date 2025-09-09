# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import itertools
import numbers

import numpy as np

from sklearn.preprocessing import OneHotEncoder

from pybear.preprocessing._SlimPolyFeatures._partial_fit.\
    _get_dupls_for_combo_in_X_and_poly import _get_dupls_for_combo_in_X_and_poly



class Fixtures:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @staticmethod
    @pytest.fixture(scope='module')
    def _gdfc_args():

        _args = {
            '_equal_nan': True,
            '_rtol': 1e-5,
            '_atol': 1e-8,
            '_n_jobs': 1,  # leave this at 1 because of contention
            '_job_size': 20
        }

        return _args


    @staticmethod
    @pytest.fixture(scope='module')
    def _combos(_shape):
        return list(itertools.combinations_with_replacement(range(_shape[1]), 2))

    # # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


class TestDuplsForComboValidation(Fixtures):


    # _X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('junk_X',
        (-np.e, -1, 0, 1, np.e, True, False, 'trash', [0,1], (0,1), lambda x: x)
    )
    def test_X_rejects_junk(self, junk_X, _combos, _gdfc_args):

        with pytest.raises(AssertionError):
            _get_dupls_for_combo_in_X_and_poly(
                _X=junk_X,
                _poly_combos=_combos,
                _min_degree=1,
                **_gdfc_args
            )


    @pytest.mark.parametrize('_format',
        ('coo_matrix', 'coo_array', 'dia_matrix',
         'dia_array', 'bsr_matrix', 'bsr_array')
    )
    def test_X_rejects_bad(self, _X_factory, _shape, _combos, _gdfc_args, _format):

        _bad_X = _X_factory(
            _format=_format,
            _shape=_shape
        )

        with pytest.raises(AssertionError):
            _get_dupls_for_combo_in_X_and_poly(
                _X=_bad_X,
                _poly_combos=_combos,
                _min_degree=1,
                **_gdfc_args
            )

    # END _X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # _poly_combos ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('junk_poly_combos',
        (-np.e, -1, 0, 1, np.e, True, False, None, lambda x: x)
    )
    def test_poly_combos_rejects_junk(self, X_np, junk_poly_combos, _gdfc_args):

        with pytest.raises(AssertionError):
            _get_dupls_for_combo_in_X_and_poly(
                _X=X_np,
                _poly_combos=junk_poly_combos,
                _min_degree=1,
                **_gdfc_args
            )

    # END _poly_combos ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # other kwargs  ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('_equal_nan',(1 ,None,'trash', True, False))
    @pytest.mark.parametrize('_rtol', (None, -np.e, -1, True, False))
    @pytest.mark.parametrize('_atol', (None, -np.e, -1, True, False))
    @pytest.mark.parametrize('_n_jobs', (True, False, 'trash', -2, 0, -1, 1))
    @pytest.mark.parametrize('_job_size', (True, False, 'trash', -2, 0, -1, 1))
    def test_rejects_junk(
        self, X_np, _combos, _equal_nan, _rtol, _atol, _n_jobs, _job_size
    ):

        _will_raise = 0
        if not isinstance(_equal_nan, bool):
            _will_raise += 1
        if not isinstance(_rtol, numbers.Real) or _rtol < 0 or _rtol in [True, False]:
            _will_raise += 1
        if not isinstance(_atol, numbers.Real) or _atol < 0 or _atol in [True, False]:
            _will_raise += 1
        if _n_jobs is not None:
            if not isinstance(_n_jobs, numbers.Integral) or _n_jobs < -1:
                _will_raise += 1

        kwargs = {
            '_equal_nan': _equal_nan, '_rtol': _rtol,
            '_atol': _atol, '_n_jobs': _n_jobs, '_job_size': _job_size
        }

        if not _will_raise:
            assert _get_dupls_for_combo_in_X_and_poly(
                X_np,
                _combos,
                _min_degree=1,
                **kwargs
            ) is None
        else:
            with pytest.raises(AssertionError):
                _get_dupls_for_combo_in_X_and_poly(
                    X_np,
                    _combos,
                    _min_degree=1,
                    **kwargs
                )

    # END other kwargs  ** * ** * ** * ** * ** * ** * ** * ** * ** * **


class TestGetDuplsForComboAccuracy(Fixtures):


    def test_accuracy_no_dupls(
        self, _X_factory, _shape, _combos, _gdfc_args
    ):

        # something with no dupls in it
        _X_wip = _X_factory(
            _format='np',
            _dtype='flt',
            _shape=_shape
        )

        out = _get_dupls_for_combo_in_X_and_poly(
            _X_wip,
            _combos,
            _min_degree=1,
            **_gdfc_args
        )

        assert isinstance(out, list)
        assert len(out) == 0


    def test_accuracy_dupls_in_X(
        self, _X_factory, _shape, _combos, _gdfc_args
    ):

        assert (0, 0) in _combos

        # rig X so that a poly column will be a dupl of an X column to
        # see if this finds them. make 1 column all 2s and another all
        # 4s, so that the poly column for the 2s will be another column
        # of 4s.
        _X_wip = _X_factory(
            _format='np',
            _dtype='int',
            _has_nan=False,
            _constants={0: 2, _shape[1]-1: 4},
            _shape=_shape
        )

        out = _get_dupls_for_combo_in_X_and_poly(
            _X_wip,
            _combos,
            _min_degree=1,
            **_gdfc_args
        )

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], tuple)
        assert out[0] == ((_shape[1]-1,), (0, 0))


    def test_accuracy_dupls_in_poly(self, _gdfc_args):

        # rig a dataset to cause poly terms to be dupls.
        # this is conveniently done by doing poly on a dummied
        # series and only using interaction terms
        # the duplicates will also happen to be columns of constants

        # This is just to see if the POLY scan part of _get_dupls can
        # actually find duplicates.

        _shape = (100, 3)

        _pool = list('abc')

        while True:
            # ensure that X_np will dummy out to 3 columns
            # that is, there are 3 unique categories in _X_np
            _X_np = np.random.choice(_pool, _shape[0], replace=True)
            if len(np.unique(_X_np)) == 3:
                break

        _X_np = _X_np.reshape((-1, 1))

        _X_ohe = OneHotEncoder(drop=None).fit_transform(_X_np)

        # need to manage for versions where OHE does/doesnt have sparse_output
        if hasattr(_X_ohe, 'toarray'):
            _X_ohe = _X_ohe.toarray()

        assert _X_ohe.shape[1] == 3

        _combos = list(itertools.combinations(range(len(_pool)), 2))

        del _pool

        # there should be 2 poly columns of all zeros, which
        # means they are all equal to each other.
        # there should be no duplicates against X.

        out = _get_dupls_for_combo_in_X_and_poly(
            _X_ohe,
            _combos,
            _min_degree=1,
            **_gdfc_args
        )

        assert isinstance(out, list)
        assert len(out) == 3
        assert all(map(isinstance, out, (tuple for _ in out)))

        assert out[0] == ((0, 1), (0, 2))
        assert out[1] == ((0, 1), (1, 2))
        assert out[2] == ((0, 2), (1, 2))




