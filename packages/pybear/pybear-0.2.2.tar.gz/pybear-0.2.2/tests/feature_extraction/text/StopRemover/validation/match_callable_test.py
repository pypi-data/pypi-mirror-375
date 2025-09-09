# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._StopRemover._validation._match_callable \
    import _val_match_callable



class TestMatchCallable:


    @pytest.mark.parametrize('junk_match_callable',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, {'a':1})
    )
    def test_rejects_non_callable_none(self, junk_match_callable):

        with pytest.raises(TypeError):
            _val_match_callable(junk_match_callable)



    def test_accepts_callable_none(self):

        assert _val_match_callable(lambda x, y: x == y) is None

        assert _val_match_callable(None) is None








