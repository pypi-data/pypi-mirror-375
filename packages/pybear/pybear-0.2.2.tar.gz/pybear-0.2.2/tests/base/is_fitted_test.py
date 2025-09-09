# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._is_fitted import is_fitted
from pybear.preprocessing import (
    ColumnDeduplicator as CDT,
    InterceptManager as IM
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


import pytest



class TestIsFitted:


    @staticmethod
    @pytest.fixture(scope='module')
    def good_estimator():

        class Foo:

            def __init__(self):
                self.a = 1
                self.b = 2
                self.c = 3

            def __pybear_is_fitted__(self):
                return True

            def fit(self):
                self.d_ = 4


        return Foo


    @staticmethod
    @pytest.fixture(scope='module')
    def good_attributes():
        return ('a', 'b', 'c')


    @pytest.mark.parametrize('junk_estimator',
        (-2.7, -1, 0, 1, 2.7, True, None, 'junk', [0,1], (0,1), {1,2}, {'a': 1})
    )
    def test_rejects_junk_estimator(self, junk_estimator, good_attributes):

        with pytest.raises(ValueError):
            is_fitted(
                junk_estimator,
                good_attributes,
                all_or_any=all
            )


    @pytest.mark.parametrize('bad_estimator', (min, max, lambda x: x))
    def test_rejects_bad_estimator(self, bad_estimator, good_attributes):

        with pytest.raises(ValueError):
            is_fitted(
                bad_estimator,
                good_attributes,
                all_or_any=all
            )


    @pytest.mark.parametrize('good_estimator',
        (CDT(), IM(), LogisticRegression(), StandardScaler())
    )
    def test_accepts_good_estimator(self, good_estimator, good_attributes):

        is_fitted(
            good_estimator,
            good_attributes,
            all_or_any=all
        )


    @pytest.mark.parametrize('junk_attributes',
        (-2.7, -1, 0, 1, 2.7, True, False, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_attributes(
        self, good_estimator, junk_attributes
    ):

        with pytest.raises(ValueError):
            is_fitted(
                good_estimator(),
                junk_attributes,
                all_or_any=all
            )

    @pytest.mark.parametrize('bad_attributes', ([1,2,3], (1,2,3), {1,2,3}))
    def test_rejects_bad_attributes(self, good_estimator, bad_attributes):

        with pytest.raises(ValueError):
            is_fitted(
                good_estimator(),
                bad_attributes,
                all_or_any=all
            )


    def test_accepts_good_attributes(self, good_estimator, good_attributes):

        is_fitted(
            good_estimator(),
            attributes=good_attributes,
            all_or_any=all
        )

        is_fitted(
            good_estimator(),
            attributes='a',
            all_or_any=all
        )

        is_fitted(
            good_estimator(),
            attributes=None,
            all_or_any=all
        )


    @pytest.mark.parametrize('junk_any_or_all',
        (-2.7, -1, 0, 1, 2.7, True, None, 'junk', [0,1], (0,1), {1,2}, {'a': 1})
    )
    def test_rejects_junk_all_or_any(
        self, good_estimator, good_attributes, junk_any_or_all
    ):

        with pytest.raises(ValueError):
            is_fitted(
                good_estimator(),
                attributes=good_attributes,
                all_or_any=junk_any_or_all
            )


    @pytest.mark.parametrize('bad_all_or_any', (min, max, lambda x: x))
    def test_rejects_bad_all_or_any(
        self, good_estimator, good_attributes, bad_all_or_any
    ):
        with pytest.raises(ValueError):
            is_fitted(
                good_estimator(),
                attributes=good_attributes,
                all_or_any=bad_all_or_any
            )


    @pytest.mark.parametrize('good_all_or_any', (any, all))
    def test_accepts_good_all_or_any(
        self, good_estimator, good_attributes, good_all_or_any
    ):

        is_fitted(
            good_estimator(),
            attributes=good_attributes,
            all_or_any=all
        )

    # end test validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # ** * ** * ** ** * ** * ** ** * ** * ** ** * ** * ** ** * ** * ** ** * **
    # ** * ** * ** ** * ** * ** ** * ** * ** ** * ** * ** ** * ** * ** ** * **

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # dunder

    @staticmethod
    @pytest.fixture(scope='function')
    def _dunder_est():

        def foo(est_is_fitted: bool):

            class TRF_EST:
                def __init__(self):
                    pass
                def __pybear_is_fitted__(self):
                    return est_is_fitted
                def fit(self):
                    pass

            return TRF_EST

        return foo


    @pytest.mark.parametrize('est_is_fitted', (True, False))
    def test_dunder(self, _dunder_est, est_is_fitted):

        out = is_fitted(
            _dunder_est(est_is_fitted)(),
            attributes=None,
            all_or_any=all
        )

        assert out is est_is_fitted

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # attributes

    @staticmethod
    @pytest.fixture(scope='function')
    def _attr_est():

        def foo(est_is_fitted: bool):

            class TRF_EST:

                def __init__(self):

                    self.x, self.y, self.z = 4, 5, 6

                    if est_is_fitted:
                        self.a = 1
                        self.b = 2
                        self.c = 3

                def fit(self):
                    pass

            return TRF_EST

        return foo


    @pytest.mark.parametrize('est_is_fitted', (True, False))
    def test_attr(self, _attr_est, est_is_fitted):
        # - - - - - - - - - - - - - - - - - - - - -
        out = is_fitted(
            _attr_est(est_is_fitted)(),
            attributes=('a', 'b', 'c'),
            all_or_any=all
        )

        assert out is est_is_fitted
        # - - - - - - - - - - - - - - - - - - - - -
        out2 = is_fitted(
            _attr_est(est_is_fitted)(),
            attributes=('a', 'b', 'c'),
            all_or_any=any
        )

        assert out2 is est_is_fitted
        # - - - - - - - - - - - - - - - - - - - - -
        out3 = is_fitted(
            _attr_est(est_is_fitted)(),
            attributes='a',
            all_or_any=all
        )

        assert out3 is est_is_fitted
        # - - - - - - - - - - - - - - - - - - - - -
        out4 = is_fitted(
            _attr_est(est_is_fitted)(),
            attributes='a',
            all_or_any=any
        )

        assert out4 is est_is_fitted
        # - - - - - - - - - - - - - - - - - - - - -

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # trailing underscore

    @staticmethod
    @pytest.fixture(scope='function')
    def _trailing_underscore_est():

        def foo(est_is_fitted: bool):

            class TRF_EST:
                def __init__(self):

                    self.x, self.y, self.z = 4, 5, 6

                    if est_is_fitted:
                        self.a_ = 1
                        self.b_ = 2
                        self.c_ = 3

                def fit(self):
                    pass

            return TRF_EST

        return foo


    @pytest.mark.parametrize('est_is_fitted', (True, False))
    def test_trailing_underscore(self, _trailing_underscore_est, est_is_fitted):

        out = is_fitted(
            _trailing_underscore_est(est_is_fitted)(),
            attributes=None,
            all_or_any=all
        )

        assert out is est_is_fitted

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^






