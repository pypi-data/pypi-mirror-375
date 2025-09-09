# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from pybear.utilities._logger import logger
import sys, io



def test_returns_original_function():

    dum_lambda = lambda x: 2*x + 11

    # BLOCK stdout FROM PRINTING TO SCREEN DURING TEST BY CAPTURING
    stdout_buffer = io.StringIO()
    sys.stdout = stdout_buffer

    @logger
    def dum_fxn(value):
        return dum_lambda(value)

    assert dum_lambda(3) == 17
    assert dum_fxn(3) == dum_lambda(3)







