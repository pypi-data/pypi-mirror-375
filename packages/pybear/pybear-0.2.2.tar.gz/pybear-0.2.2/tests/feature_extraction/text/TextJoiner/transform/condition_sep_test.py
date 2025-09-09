# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextJoiner._transform._condition_sep import \
    _condition_sep



class TestConditionSep:

    # there is no validation in _condition_sep

    # simply test that if given a list-like, the original list is returned,
    # if given a string value, a list of that string value is returned.


    @pytest.mark.parametrize('_sep',
        (' ', ', ', '', list('abcd'), tuple('abcd'), set('abcd'))
    )
    def test_accuracy(self, _sep):


        _X_shape = (4, 200)

        out = _condition_sep(_sep, _X_shape[0])

        assert isinstance(out, list)
        assert len(out) == _X_shape[0]
        assert all(map(isinstance, out, (str for _ in out)))

        if isinstance(_sep, str):
            assert np.array_equal(out, [_sep for _ in range(_X_shape[0])])
        else:
            assert np.array_equal(out, list(_sep))






