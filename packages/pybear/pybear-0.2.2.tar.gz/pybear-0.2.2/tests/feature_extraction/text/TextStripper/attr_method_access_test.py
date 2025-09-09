# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextStripper.TextStripper import \
    TextStripper
from pybear.base import is_fitted


# TextStripper has no attributes

# TextStripper is always "fit"
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


        TestCls = TextStripper()

        assert is_fitted(TestCls) is True

        if has_seen_data:
            TestCls.fit(_X_list)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        with pytest.raises(NotImplementedError):
            getattr(TestCls, 'get_metadata_routing')()

        out = getattr(TestCls, 'get_params')()
        assert isinstance(out, dict)
        assert len(out) == 0


        out = getattr(TestCls, 'set_params')(**{})
        assert isinstance(out, TextStripper)

         # v v v v v must see X every time, put these last v v v v v v v

        out = getattr(TestCls, 'transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))


        out = getattr(TestCls, 'score')(_X_list)
        assert out is None

        out = getattr(TestCls, 'fit')(_X_list)
        assert isinstance(out, TextStripper)

        out = getattr(TestCls, 'partial_fit')(_X_list)
        assert isinstance(out, TextStripper)

        out = getattr(TestCls, 'fit_transform')(_X_list)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))





