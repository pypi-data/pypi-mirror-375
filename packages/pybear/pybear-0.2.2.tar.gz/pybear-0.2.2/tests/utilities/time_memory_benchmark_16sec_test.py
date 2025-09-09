# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

import io
import sys

import numpy as np

from pybear.utilities._benchmarking import time_memory_benchmark as tmb



@pytest.fixture
def good_args():
    return (
        ('incrementer', lambda x: x + 1, [3], {}),
        ('doubler', lambda x: 2 * x, [7], {}),
        ('tripler', lambda x: 3 * x, [2], {}),
        ('subtracter', lambda x: x - 1, [9], {})
    )



class TestArgs:


    def test_args_must_have_quad_format(self, good_args):
        tmb(*good_args, number_of_trials=2, rest_time=0.1, verbose=0)


    def test_must_have_args(self):
        with pytest.raises(ValueError):
            tmb([])


    def test_arg_length(self):
        with pytest.raises(ValueError):
            tmb(('some_fxn', lambda r: np.pi * r**2, [1]))


    @pytest.mark.parametrize('name', ('some_fxn', lambda r: np.pi * r**2, [1], {}))
    @pytest.mark.parametrize('function', ('some_fxn', lambda r: np.pi * r**2, [1], {}))
    @pytest.mark.parametrize('args', ('some_fxn', lambda r: np.pi * r**2, [1], {}))
    @pytest.mark.parametrize('kwargs', ('some_fxn', lambda r: np.pi * r**2, [1], {}))
    def test_arg_input_types(self, name, function, args, kwargs):

        if name=='some_fxn' and callable(function) and args==[1] and kwargs=={}:
            tmb(
                (name, function, args, kwargs),
                number_of_trials=1,
                rest_time=0,
                verbose=0
            )
        else:
            with pytest.raises(TypeError):
                tmb(
                    (name, function, args, kwargs),
                    number_of_trials=1,
                    rest_time=0,
                    verbose=0
                )


class TestTrials:

    def test_accepts_integer_greater_than_zero(self, good_args):
        tmb(*good_args, number_of_trials=3, rest_time=0.1, verbose=0)


    @pytest.mark.parametrize('num_trials', ('bad', -1, 0, np.pi, 11.33, []))
    def test_rejects_non_integers_and_less_than_zero(self, good_args, num_trials):
        with pytest.raises(ValueError):
            tmb(*good_args, number_of_trials=num_trials, rest_time=0.02, verbose=0)


class TestRestTime:

    def test_accepts_number_greater_than_zero(self, good_args):
        tmb(*good_args, number_of_trials=3, rest_time=0.123, verbose=0)


    @pytest.mark.parametrize('rest_time', ('bad', -1, -np.pi, []))
    def test_rejects_non_numbers_and_less_than_zero(self, good_args, rest_time):
        with pytest.raises(ValueError):
            tmb(*good_args, number_of_trials=3, rest_time=rest_time, verbose=0)


class TestVerbose:

    def test_accepts_number_greater_than_zero(self, good_args, capfd):
        # BLOCK stdout FROM PRINTING TO SCREEN DURING TEST BY CAPTURING
        stdout_buffer = io.StringIO()
        sys.stdout = stdout_buffer
        tmb(*good_args, number_of_trials=2, rest_time=0.02, verbose=np.pi)


    @pytest.mark.parametrize('verbose', ('bad', -1, -np.pi, []))
    def test_rejects_non_numbers_and_less_than_zero(self, good_args, verbose):
        with pytest.raises(ValueError):
            tmb(*good_args, number_of_trials=3, rest_time=0.02, verbose=verbose)


class TestResults:


    @pytest.mark.parametrize('number_of_trials', (2,4,6))
    @pytest.mark.parametrize('number_of_fxns', (1,2,3))
    def test_results(self, number_of_fxns, number_of_trials, good_args):

        args = [good_args[i] for i in range(number_of_fxns)]
        RESULT = tmb(
            *args,
            number_of_trials=number_of_trials,
            rest_time=0.03,
            verbose=0
        )

        # MUST HAVE SHAPE:
        # axis_0 = time, mem
        # axis_1 = number_of_functions
        # axis_2 = number_of_trials
        assert RESULT.shape == (2, number_of_fxns, number_of_trials)

        # ALL TIMES MUST BE >= 0 (SOMETIMES ANOMALIES HAPPEN WITH MEMORY)
        assert (RESULT[0, :, :] > 0).all()





