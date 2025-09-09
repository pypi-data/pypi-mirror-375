# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._validation._ngcallable import \
    _val_ngcallable

import pytest



class TestNGCallable:


    @pytest.mark.parametrize('junk_ngcallable',
        (-2.7, -1, 0, 1, 2.7, True, False, 'junk', [0,1], (1,), {1,2}, {'a':1})
    )
    def test_rejects_junk(self, junk_ngcallable):

        with pytest.raises(TypeError):
            _val_ngcallable(junk_ngcallable)



    def test_accepts_callable_None(self):

        assert _val_ngcallable(None) is None

        assert _val_ngcallable(lambda x, y: f"{x}__{y}") is None

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        def crazy_function(*args) -> str:

            return "@".join(args)


        assert _val_ngcallable(crazy_function) is None






