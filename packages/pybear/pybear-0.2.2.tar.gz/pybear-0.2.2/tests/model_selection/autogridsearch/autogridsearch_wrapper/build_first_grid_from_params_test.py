# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _build_first_grid_from_params import _build



class TestBuild:

    # There is no _validation on the _build module

    def test_accuracy(self):

        _params = {
            'string' : [['a','b','c'], 3, 'fixed_string'],
            'num': [[1,2,3,4], [4,4,4,4,4], 'fixed_integer']
        }

        assert _build(_params) == {0: {'string':['a','b','c'], 'num':[1,2,3,4]}}


    def test_grid_with_two_zeros_in_it(self):

        # this should be allowed to happen. _validation._params should catch
        # duplicates.

        _params = {
            'string' : [['a','b','c'], 3, 'fixed_string'],
            'num': [[0, 0, 1, 2], [4,4,4,4,4], 'fixed_integer']
        }

        assert _build(_params) == {
            0: {'string':['a','b','c'], 'num':[0,0,1,2]}}






