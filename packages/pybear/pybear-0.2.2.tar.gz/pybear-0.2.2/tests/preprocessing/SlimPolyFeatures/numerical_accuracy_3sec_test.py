# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import itertools

import numpy as np

from sklearn.preprocessing import OneHotEncoder as OHE

from pybear.preprocessing._SlimPolyFeatures.SlimPolyFeatures import \
    SlimPolyFeatures as SlimPoly



# this has to stay because of all the hard-coded assertions
@pytest.fixture(scope='module')
def _shape():
    return (9, 3)


class TestBasicCaseNoDuplsNoConstantsInPoly:


    @pytest.mark.parametrize('min_degree', (1,2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_basic_case(
        self, _X_factory, _columns, _kwargs, _shape, min_degree, intx_only
    ):


        _X_np = _X_factory(
            _dupl=None, _format='np', _dtype='flt', _has_nan=False,
            _constants=None, _columns=None, _zeros=None, _shape=_shape
        )

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only

        TestCls = SlimPoly(**_new_kwargs)
        out = TestCls.fit_transform(_X_np)

        if min_degree == 1:
            if intx_only:
                assert out.shape[1] == \
                    _shape[1] + len(list(itertools.combinations(range(_shape[1]), 2)))
                assert np.array_equal(out[:, 0], _X_np[:, 0])
                assert np.array_equal(out[:, 1], _X_np[:, 1])
                assert np.array_equal(out[:, 2], _X_np[:, 2])
                assert np.array_equal(out[:, 3], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 4], _X_np[:, (0, 2)].prod(1))
                assert np.array_equal(out[:, 5], _X_np[:, (1, 2)].prod(1))
            elif not intx_only:
                assert out.shape[1] == \
                   _shape[1] + \
                   len(list(itertools.combinations_with_replacement(range(_shape[1]), 2)))
                assert np.array_equal(out[:, 0], _X_np[:, 0])
                assert np.array_equal(out[:, 1], _X_np[:, 1])
                assert np.array_equal(out[:, 2], _X_np[:, 2])
                assert np.array_equal(out[:, 3], _X_np[:, (0, 0)].prod(1))
                assert np.array_equal(out[:, 4], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 5], _X_np[:, (0, 2)].prod(1))
                assert np.array_equal(out[:, 6], _X_np[:, (1, 1)].prod(1))
                assert np.array_equal(out[:, 7], _X_np[:, (1, 2)].prod(1))
                assert np.array_equal(out[:, 8], _X_np[:, (2, 2)].prod(1))

        elif min_degree == 2:
            if intx_only:
                assert out.shape[1] == \
                   len(list(itertools.combinations(range(_shape[1]), 2)))
                assert np.array_equal(out[:, 0], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 1], _X_np[:, (0, 2)].prod(1))
                assert np.array_equal(out[:, 2], _X_np[:, (1, 2)].prod(1))
            elif not intx_only:
                assert out.shape[1] == \
                   len(list(itertools.combinations_with_replacement(range(_shape[1]), 2)))
                assert np.array_equal(out[:, 0], _X_np[:, (0, 0)].prod(1))
                assert np.array_equal(out[:, 1], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 2], _X_np[:, (0, 2)].prod(1))
                assert np.array_equal(out[:, 3], _X_np[:, (1, 1)].prod(1))
                assert np.array_equal(out[:, 4], _X_np[:, (1, 2)].prod(1))
                assert np.array_equal(out[:, 5], _X_np[:, (2, 2)].prod(1))


class TestRiggedCasePolyHasConstantsAndDupls:

    # A POLY EXPANSION ON A ONE HOT ENCODED COLUMN, ALL INTERACTION FEATURES
    # ARE COLUMNS OF ZEROS OR DUPLICATE

    # ALSO TEST MULTIPLE PARTIAL FITS & TRANSFORMS

    @pytest.mark.parametrize('min_degree', (1,2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_constant_and_dupl(
        self, _kwargs, _shape, min_degree, intx_only
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 2
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only

        TestCls = SlimPoly(**_new_kwargs)

        partial_fits = 5
        BATCH_XS = []
        for batch in range(partial_fits):
            while True:
                _X = np.random.choice(
                    list('abc'), _shape[0], replace=True
                ).reshape((-1,1))
                if len(np.unique(_X.ravel())) == 3:
                    BATCH_XS.append(_X)
                    break

        assert len(BATCH_XS) == partial_fits

        _ohe = OHE()
        for batch_idx, batch in enumerate(BATCH_XS):
            _expanded = _ohe.fit_transform(batch)
            # need to manage for versions of OHE that do/dont have sparse_output
            if hasattr(_expanded, 'toarray'):
                _expanded = _expanded.toarray()
            BATCH_XS[batch_idx] = _expanded

        for _X_np in BATCH_XS:

            out = TestCls.fit_transform(_X_np)

            if min_degree == 1:
                if intx_only:
                    assert out.shape[1] == 3
                    assert np.array_equal(out[:, 0], _X_np[:, 0])
                    assert np.array_equal(out[:, 1], _X_np[:, 1])
                    assert np.array_equal(out[:, 2], _X_np[:, 2])
                elif not intx_only:
                    assert out.shape[1] == 3
                    assert np.array_equal(out[:, 0], _X_np[:, 0])
                    assert np.array_equal(out[:, 1], _X_np[:, 1])
                    assert np.array_equal(out[:, 2], _X_np[:, 2])
            elif min_degree == 2:
                if intx_only:
                    assert isinstance(out, np.ndarray)
                    assert out.shape[1] == 0
                elif not intx_only:
                    assert isinstance(out, np.ndarray)
                    assert out.shape[1] == 3
                    assert np.array_equal(out[:, 0], _X_np[:, 0])
                    assert np.array_equal(out[:, 1], _X_np[:, 1])
                    assert np.array_equal(out[:, 2], _X_np[:, 2])


class TestRiggedCaseAllIntxAreDupl:

    @pytest.mark.parametrize('min_degree', (1,2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_dupls(
        self, _X_factory, _columns, _kwargs, _shape, min_degree, intx_only
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 2
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only


        # with this rigging:
        # - all squared columns != original column.
        # - all interactions equal the same thing, so there should be
        #       only one feature in poly.
        _X_np = np.array(
            [
                [2, 0, 0],
                [2, 0, 0],
                [2, 0, 0],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [0, 0, 2],
                [0, 2, 0],
                [0, 2, 0]
            ],
            dtype=np.uint8
        )

        TestCls = SlimPoly(**_new_kwargs)
        out = TestCls.fit_transform(_X_np)

        if min_degree == 1:
            if intx_only:
                assert out.shape[1] == 4
                assert np.array_equal(out[:, 0], _X_np[:, 0])
                assert np.array_equal(out[:, 1], _X_np[:, 1])
                assert np.array_equal(out[:, 2], _X_np[:, 2])
                assert np.array_equal(out[:, 3], _X_np[:, (0, 1)].prod(1))
            elif not intx_only:
                assert out.shape[1] == 7
                assert np.array_equal(out[:, 0], _X_np[:, 0])
                assert np.array_equal(out[:, 1], _X_np[:, 1])
                assert np.array_equal(out[:, 2], _X_np[:, 2])
                assert np.array_equal(out[:, 3], _X_np[:, (0, 0)].prod(1))
                assert np.array_equal(out[:, 4], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 5], _X_np[:, (1, 1)].prod(1))
                assert np.array_equal(out[:, 6], _X_np[:, (2, 2)].prod(1))

        elif min_degree == 2:
            if intx_only:
                assert out.shape[1] == 1
                assert np.array_equal(out[:, 0], _X_np[:, (0, 1)].prod(1))
            elif not intx_only:
                assert out.shape[1] == 4
                assert np.array_equal(out[:, 0], _X_np[:, (0, 0)].prod(1))
                assert np.array_equal(out[:, 1], _X_np[:, (0, 1)].prod(1))
                assert np.array_equal(out[:, 2], _X_np[:, (1, 1)].prod(1))
                assert np.array_equal(out[:, 3], _X_np[:, (2, 2)].prod(1))


class TestOneColumnX:

    @pytest.mark.parametrize('min_degree', (1,3))
    def test_one_column(self, _kwargs, _shape, min_degree):

        # interaction_only must always be False for single column

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 3
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = False

        TestCls = SlimPoly(**_new_kwargs)

        _X_np = np.random.uniform(0, 1, (_shape[0], 1))

        out = TestCls.fit_transform(_X_np)

        if min_degree == 1:
            assert isinstance(out, np.ndarray)
            assert out.shape[1] == 3
            assert np.array_equal(out[:, 0], _X_np[:, 0])
            assert np.array_equal(out[:, 1], _X_np[:, (0, 0)].prod(1))
            assert np.array_equal(out[:, 2], _X_np[:, (0, 0, 0)].prod(1))
        elif min_degree == 2:
            assert isinstance(out, np.ndarray)
            assert out.shape[1] == 2
            assert np.array_equal(out[:, 0], _X_np[:, (0, 0)].prod(1))
            assert np.array_equal(out[:, 1], _X_np[:, (0, 0, 0)].prod(1))
        elif min_degree == 3:
            assert out.shape[1] == 1
            assert np.array_equal(out[:, 0], _X_np[:, (0, 0, 0)].prod(1))








