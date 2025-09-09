# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from typing import Sequence

import numbers

import numpy as np

from pybear.feature_extraction.text._TextJustifier.TextJustifier import \
    TextJustifier as TJ



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES

@pytest.fixture(scope='function')
def _kwargs():
    return {
        'n_chars': 80,
        'sep': ' ',
        'line_break': None,
        'backfill_sep': ' ',
        'join_2D': ' '
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

        TestCls = TJ(**_kwargs)

        _attrs = ['n_rows_']

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

        TestCls = TJ(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X, None), TJ)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X, None), list)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'sep' in out
        assert isinstance(out['sep'], (str, Sequence))

        # inverse_transform()
        # TJ should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X, None), TJ)

        # score()
        # remember TextJustifier is always fitted
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(sep='what'), TJ)
        assert TestCls.sep == 'what'

        # transform()
        # remember TextJustifier is always fitted
        assert isinstance(TestCls.transform(_X), list)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = TJ(**_kwargs)
        TestCls.fit(_X, None)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TestCls.fit(_X), TJ)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'sep' in out
        assert isinstance(out['sep'], (str, Sequence))

        # inverse_transform()
        # TJ should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X), TJ)

        # score()
        # remember TextJustifier is always fitted
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(sep=set(list('abcde'))), TJ)
        assert np.array_equal(TestCls.sep, set(list('abcde')))

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = TJ(**_kwargs).fit(_X, None)
        TransformedTestCls = TJ(**_kwargs).fit(_X, None)
        TransformedTestCls.transform(_X)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TransformedTestCls.fit(_X), TJ)

        TransformedTestCls.transform(_X, None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # TJ should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(_X), TJ)
        TransformedTestCls.transform(_X)

        # score()
        # remember TextJustifier is always fitted
        assert TransformedTestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TransformedTestCls.set_params(sep='_'), TJ)
        assert TransformedTestCls.sep == '_'

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM





