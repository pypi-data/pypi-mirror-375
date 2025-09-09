# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import pytest

import numpy as np

from pybear.feature_extraction.text._StopRemover.StopRemover import \
    StopRemover as SR



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES

@pytest.fixture(scope='function')
def _kwargs():
    return {
        'match_callable': None,
        'remove_empty_rows': True,
        'n_jobs': 1  # leave a 1 because of confliction
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

        TestCls = SR(**_kwargs)

        _attrs = ['n_rows_', 'row_support_']

        # BEFORE FIT ***************************************************

        # SHOULD GIVE AttributeError
        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)

        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        TestCls.fit(_X, None)

        # after fit, should be the exact same condition as before fit.
        # SHOULD GIVE AttributeError
        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)
        # END AFTER FIT ************************************************

        # AFTER TRANSFORM **********************************************

        TestCls.transform(_X)

        # after transform, should have access.
        for attr in _attrs:
            out = getattr(TestCls, attr)
            if attr == 'n_rows_':
                assert isinstance(out, numbers.Integral)
                assert out == 5
            elif attr == 'row_support_':
                assert isinstance(out, np.ndarray)
                assert len(out) == len(_X)
                assert all(map(isinstance, out, (np.bool_ for _ in out)))
            else:
                raise Exception

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
    #     'score',
    #     'set_params',
    #     'transform'
    # ]


    def test_access_methods_before_fit(self, _X, _kwargs):

        TestCls = SR(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X, None), SR)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X, None), list)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'remove_empty_rows' in out
        assert isinstance(out['remove_empty_rows'], bool)

        # inverse_transform()
        # SR should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X, None), SR)

        # score()
        # remember StopRemover is always fitted
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(match_callable=lambda x, y: x==y), SR)
        assert callable(TestCls.match_callable)
        assert TestCls.match_callable('a', 'a') is True

        # transform()
        # remember StopRemover is always fitted
        assert isinstance(TestCls.transform(_X), list)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = SR(**_kwargs)
        TestCls.fit(_X, None)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TestCls.fit(_X), SR)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'remove_empty_rows' in out
        assert isinstance(out['remove_empty_rows'], bool)

        # inverse_transform()
        # SR should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X), SR)

        # score()
        # remember StopRemover is always fitted
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(remove_empty_rows=False), SR)
        assert TestCls.remove_empty_rows is False

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = SR(**_kwargs).fit(_X, None)
        TransformedTestCls = SR(**_kwargs).fit(_X, None)
        TransformedTestCls.transform(_X)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TransformedTestCls.fit(_X), SR)

        TransformedTestCls.transform(_X, copy=None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # SR should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(_X), SR)
        TransformedTestCls.transform(_X)

        # score()
        # remember StopRemover is always fitted
        assert TransformedTestCls.score(_X, None) is None

        # set_params()
        assert isinstance(
            TransformedTestCls.set_params(match_callable=lambda x, y: x != y), SR
        )
        assert callable(TransformedTestCls.match_callable)
        assert TransformedTestCls.match_callable('a', 'b') is True

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM




