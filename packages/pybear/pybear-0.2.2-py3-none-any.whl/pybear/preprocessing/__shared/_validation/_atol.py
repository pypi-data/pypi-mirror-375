# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np



def _val_atol(_atol: numbers.Real) -> None:
    """Verify atol is a non-boolean, non-negative, real number that is
    accepted by numpy allclose.

    Parameters
    ----------
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.

    Return
    ------
    None

    """


    err_msg = (f"'atol' must be a non-boolean, non-negative, real number "
               f"that is accepted by numpy allclose.")


    if not isinstance(_atol, numbers.Real):
        raise TypeError(err_msg)

    if isinstance(_atol, bool):
        raise ValueError(err_msg)

    if _atol < 0:
        raise ValueError(err_msg)

    X1 = np.random.uniform(0, 1, 20)

    np.allclose(X1, X1, rtol=1e-6, atol=_atol)

    del X1




