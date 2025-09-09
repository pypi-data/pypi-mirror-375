# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from pybear.feature_extraction.text._TextStatistics._validation._validation \
    import _validation


import pytest



class TestValidation:


    # most of the work is handled by the submodules. just make sure this
    # works and passes all good.


    @pytest.mark.parametrize('_X',
        (list('abc'), tuple('abcd'), set('abcde'), [list('abc'), list('abcde')])
    )
    @pytest.mark.parametrize('_store_uniques', (True, False))
    def test_passes(self, _X, _store_uniques):

        out = _validation(
            _X,
            _store_uniques
        )


        assert out is None











