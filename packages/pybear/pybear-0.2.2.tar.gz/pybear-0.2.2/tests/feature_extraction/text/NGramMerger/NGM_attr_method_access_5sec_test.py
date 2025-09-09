# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np

from pybear.feature_extraction.text._NGramMerger.NGramMerger import \
    NGramMerger as NGM



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES

@pytest.fixture(scope='module')
def _kwargs():
    return {
        'ngrams': [['GREEN', 'EGGS', 'AND', 'HAM']],
        'ngcallable': None,
        'sep': '@',
        'wrap': False,
        'remove_empty_rows': False
    }


@pytest.fixture(scope='module')
def _X():
    return [
        ['I', 'AM', 'SAM'],
        ['SAM', 'I', 'AM'],
        ['THAT', 'SAM-I-AM'],
        ['THAT', 'SAM-I-AM'],
        ['I', 'DO', 'NOT', 'LIKE'],
        ['THAT', 'SAM-I-AM'],
        ['DO', 'YOU', 'LIKE'],
        ['GREEN', 'EGGS', 'AND', 'HAM'],
        ['I', 'DO', 'NOT', 'LIKE', 'THEM'],
        ['SAM-I-AM'],
        ['I', 'DO', 'NOT', 'LIKE'],
        ['GREEN', 'EGGS', 'AND', 'HAM']
    ]

# END fixtures
# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^



# ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM
class TestAttrAccessBeforeAndAfterFitAndTransform:


    def test_attr_access(self, _X, _kwargs):


        _attrs = [
            'n_rows_',
            'row_support_'
        ]

        TestCls = NGM(**_kwargs)

        # BEFORE FIT ***************************************************

        # SHOULD GIVE AttributeError
        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)

        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        TestCls.fit(_X, None)

        # same as before fit, no access
        # SHOULD GIVE AttributeError
        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)
        # END AFTER FIT ************************************************

        # AFTER TRANSFORM **********************************************

        TestCls.transform(_X)

        # after transform, should have access to everything
        _n_rows = getattr(TestCls, 'n_rows_')
        assert isinstance(_n_rows, numbers.Integral)
        assert _n_rows == 12

        _row_support = getattr(TestCls, 'row_support_')
        assert isinstance(_row_support, np.ndarray)
        assert len(_row_support) == len(_X)
        assert all(map(isinstance, _row_support, (np.bool_ for _ in _row_support)))
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
    #     'reset',
    #     'score',
    #     'set_params',
    #     'transform'
    # ]


    def test_access_methods_before_fit(self, _X, _kwargs):

        TestCls = NGM(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X, None), NGM)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X, None), list)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'wrap' in out
        assert isinstance(out['wrap'], bool)

        # inverse_transform()
        # NGM should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X, None), NGM)

        # reset()  no-op
        assert isinstance(TestCls.reset(), NGM)

        # score()
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(wrap=True), NGM)
        assert TestCls.wrap is True
        assert isinstance(TestCls.set_params(wrap=False), NGM)
        assert TestCls.wrap is False

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = NGM(**_kwargs)
        TestCls.fit(_X, None)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X), list)

        TestCls.reset()
        TestCls.fit(_X)

        # fit()
        assert isinstance(TestCls.fit(_X), NGM)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'sep' in out
        assert isinstance(out['sep'], str)

        # inverse_transform()
        # NGM should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X), NGM)

        # reset()
        assert isinstance(TestCls.reset(), NGM)
        TestCls.fit(_X)

        # score()
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(remove_empty_rows=True), NGM)
        assert TestCls.remove_empty_rows is True
        assert isinstance(TestCls.set_params(remove_empty_rows=False), NGM)
        assert TestCls.remove_empty_rows is False

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = NGM(**_kwargs).fit(_X, None)
        TransformedTestCls = NGM(**_kwargs).fit(_X, None)

        TransformedTestCls.transform(_X)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TransformedTestCls.fit(_X), NGM)

        TransformedTestCls.transform(_X, copy=None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # NGM should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(_X), NGM)
        TransformedTestCls.transform(_X)

        # score()
        assert TransformedTestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TransformedTestCls.set_params(sep='XYZ'), NGM)
        assert TransformedTestCls.sep == 'XYZ'
        assert isinstance(TransformedTestCls.set_params(sep='ABC'), NGM)
        assert TransformedTestCls.sep == 'ABC'

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM






