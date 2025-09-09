# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._NanStandardizer.NanStandardizer import NanStandardizer
from pybear.base import is_fitted



# NanStandardizer is always "fit"
class TestAttrAccess:


    @pytest.mark.parametrize('has_seen_data', (True, False))
    def test_attr_access(self, has_seen_data, X_np):

        # _attrs
        #     [ 'new_value' ]

        TestCls = NanStandardizer(new_value=99)

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(X_np)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # all attrs should be accessible always
        assert getattr(TestCls, 'new_value') == 99



# NanStandardizer is always "fit"
class TestMethodAccess:


    @pytest.mark.parametrize('has_seen_data', (True, False))
    def test_access_methods(self, X_np, has_seen_data):

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

        TestCls = NanStandardizer(new_value=-1)

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(X_np)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        with pytest.raises(NotImplementedError):
            getattr(TestCls, 'get_metadata_routing')()

        out = getattr(TestCls, 'get_params')()
        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert len(out) == 1
        assert 'new_value' in out
        assert out['new_value'] == -1


        out = getattr(TestCls, 'set_params')(**{'new_value': '314'})
        assert isinstance(out, NanStandardizer)
        assert TestCls.new_value == '314'

         # v v v v v must see X every time, put these last v v v v v v v

        out = getattr(TestCls, 'transform')(X_np)
        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (np.ndarray for _ in out)))


        out = getattr(TestCls, 'score')(X_np)
        assert out is None

        out = getattr(TestCls, 'fit')(X_np)
        assert isinstance(out, NanStandardizer)

        out = getattr(TestCls, 'partial_fit')(X_np)
        assert isinstance(out, NanStandardizer)

        out = getattr(TestCls, 'fit_transform')(X_np)
        assert isinstance(out, np.ndarray)
        assert all(map(isinstance, out, (np.ndarray for _ in out)))





