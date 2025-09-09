# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np



def _cond_verbose(
    _verbose: numbers.Real
) -> int:
    """Condition `verbose`, the amount of verbosity to display to screen
    during the grid search.

    Take in a number-like and return an integer in the range of 0 to 10,
    inclusive. False is converted to zero, True is converted to 10.
    Floats are rounded to integers. Numbers greater than 10 are set to
    10.

    Parameters
    ---------
    _verbose : numbers.Real
        The amount of verbosity to display to screen during the grid
        search.

    Returns
    -------
    _verbose : int
        `verbose` scaled from 0 to 10.

    """


    if _verbose is True:
        _verbose = 10
    elif _verbose is False:
        _verbose = 0
    elif _verbose is np.nan:
        _verbose = 0

    _verbose = min(int(round(_verbose, 0)), 10)


    return _verbose







