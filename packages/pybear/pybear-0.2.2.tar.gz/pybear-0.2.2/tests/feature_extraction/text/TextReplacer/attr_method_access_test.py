# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextReplacer.TextReplacer import TextReplacer
from pybear.base import is_fitted



# TextReplacer is always "fit"
class TestAttrAccess:


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_list():
        return np.random.choice(
            list('abcdefghijklmnop'),
            (10,),
            replace=True
        ).tolist()


    # attrs
    # [
    #     'replace',
    #     'case_sensitive',
    #     'flags'
    # ]


    @pytest.mark.parametrize('has_seen_data', (True, False))
    def test_attr_access(self, has_seen_data, _X_list):

        TestCls = TextReplacer(replace=(' ', ','))

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # all attrs should be accessible always
        assert getattr(TestCls, 'replace') == (' ', ',')
        assert getattr(TestCls, 'case_sensitive') is True
        assert getattr(TestCls, 'flags') is None



# TextReplacer is always "fit"
class TestMethodAccess:


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_list():
        return np.random.choice(list('abcdefghijklmnop'), (10,), replace=True).tolist()


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


        TestCls = TextReplacer(replace=(re.compile('[a-m]'), ''))

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        with pytest.raises(NotImplementedError):
            getattr(TestCls, 'get_metadata_routing')()

        out = getattr(TestCls, 'get_params')()
        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        for param in ['replace', 'case_sensitive', 'flags']:
            assert param in out
        assert out['replace'] == (re.compile('[a-m]'), '')
        assert out['case_sensitive'] is True
        assert out['flags'] is None

        out = getattr(TestCls, 'set_params')(**{'replace': ('A', '')})
        assert isinstance(out, TextReplacer)
        assert TestCls.replace == ('A', '')

         # v v v v v must see X every time, put these last v v v v v v v

        out = getattr(TestCls, 'transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        out = getattr(TestCls, 'score')(_X_list)
        assert out is None

        out = getattr(TestCls, 'fit')(_X_list)
        assert isinstance(out, TextReplacer)

        out = getattr(TestCls, 'partial_fit')(_X_list)
        assert isinstance(out, TextReplacer)

        out = getattr(TestCls, 'fit_transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))




