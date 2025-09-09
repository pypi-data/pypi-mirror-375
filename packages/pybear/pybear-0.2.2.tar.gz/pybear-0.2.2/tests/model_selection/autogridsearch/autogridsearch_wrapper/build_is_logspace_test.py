# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper.\
    _build_is_logspace import _build_is_logspace



class TestBuildIsLogspace:

    # there is no _validation on _build_is_logspace

    # "string" cannot be logspace
    # "soft" & "hard" CAN BE LOGSPACES, BUT "fixed" CANNOT
    # if 0 in the space, cannot be logspace
    # if 2 or less points in points, cannot be logspace
    # IF IS LOGSPACE, PUT IN THE SIZE OF THE GAP (bool(>0) WILL RETURN True)


    def test_accuracy_1(self):

        _params_1 = {'a': [['x','y','z'], 3, 'fixed_string']}

        _expected_is_logspace = {'a': False}

        assert _build_is_logspace(_params_1) == _expected_is_logspace


    def test_accuracy_2(self):
        _params_2 = {'b': [[1, 2, 3, 4], [4, 4, 4], 'fixed_integer']}

        _expected_is_logspace = {'b': False}

        assert _build_is_logspace(_params_2) == _expected_is_logspace


    def test_accuracy_3(self):
        _params_3 = {'c': [np.logspace(-4,4,9), [9,9,9], 'soft_float']}

        _expected_is_logspace = {'c': 1.0}

        assert _build_is_logspace(_params_3) == _expected_is_logspace


    def test_accuracy_4(self):
        _params_4 = {'d': [[1, 10, 100], [3, 3, 3], 'hard_integer']}

        _expected_is_logspace = {'d': 1.0}

        assert _build_is_logspace(_params_4) == _expected_is_logspace


    def test_accuracy_5(self):
        _params_5 = {'e': [[0, 1, 10, 100], [4, 4, 4], 'soft_float']}

        _expected_is_logspace = {'e': False}

        assert _build_is_logspace(_params_5) == _expected_is_logspace


    def test_accuracy_6(self):

        _params_6 = {'f': [[1, 10], [2,2,3], 'soft_integer']}

        _expected_is_logspace = {'f': False}

        assert _build_is_logspace(_params_6) == _expected_is_logspace


    def test_accuracy_7(self):

        _params_7 = {'g': [[5], [1,1,1], 'soft_integer']}

        _expected_is_logspace = {'g': False}

        assert _build_is_logspace(_params_7) == _expected_is_logspace


    def test_accuracy_8(self):
        _params_8 = {'i': [np.logspace(-5, 5, 11), [11, 11], 'fixed_float']}

        _expected_is_logspace = {'i': False}

        assert _build_is_logspace(_params_8) == _expected_is_logspace


    def test_accuracy_9(self):
        _params_9 = {'j': [[10, 100, 1000], [3, 3], 'soft_integer']}

        _expected_is_logspace = {'j': 1.0}

        assert _build_is_logspace(_params_9) == _expected_is_logspace


    def test_accuracy_10(self):
        _params_10 = {'k': [np.logspace(-10, 10, 11), [11, 11], 'soft_float']}

        _expected_is_logspace = {'k': 2.0}

        assert _build_is_logspace(_params_10) == _expected_is_logspace


    def test_accuracy_11(self):
        _params_11 = {'l': [['1', '10', '100'], 3, 'fixed_string']}

        _expected_is_logspace = {'l': False}

        assert _build_is_logspace(_params_11) == _expected_is_logspace


    def test_accuracy_12(self):
        _params_12 = {'m': [[11, 12, 13], [3,3], 'fixed_integer']}

        _expected_is_logspace = {'m': False}

        assert _build_is_logspace(_params_12) == _expected_is_logspace


    def test_accuracy_13(self):
        _params_13 = {'n': [np.logspace(-10,-4, 7), [7,7], 'hard_float']}

        _expected_is_logspace = {'n': 1.0}

        assert _build_is_logspace(_params_13) == _expected_is_logspace


    def test_accuracy_14(self):

        _params_14 = {'h': [np.linspace(-10, 10, 5), [5, 5, 5], 'hard_float']}

        _expected_is_logspace = {'h': False}

        assert _build_is_logspace(_params_14) == _expected_is_logspace









