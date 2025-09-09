# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextLookup._shared._validation. \
    _replace_always import _val_replace_always



class TestReplaceAlways:


    def test_accepts_None(self):

        assert _val_replace_always(None) is None


    @pytest.mark.parametrize('key',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    @pytest.mark.parametrize('value',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    def test_accepts_dict_str_str(self, key, value):

        try:
            {key: value}
        except:
            pytest.skip(reason=f"cant do a test if cant make a dict")


        if isinstance(key, str) and isinstance(value, str):
            assert _val_replace_always({key: value}) is None
        else:
            with pytest.raises(TypeError):
                assert _val_replace_always({key: value}) is None







