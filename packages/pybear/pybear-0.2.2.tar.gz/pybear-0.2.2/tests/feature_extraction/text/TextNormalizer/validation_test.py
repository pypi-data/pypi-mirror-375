# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextNormalizer._validation import _validation



class TestValidation:



    # the individual validation modules handle the brunt
    # check the _validation passes good stuff




    @pytest.mark.parametrize('X',
        (list('abcde'), list((list('abc'), list('def'))), [1,2,3], [[1,2], [3,4]])
    )
    @pytest.mark.parametrize('upper', (True, False, None, -2.7, 'trash', [0,1]))
    def test_accuracy(self, X, upper):

        _will_raise = False

        if not isinstance(upper, (type(None), bool)):
            _will_raise = True

        if not all(map(isinstance, X, ((str, list) for _ in X))):
            _will_raise = True

        try:
            __ = X[0][0]
            if not isinstance(__, str):
                _will_raise = True
        except:
            pass


        if _will_raise:
            with pytest.raises(TypeError):
                _validation(X, upper)
        else:
            assert _validation(X, upper) is None








