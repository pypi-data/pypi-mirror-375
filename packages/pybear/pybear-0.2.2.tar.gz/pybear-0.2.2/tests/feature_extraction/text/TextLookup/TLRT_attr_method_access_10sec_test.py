# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import pytest
import numpy as np

from pybear.feature_extraction.text._TextLookup.TextLookupRealTime import \
    TextLookupRealTime as TJRT



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES


@pytest.fixture(scope='module')
def _kwargs():
    return {
        'update_lexicon': False,
        'skip_numbers': True,
        'auto_split': True,
        'auto_add_to_lexicon': False,
        'auto_delete': True,   # <===== make it so it doesnt prompt
        'DELETE_ALWAYS': None,
        'REPLACE_ALWAYS': None,
        'SKIP_ALWAYS': None,
        'SPLIT_ALWAYS': None,
        'remove_empty_rows': False,
        'verbose': False
    }

@pytest.fixture(scope='module')
def _X():
    return [
        ['TWO', 'ROADS', 'DIVERGED', 'IN', 'A', 'YELLOW', 'WOOD'],
        ['AND', 'SORRY', 'I', 'COULD', 'NOT', 'TRAVEL', 'BOTH'],
        ['AND', 'BE', 'ONE', 'TRAVELER,', 'LONG', 'I', 'STOOD'],
        ['AND', 'LOOKED', 'DOWN', 'ONE', 'AS', 'FAR', 'AS', 'I', 'COULD'],
        ['TO','WHERE', 'IT', 'BENT', 'IN', 'THE', 'UNDERGROWTH']
    ]

# END fixtures
# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^



# ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM
class TestAttrAccessBeforeAndAfterFitAndTransform:


    def test_attr_access(self, _X, _kwargs):

        TestCls = TJRT(**_kwargs)

        _attrs = [
            'n_rows_',
            'row_support_',
            'DELETE_ALWAYS_',
            'REPLACE_ALWAYS_',
            'SKIP_ALWAYS_',
            'SPLIT_ALWAYS_',
            'KNOWN_WORDS',
            'LEXICON_ADDENDUM_'
        ]

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
        _n_rows = getattr(TestCls, 'n_rows_')
        assert isinstance(_n_rows, numbers.Integral)
        assert _n_rows == 5

        _row_support = getattr(TestCls, 'row_support_')
        assert isinstance(_row_support, np.ndarray)
        assert len(_row_support) == len(_X)
        assert all(map(isinstance, _row_support, (np.bool_ for _ in _row_support)))

        _DELETE_ALWAYS = getattr(TestCls, 'DELETE_ALWAYS_')
        assert isinstance(_DELETE_ALWAYS, list)
        assert all(map(isinstance, _DELETE_ALWAYS, (str for _ in _DELETE_ALWAYS)))

        _REPLACE_ALWAYS = getattr(TestCls, 'REPLACE_ALWAYS_')
        assert isinstance(_REPLACE_ALWAYS, dict)
        assert all(map(
            isinstance,
            _REPLACE_ALWAYS.keys(),
            (str for _ in _REPLACE_ALWAYS.keys())
        ))
        assert all(map(
            isinstance,
            _REPLACE_ALWAYS.values(),
            (str for _ in _REPLACE_ALWAYS.values())
        ))

        _SKIP_ALWAYS = getattr(TestCls, 'SKIP_ALWAYS_')
        assert isinstance(_SKIP_ALWAYS, list)
        assert all(map(isinstance, _SKIP_ALWAYS, (str for _ in _SKIP_ALWAYS)))

        _SPLIT_ALWAYS = getattr(TestCls, 'SPLIT_ALWAYS_')
        assert all(map(
            isinstance,
            _REPLACE_ALWAYS.keys(),
            (str for _ in _REPLACE_ALWAYS.keys())
        ))
        assert all(map(
            isinstance,
            _REPLACE_ALWAYS.values(),
            (list for _ in _REPLACE_ALWAYS.values())
        ))

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

        TestCls = TJRT(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X, None), TJRT)

        TestCls.reset()

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X, None), list)

        TestCls.reset()

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'verbose' in out
        assert isinstance(out['verbose'], bool)

        # inverse_transform()
        # TJRT should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X, None), TJRT)

        # reset()
        assert isinstance(TestCls.reset(), TJRT)

        # score()
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(verbose=True), TJRT)
        assert TestCls.verbose is True
        assert isinstance(TestCls.set_params(verbose=False), TJRT)
        assert TestCls.verbose is False

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = TJRT(**_kwargs)
        TestCls.fit(_X, None)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(_X), list)

        TestCls.reset()
        TestCls.fit(_X)

        # fit()
        assert isinstance(TestCls.fit(_X), TJRT)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        out = TestCls.get_params(True)
        assert isinstance(out, dict)
        assert 'remove_empty_rows' in out
        assert isinstance(out['remove_empty_rows'], bool)

        # inverse_transform()
        # TJRT should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(_X), TJRT)

        # reset()
        assert isinstance(TestCls.reset(), TJRT)
        TestCls.fit(_X)

        # score()
        assert TestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TestCls.set_params(verbose=True), TJRT)
        assert TestCls.verbose is True
        assert isinstance(TestCls.set_params(verbose=False), TJRT)
        assert TestCls.verbose is False

        # transform()
        assert isinstance(TestCls.transform(_X), list)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, _X, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = TJRT(**_kwargs).fit(_X, None)
        TransformedTestCls = TJRT(**_kwargs).fit(_X, None)

        # here is a good place to test reset()
        assert not hasattr(TransformedTestCls, 'DELETE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'REPLACE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SKIP_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SPLIT_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'KNOWN_WORDS_')
        assert not hasattr(TransformedTestCls, 'LEXICON_ADDENDUM_')
        TransformedTestCls.reset()
        assert not hasattr(TransformedTestCls, 'DELETE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'REPLACE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SKIP_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SPLIT_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'KNOWN_WORDS_')
        assert not hasattr(TransformedTestCls, 'LEXICON_ADDENDUM_')

        TransformedTestCls.transform(_X)

        assert hasattr(TransformedTestCls, 'DELETE_ALWAYS_')
        assert hasattr(TransformedTestCls, 'REPLACE_ALWAYS_')
        assert hasattr(TransformedTestCls, 'SKIP_ALWAYS_')
        assert hasattr(TransformedTestCls, 'SPLIT_ALWAYS_')
        assert hasattr(TransformedTestCls, 'KNOWN_WORDS_')
        assert hasattr(TransformedTestCls, 'LEXICON_ADDENDUM_')

        TransformedTestCls.reset()

        assert not hasattr(TransformedTestCls, 'DELETE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'REPLACE_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SKIP_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'SPLIT_ALWAYS_')
        assert not hasattr(TransformedTestCls, 'KNOWN_WORDS_')
        assert not hasattr(TransformedTestCls, 'LEXICON_ADDENDUM_')

        TransformedTestCls.transform(_X)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        # fit()
        assert isinstance(TransformedTestCls.fit(_X), TJRT)

        TransformedTestCls.transform(_X, None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # TJRT should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(_X), TJRT)
        TransformedTestCls.transform(_X)

        # score()
        assert TransformedTestCls.score(_X, None) is None

        # set_params()
        assert isinstance(TransformedTestCls.set_params(verbose=True), TJRT)
        assert TransformedTestCls.verbose is True
        assert isinstance(TransformedTestCls.set_params(verbose=False), TJRT)
        assert TransformedTestCls.verbose is False

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(_X), list)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM




