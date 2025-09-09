# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np



def _val_rtol(_rtol: numbers.Real) -> None:
    """Verify rtol is a non-boolean, non-negative, real number that is
    accepted by numpy allclose.

    Parameters
    ----------
    _rtol : numbers.Real - The relative difference tolerance for
        equality. Must be a non-boolean, non-negative, real number. See
        numpy.allclose.

    Return
    ------
    None

    """


    err_msg = (f"'rtol' must be a non-boolean, non-negative, real number "
               f"that is accepted by numpy allclose")


    if not isinstance(_rtol, numbers.Real):
        raise TypeError(err_msg)

    if isinstance(_rtol, bool):
        raise ValueError(err_msg)

    if _rtol < 0:
        raise ValueError(err_msg)

    X1 = np.random.uniform(0, 1, 20)

    np.allclose(X1, X1, rtol=_rtol, atol=1e-6)

    del X1




