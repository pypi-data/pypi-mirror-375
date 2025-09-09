# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from numbers import Integral

from pybear.preprocessing._SlimPolyFeatures._validation._degree__min_degree import \
    _val_degree__min_degree



class TestDegree__MinDegree:

    # must be integers >= 0
    # degree must be >= min_degree


    junk = [True, False, 'trash', None, [0,1], {0,1}, {'a':1}, lambda x: x]
    bad = [-3.14, -1, 3.14]
    _min_good = [1, 2, 3]
    _max_good = [2, 3, 4]

    @pytest.mark.parametrize('_degree', junk + bad + _max_good)
    @pytest.mark.parametrize('_min_degree', junk + bad + _min_good)
    def test_validation(self, _degree, _min_degree):

        if isinstance(_degree, bool) or \
            isinstance(_min_degree, bool) or \
            not isinstance(_degree, Integral) or \
            not isinstance(_min_degree, Integral) or \
            _degree not in range(2, 100) or \
            _min_degree not in range(1, 100) or \
            _degree < _min_degree:

            with pytest.raises(ValueError):
                _val_degree__min_degree(
                    _degree,
                    _min_degree
                )

        else:
            _val_degree__min_degree(
                _degree,
                _min_degree
            )










