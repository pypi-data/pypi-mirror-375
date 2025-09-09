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

from pybear.preprocessing import SlimPolyFeatures as SlimPoly



# this tests the accuracy of the 5 @property attributes & feature_names_in_
# & n_features_in_ of SlimPoly for different min_degree/degree/interaction_only
# settings



class TestNFeaturesInFeatureNamesIn:

    # TEST ATTRS THAT ARE INDEPENDENT OF THE DEGREES OF EXPANSION

    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'coo_array'))
    def test_attr_accuracy(
        self, _X_factory, _columns, _kwargs, _shape, X_format
    ):

        _X_wip = _X_factory(
            _dupl=None,
            _format=X_format,
            _dtype='flt',
            _has_nan=False,
            _constants=None,
            _columns=_columns,
            _zeros=None,
            _shape=_shape
        )


        TestCls = SlimPoly(**_kwargs)

        # must be fitted to access all of these attrs & properties!
        assert TestCls.fit(_X_wip) is TestCls

        # feature_names_in_ - - - - - - - - - - - - - - -
        if X_format in ['pd', 'pl']:
            _fni = TestCls.feature_names_in_
            assert isinstance(_fni, np.ndarray)
            assert _fni.dtype == object
            assert len(_fni) == _X_wip.shape[1]
            assert np.array_equiv(_fni, _columns), \
                f"{_fni} after fit() != originally passed columns"
        else:
            with pytest.raises(AttributeError):
                TestCls.feature_names_in_
        # END feature_names_in_ - - - - - - - - - - - - - - -

        # n_features_in_ - - - - - - - - - - - - -
        _nfi = TestCls.n_features_in_
        assert isinstance(_nfi, int)
        assert _nfi == _shape[1]
        # - - - - - - - - - - - - - - - - - - - - -



class TestBasicCaseNoDuplsNoConstantsInPoly:

    # TEST THE @PROPERTY ATTRIBUTES THAT DEPEND ON DEGREES OF EXPANSION

    @pytest.mark.parametrize('min_degree', (2,3))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_basic_case(
        self, X_np, _columns, _kwargs, _shape, min_degree, intx_only
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 3
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only
        _new_kwargs['sparse_output'] = True

        TestCls = SlimPoly(**_new_kwargs)
        TestCls.fit(X_np)

        # poly_combinations_ - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_combinations_
        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for _ in out)))

        _2_deg_intx_only = \
            list(itertools.combinations(range(_shape[1]), 2))
        _2_deg_not_intx_only = \
            list(itertools.combinations_with_replacement(range(_shape[1]), 2))
        _3_deg_intx_only = \
            list(itertools.combinations(range(_shape[1]), 3))
        _3_deg_not_intx_only = \
            list(itertools.combinations_with_replacement(range(_shape[1]), 3))

        if min_degree == 2:
            if intx_only:
                assert out == tuple(_2_deg_intx_only + _3_deg_intx_only)
            elif not intx_only:
                assert out == tuple(_2_deg_not_intx_only + _3_deg_not_intx_only)

        elif min_degree == 3:
            if intx_only:
                assert out == tuple(_3_deg_intx_only)
            elif not intx_only:
                assert out == tuple(_3_deg_not_intx_only)
        # END poly_combinations_ - - - - - - - - - - - - - - - - - - - -

        # poly_duplicates_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_duplicates_
        assert isinstance(out, list)
        assert all(map(isinstance, out, (list for _ in out)))
        # should be empty list in every case for these specific tests
        assert len(out) == 0
        # END poly_duplicates_ - - - - - - - - - - - - - - - - - - - - -

        # kept_poly_duplicates_ - - - - - - - - - - - - - - - - - - - -
        out = TestCls.kept_poly_duplicates_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        # should be empty dict in every case for these specific tests
        assert len(out) == 0
        # END kept_poly_duplicates_ - - - - - - - - - - - - - - - - - -

        # dropped_poly_duplicates_ - - - - - - - - - - - - - - - - - - -
        out = TestCls.dropped_poly_duplicates_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        # should be empty dict in every case for these specific tests
        assert len(out) == 0
        # END dropped_poly_duplicates_ - - - - - - - - - - - - - - - - -

        # poly_constants_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_constants_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        # should be empty dict in every case for these specific tests
        assert len(out) == 0
        # END poly_constants_ - - - - - - - - - - - - - - - - - - - - -



class TestRiggedCasePolyHasConstantsAndDupls:

    # A POLY EXPANSION ON A ONE HOT ENCODED COLUMN, ALL INTERACTION
    # FEATURES ARE COLUMNS OF ZEROS OR DUPLICATE

    @pytest.mark.parametrize('min_degree', (1,2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_constant_and_dupl(
        self, _kwargs, _shape, min_degree, intx_only
    ):

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 2
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only
        _new_kwargs['sparse_output'] = True

        TestCls = SlimPoly(**_new_kwargs)

        while True:
            _X_wip = np.random.choice(
                list('abc'), _shape[0], replace=True
            ).reshape((-1,1))
            if len(np.unique(_X_wip.ravel())) == 3:
                break

        _X_wip = OHE().fit_transform(_X_wip)

        TestCls.fit(_X_wip)


        # poly_combinations_ - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_combinations_
        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for _ in out)))
        if min_degree == 1:
            # the squares of the og columns, which are in [0,1], would
            # be equal to the og column, so not included in output if og
            # X is included.
            assert len(out) == 0
        elif min_degree == 2:
            if intx_only:
                assert len(out) == 0
            elif not intx_only:
                # but if the og data is not included, then the squared
                # columns have nothing to be a duplicate of anymore, so
                # they stay.
                assert len(out) == _X_wip.shape[1]
                assert out == ((0, 0), (1, 1), (2, 2))
        else:
            raise Exception
        # END poly_combinations_ - - - - - - - - - - - - - - - - - - - -

        # poly_duplicates_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_duplicates_
        assert isinstance(out, list)
        assert all(map(isinstance, out, (list for _ in out)))
        if min_degree == 1:
            # because all the intx columns are constants
            # and the squares are duplicates of columns in X
            if intx_only:
                assert len(out) == 0
            elif not intx_only:
                assert len(out) == _X_wip.shape[1]
                assert out[0] == [(0,), (0, 0)]
                assert out[1] == [(1,), (1, 1)]
                assert out[2] == [(2,), (2, 2)]
        elif min_degree == 2:
            # all the duplicates are of columns in X, which isnt attached,
            # so they arent duplicates
            assert len(out) == 0
        else:
            raise Exception
        # END poly_duplicates_ - - - - - - - - - - - - - - - - - - - - -

        # kept_poly_duplicates_ - - - - - - - - - - - - - - - - - - - -
        out = TestCls.kept_poly_duplicates_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        if min_degree == 1:
            if intx_only:
                # because there are no duplicates, only constants
                assert len(out) == 0
            elif not intx_only:
                # all the duplicates are of columns in X
                assert len(out) == 3
                _keys = list(out.keys())
                assert _keys[0] == (0, )
                assert out[_keys[0]] == [(0, 0)]
                assert _keys[1] == (1, )
                assert out[_keys[1]] == [(1, 1)]
                assert _keys[2] == (2, )
                assert out[_keys[2]] == [(2, 2)]
        elif min_degree == 2:
            if intx_only:
                # because there are no duplicates, only constants
                assert len(out) == 0
            elif not intx_only:
                # all poly duplicates would be dupl of columns in X
                assert len(out) == 0
        else:
            raise Exception
        # END kept_poly_duplicates_ - - - - - - - - - - - - - - - - - -

        # dropped_poly_duplicates_ - - - - - - - - - - - - - - - - - - -
        out = TestCls.dropped_poly_duplicates_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        if min_degree == 1:
            if intx_only:
                # because there are no duplicates, only constants
                assert len(out) == 0
            elif not intx_only:
                assert len(out) == 3
                _keys = list(out.keys())
                assert _keys[0] == (0, 0)
                assert out[_keys[0]] == (0,)
                assert _keys[1] == (1, 1)
                assert out[_keys[1]] == (1,)
                assert _keys[2] == (2, 2)
                assert out[_keys[2]] == (2,)
        elif min_degree == 2:
            if intx_only:
                # because there are no duplicates, only constants
                assert len(out) == 0
            elif not intx_only:
                # all poly duplicates would be dupl of columns in X
                assert len(out) == 0
        else:
            raise Exception
        # END dropped_poly_duplicates_ - - - - - - - - - - - - - - - - -

        # poly_constants_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_constants_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))
        # because all the duplicates are also constants, constant supercedes
        assert len(out) == 3
        _keys = list(out.keys())
        assert _keys[0] == (0, 1)
        assert _keys[1] == (0, 2)
        assert _keys[2] == (1, 2)
        # END poly_constants_ - - - - - - - - - - - - - - - - - - - - -


class TestRiggedCaseAllIntxAreDupl:

    @pytest.mark.parametrize('min_degree', (1,2))
    @pytest.mark.parametrize('intx_only', (True, False))
    def test_dupls(
        self, _X_factory, _columns, _kwargs, _shape, min_degree, intx_only
    ):

        # remember that min_degree == 1 shouldnt affect these

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 2
        _new_kwargs['min_degree'] = min_degree
        _new_kwargs['interaction_only'] = intx_only
        _new_kwargs['sparse_output'] = True

        # with this rigging:
        # - all squared columns != original column.
        # - all interactions equal the same thing
        _X_wip = np.array(
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
        TestCls.fit(_X_wip)


        # poly_combinations_ - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_combinations_
        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for _ in out)))

        if intx_only:
            # all interactions equal the same thing, so there should be
            # only one feature in poly.
            assert out == ((0, 1),)
        elif not intx_only:
            # all squared columns != original column + 1 intx column
            assert out == ((0, 0), (0, 1), (1, 1), (2, 2))
        # END poly_combinations_ - - - - - - - - - - - - - - - - - - - -

        # poly_duplicates_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_duplicates_
        assert isinstance(out, list)
        assert all(map(isinstance, out, (list for _ in out)))

        # all interactions equal the same thing
        # all squared columns != original column.
        assert out == [[(0,1), (0,2), (1,2)]]
        # END poly_duplicates_ - - - - - - - - - - - - - - - - - - - - -

        # kept_poly_duplicates_ - - - - - - - - - - - - - - - - - - - -
        out = TestCls.kept_poly_duplicates_
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))

        # all interactions equal the same thing, so there should be
        # only one feature in poly.
        # all squared columns != original column.
        assert out == {(0,1): [(0,2), (1,2)]}
        # END kept_poly_duplicates_ - - - - - - - - - - - - - - - - - -

        # dropped_poly_duplicates_ - - - - - - - - - - - - - - - - - - -
        out = TestCls.dropped_poly_duplicates_
        assert isinstance(TestCls.dropped_poly_duplicates_, dict)
        assert all(map(isinstance, out, (tuple for _ in out)))

        # all interactions equal the same thing, so there should be
        # only one feature in poly.
        # all squared columns != original column.
        assert out == {(0, 2): (0, 1), (1, 2): (0, 1)}
        # END dropped_poly_duplicates_ - - - - - - - - - - - - - - - - -

        # poly_constants_ - - - - - - - - - - - - - - - - - - - - - - -
        out = TestCls.poly_constants_
        assert isinstance(out, dict)
        assert len(out) == 0
        # END poly_constants_ - - - - - - - - - - - - - - - - - - - - -




