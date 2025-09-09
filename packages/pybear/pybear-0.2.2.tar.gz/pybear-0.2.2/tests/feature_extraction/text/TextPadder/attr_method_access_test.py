# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np

from pybear.base import is_fitted
from pybear.base.exceptions import NotFittedError

from pybear.feature_extraction.text._TextPadder.TextPadder import TextPadder as TP



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES

@pytest.fixture(scope='function')
def _kwargs():
    return {
        'fill': 'qbert',
        'n_features': 1
    }


@pytest.fixture(scope='function')
def _X():
    return [
        ['Two', 'roads', 'diverged', 'in', 'a', 'yellow', 'wood'],
        ['And', 'sorry', 'I', 'could', 'not', 'travel', 'both'],
        ['And', 'be', 'one', 'traveler,', 'long', 'I', 'stood'],
        ['And', 'looked', 'down', 'one', 'as', 'far', 'as', 'I', 'could'],
        ['To','where', 'it', 'bent', 'in', 'the', 'undergrowth;']
    ]

# END fixtures
# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^



# ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM
class TestAttrAccessBeforeAndAfterFitAndTransform:


    def test_attr_access(self, _X, _kwargs):

        TestCls = TP(**_kwargs)

        _attrs = ['n_features_']

        # BEFORE FIT ***************************************************

        # SHOULD GIVE AttributeError/NotFittedError
        # TP external attrs are @property and raise NotFittedError
        # which is child of AttrError
        for attr in _attrs:
            with pytest.raises(NotFittedError):
                getattr(TestCls, attr)

        # n_features cannot be set
        with pytest.raises(AttributeError):
            TestCls.n_features_ = 4

        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        TestCls.fit(_X, None)

        if TestCls.n_features <= 9:
            # self.n_features_ should have incremented to 9
            assert TestCls.n_features_ == 9

        # all attrs should be accessible after fit
        for attr in _attrs:
            out = getattr(TestCls, attr)
            if attr == 'n_features_':
                assert isinstance(out, numbers.Integral)
                assert out == 9

        # n_features cannot be set
        with pytest.raises(AttributeError):
            TestCls.n_features_ = 4
        # END AFTER FIT ************************************************

        # AFTER TRANSFORM **********************************************

        TestCls.transform(_X)

        # after transform, should be the exact same condition as after
        # fit, and pass the same tests
        for attr in _attrs:
            out = getattr(TestCls, attr)
            if attr == 'n_features_':
                assert isinstance(out, numbers.Integral)
                assert out == 9

        # n_features cannot be set
        with pytest.raises(AttributeError):
            TestCls.n_features_ = 4
        # END AFTER TRANSFORM ******************************************

        del TestCls

# END ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM


# ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM ***
class TestMethodAccessBeforeAndAfterFitAndAfterTransform:



    # methods
    # [
    #     'fit',
    #     'fit_transform',
    #     'get_metadata_routing',
    #     'get_params',
    #     'partial_fit',
    #     '_reset',
    #     'score',
    #     'set_output',
    #     'set_params',
    #     'transform'
    # ]


    def test_access_methods_before_fit(self, _X, _kwargs):

        TestCls = TP(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X, None), TP)

        # HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^v^v^
        # Reset Changes is_fitted To False:
        # fit an instance  (done above)
        # assert the instance is fitted
        assert is_fitted(TestCls) is True
        # call :meth: reset
        TestCls._reset()
        # assert the instance is not fitted
        assert is_fitted(TestCls) is False
        # END HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X, None), list)

        TestCls._reset()

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'fill' in out
        assert isinstance(out['fill'], str)
        assert 'n_features' in out

        # inverse_transform()
        # TP should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X, None), TP)

        # reset()
        assert isinstance(TestCls._reset(), TP)

        # score()
        with pytest.raises(NotFittedError):
            assert TestCls.score(_X, None) is None

        # set_output()
        assert isinstance(TestCls.set_output(transform='pandas'), TP)
        assert TestCls._output_transform == 'pandas'

        # set_params()
        assert isinstance(TestCls.set_params(fill='what'), TP)
        assert TestCls.fill == 'what'

        # transform()
        with pytest.raises(NotFittedError):
            TestCls.transform(_X)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = TP(**_kwargs)
        TestCls.fit(_X, None)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X), list)

        TestCls._reset()

        # fit()
        assert isinstance(TestCls.fit(_X), TP)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'fill' in out
        assert isinstance(out['fill'], str)
        assert 'n_features' in out

        # inverse_transform()
        # TP should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X), TP)

        # reset()
        assert isinstance(TestCls._reset(), TP)

        TestCls.fit(_X, None)

        # score()
        assert TestCls.score(_X, None) is None

        # set_output()
        assert isinstance(TestCls.set_output(transform='default'), TP)
        assert TestCls._output_transform == 'default'

        # set_params()
        assert isinstance(TestCls.set_params(n_features=10_000), TP)
        assert TestCls.n_features == 10_000

        # transform()
        assert isinstance(TestCls.transform(_X), np.ndarray)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = TP(**_kwargs).fit(_X, None)
        TransformedTestCls = TP(**_kwargs).fit(_X, None)
        TransformedTestCls.transform(_X)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TransformedTestCls.fit(_X), TP)

        TransformedTestCls.transform(_X, copy=None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # TP should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(_X), TP)
        TransformedTestCls.transform(_X)

        # reset()
        assert isinstance(TransformedTestCls._reset(), TP)
        TransformedTestCls.fit_transform(_X)

        # set_output()
        assert isinstance(
            TransformedTestCls.set_output(transform='default'), TP
        )
        assert TransformedTestCls._output_transform == 'default'

        # set_params()
        assert isinstance(TransformedTestCls.set_params(n_features=9_999), TP)
        assert TransformedTestCls.n_features == 9_999

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), np.ndarray)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM






