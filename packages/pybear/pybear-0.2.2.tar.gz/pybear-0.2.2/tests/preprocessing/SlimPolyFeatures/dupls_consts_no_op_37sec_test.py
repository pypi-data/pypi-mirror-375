# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing._SlimPolyFeatures.SlimPolyFeatures import \
    SlimPolyFeatures as SlimPoly



# check accessing:
# poly_combinations_
# poly_constants_
# poly_duplicates_
# dropped_poly_duplicates_
# kept_poly_duplicates_
# when there are and arent duplicate/constant columns


class TestDuplsAndConstantsInX:

    # this coincidentally tests handling of the various pd nan-likes.

    # WHEN scan_X==True AND THERE ARE CONSTANTS/DUPLS IN X:
    # ALL @properties SHOULD WARN & RETURN NONE
    # EVERYTHING (including transform()) SHOULD BE A NO-OP EXCEPT FOR partial_fit,
    # fit, set_params, & get_params, reset, n_features_in_, and feature_names_in_


    @staticmethod
    @pytest.fixture(scope='module')
    # need to have enough rows so there is *no* chance
    # that higher order polynomial terms end up going to all nan, which
    # will ruin the tests. 10 rows was too few. When multiplying columns
    # with nans, the nans replicate, and if there are too many amongst
    # the columns involved, eventually you end up with a column of all
    # nans.
    # also need to have enough columns that the tests can be done with
    # various mixes of constants and dupl columns without overlap, i.e.,
    # no columns that are both constant and duplicate.
    def _shape():
        return (20, 6)


    @pytest.mark.parametrize('X_format', ('np',  'pd', 'pl', 'coo_array'))
    @pytest.mark.parametrize('dupls', ('none', 'dupls1', 'dupls2'))
    @pytest.mark.parametrize('constants', ('none', 'constants1', 'constants2'))
    def test_dupls_and_constants(
        self, _X_factory, _kwargs, X_format, dupls, _columns, constants, _shape
    ):

        # scan_X must be True to find dupls and constants

        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['degree'] = 3
        _new_kwargs['scan_X'] = True   # <+===== MUST BE True FOR no-ops TO HAPPEN

        # make sure there is no overlap of dupl & constant idxs or
        # it will screw up X_factory

        # set dupls v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        if dupls == 'dupls1':
            dupls = [[0, 2]]
        elif dupls == 'dupls2':
            dupls = [[0, 2], [4, 5]]
        elif dupls == 'none':
            dupls = None
        else:
            raise Exception
        # END set dupls v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


        # set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        if constants == 'constants1':
            constants = {1: 1}
        elif constants == 'constants2':
            constants = {1:0, 3:np.pi}
        elif constants == 'none':
            constants = None
        else:
            raise Exception
        # END set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


        TEST_X = _X_factory(
            _dupl=dupls, _format=X_format, _dtype='flt', _has_nan=True,
            _constants=constants, _columns=_columns, _zeros=None, _shape=_shape
        )

        TestCls = SlimPoly(**_new_kwargs)

        # if any dupls or any constants, should be no-ops on almost
        # everything. should still have access to feature_names_in_,
        # n_features_in_, partial_fit, fit (which resets), get_params,
        # reset, & set_params
        has_dupls_or_constants = False
        if dupls is not None or constants is not None:
            has_dupls_or_constants += 1


        # must be fitted to access all of these attrs, properties, and
        # methods! partial_fit and fit should always be accessible
        # regardless of dupls or constants
        # partial_fit() ---- do this partial fit first to induce a state
        # that may have constants and/or dupls...
        assert TestCls.partial_fit(TEST_X) is TestCls
        # TestCls may have degenerate condition, depending on the test.
        # should be able to access partial_fit again...
        assert TestCls.partial_fit(TEST_X) is TestCls
        # then do fit(), which resets it, to have a fitted instance for
        # the tests below fit()
        assert TestCls.fit(TEST_X) is TestCls


        if has_dupls_or_constants:

            # all of these should be blocked. should be a no-op with a
            # warning, and returns None

            with pytest.warns():
                assert TestCls.get_feature_names_out() is None

            with pytest.warns():
                assert TestCls.transform(TEST_X) is None

            with pytest.warns():
                assert TestCls.poly_combinations_ is None

            with pytest.warns():
                assert TestCls.poly_duplicates_ is None

            with pytest.warns():
                assert TestCls.kept_poly_duplicates_ is None

            with pytest.warns():
                assert TestCls.dropped_poly_duplicates_ is None

            with pytest.warns():
                assert TestCls.poly_constants_ is None


        elif not has_dupls_or_constants:

            # all things that were no-op when there were constants/duplicates
            # should be operative w/o constants/duplicates

            assert isinstance(TestCls.get_feature_names_out(), np.ndarray)

            assert isinstance(TestCls.transform(TEST_X), type(TEST_X))

            assert isinstance(TestCls.poly_combinations_, tuple)

            assert isinstance(TestCls.poly_duplicates_, list)

            assert isinstance(TestCls.kept_poly_duplicates_, dict)

            assert isinstance(TestCls.dropped_poly_duplicates_, dict)

            assert isinstance(TestCls.poly_constants_, dict)


        # v v v these all should function normally no matter what state
        # SPF is in

        # feature_names_in_
        if X_format in ['pd', 'pl']:
            _fni = TestCls.feature_names_in_
            assert isinstance(_fni, np.ndarray)
            assert _fni.dtype == object
            assert len(_fni) == TEST_X.shape[1]

        # n_features_in_
        _nfi = TestCls.n_features_in_
        assert isinstance(_nfi, int)
        assert _nfi == TEST_X.shape[1]

        # get_params
        _params = TestCls.get_params()
        assert isinstance(_params, dict)

        # set_params
        # remember most are blocked once fit!
        TestCls.set_params(sparse_output=True, n_jobs=2)
        assert TestCls.sparse_output is True
        assert TestCls.n_jobs == 2

        # reset
        assert TestCls.reset() is TestCls







