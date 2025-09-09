# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from ...__shared._validation._any_integer import _val_any_integer



def _val_n(
    _n: int
) -> None:
    """Validate 'n'. Must be an integer >= 1.

    Parameters
    ----------
    _n : int
        Something expected to be an integer that is >= 1

    Returns
    -------
    None

    """


    _val_any_integer(_n, 'n', _min=1, _can_be_bool=False)

    if not isinstance(_n, numbers.Integral):
        raise TypeError(f"'n' must be an integer >= 1")



