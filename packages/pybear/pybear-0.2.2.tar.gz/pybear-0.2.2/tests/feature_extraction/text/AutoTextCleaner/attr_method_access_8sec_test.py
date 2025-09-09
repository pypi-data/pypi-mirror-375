# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers
import re

import numpy as np

from pybear.feature_extraction.text._AutoTextCleaner.AutoTextCleaner import \
    AutoTextCleaner as ATC

from pybear.feature_extraction.text._TextStatistics.TextStatistics import \
    TextStatistics as TS

from pybear.feature_extraction.text._TextLookup.TextLookupRealTime import \
    TextLookupRealTime as TLRT

from pybear.base import is_fitted



@pytest.fixture(scope='module')
def _X_list():
    return np.random.choice(
        list('abcdefghijklmnop'),
        (10,),
        replace=True
    ).tolist()



# AutoTextCleaner is always "fit"
class TestAttrAccess:


    # attrs
    # [
    #     'n_rows_'
    #     'row_support_',
    #     'before_statistics_',
    #     'after_statistics_',
    #     'lexicon_lookup_'
    # ]


    @pytest.mark.parametrize('has_seen_data', (True, False))
    def test_attr_access(self, has_seen_data, _X_list):

        # lexicon_lookup and before/after statistics must be on for
        # these tests

        TestCls = ATC(
            remove=(' ', ',', '.', ';'),
            lexicon_lookup={'auto_delete': True},
            get_statistics={'before': False, 'after': False}

        )

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # before transform

        # all params should be accessible always
        assert getattr(TestCls, 'remove') == (' ', ',', '.', ';')
        assert getattr(TestCls, 'case_sensitive') is True
        assert getattr(TestCls, 'global_flags') is None

        # all of these need a transform to have been done and cannot be set
        for _attr in [
            'n_rows_', 'row_support_', 'before_statistics_',
            'after_statistics_', 'lexicon_lookup_'
        ]:
            with pytest.raises(AttributeError):
                getattr(TestCls, _attr)

            with pytest.raises(AttributeError):
                setattr(TestCls, _attr, any)

        # END before transform
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        TestCls.transform(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # after transform

        # all params should be accessible always
        assert getattr(TestCls, 'remove') == (' ', ',', '.', ';')
        assert getattr(TestCls, 'case_sensitive') is True
        assert getattr(TestCls, 'global_flags') is None

        # 'n_rows_' needs a transform to have been done
        out = getattr(TestCls, 'n_rows_')
        assert isinstance(out, numbers.Integral)
        assert out == len(_X_list)

        # 'n_rows_' cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'n_rows_', any)

        # 'row_support_' needs a transform to have been done
        out = getattr(TestCls, 'row_support_')
        assert isinstance(out, np.ndarray)
        assert len(out) == len(_X_list)

        # 'row_support_' cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'row_support_', any)

        # 'before_statistics_' must be enabled in the 'get_statistics'
        # parameter; needs a transform to have been done
        out = getattr(TestCls, 'before_statistics_')
        assert isinstance(out, TS)

        # 'before_statistics_' cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'before_statistics_', any)

        # 'after_statistics_'  must be enabled in the 'get_statistics'
        # parameter; needs a transform to have been done
        out = getattr(TestCls, 'after_statistics_')
        assert isinstance(out, TS)

        # 'after_statistics_' cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'after_statistics_', any)

        # 'lexicon_lookup_'  must be enabled in the 'lexicon_lookup'
        # parameter; needs a transform to have been done
        out = getattr(TestCls, 'lexicon_lookup_')
        assert isinstance(out, TLRT)

        # 'lexicon_lookup_' cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'lexicon_lookup_', any)

        # END after transform
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_before', (True, False, None))
    @pytest.mark.parametrize('_after', (True, False, None))
    def test_conditional_access_to_statistics(
        self, _X_list, _before, _after
    ):

        TestCls = ATC(
            remove=re.compile('[c-f]'), remove_empty_rows=True,
            get_statistics={'before': _before, 'after': _after}
        )

        # before transform should never be accessible
        for _attr in ['before_statistics_', 'after_statistics_']:
            with pytest.raises(AttributeError):
                getattr(TestCls, _attr)

        # after transform should only be accessible if enabled in the
        # 'get_statistics' parameter

        TestCls.transform(_X_list)

        if _before in [True, False]:
            assert isinstance(getattr(TestCls, 'before_statistics_'), TS)
        else:
            with pytest.raises(AttributeError):
                getattr(TestCls, 'before_statistics_')

        if _after in [True, False]:
            assert isinstance(getattr(TestCls, 'after_statistics_'), TS)
        else:
            with pytest.raises(AttributeError):
                getattr(TestCls, 'after_statistics_')


    @pytest.mark.parametrize('_lex_look',
        (
            None,
            {'update_lexicon': True, 'auto_add_to_lexicon': True},
            {'auto_delete': True}
        )
    )
    def test_conditional_access_to_text_lookup(self, _X_list, _lex_look):

        TestCls = ATC(
            remove=re.compile('[c-f]'), remove_empty_rows=True,
            lexicon_lookup=_lex_look
        )

        # before transform should never be accessible
        with pytest.raises(AttributeError):
            getattr(TestCls, 'lexicon_lookup_')

        # after transform should only be accessible if enabled in the
        # 'lexicon_lookup' parameter (is not None)

        TestCls.transform(_X_list)

        if _lex_look is None:
            with pytest.raises(AttributeError):
                getattr(TestCls, 'lexicon_lookup_')
        else:
            assert isinstance(getattr(TestCls, 'lexicon_lookup_'), TLRT)


# AutoTextCleaner is always "fit"
class TestMethodAccess:


    # methods
    # [
    #     'partial_fit',
    #     'fit',
    #     'fit_transform',
    #     'get_params',
    #     'set_params',
    #     'transform',
    #     'score'
    # ]


    @pytest.mark.parametrize('has_seen_data', (True, False))
    def test_access_methods(self, _X_list, has_seen_data):


        TestCls = ATC(replace=(re.compile('[a-m]'), ''))

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        with pytest.raises(NotImplementedError):
            getattr(TestCls, 'get_metadata_routing')()

        out = getattr(TestCls, 'get_params')()
        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        for param in ['replace', 'case_sensitive', 'global_flags']:
            assert param in out


        out = getattr(TestCls, 'set_params')(**{'global_flags': re.I | re.X})
        assert isinstance(out, ATC)
        assert TestCls.global_flags == re.IGNORECASE|re.VERBOSE

         # v v v v v must see X every time, put these last v v v v v v v

        out = getattr(TestCls, 'transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        out = getattr(TestCls, 'score')(_X_list)
        assert out is None

        out = getattr(TestCls, 'fit')(_X_list)
        assert isinstance(out, ATC)

        out = getattr(TestCls, 'partial_fit')(_X_list)
        assert isinstance(out, ATC)

        out = getattr(TestCls, 'fit_transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))





