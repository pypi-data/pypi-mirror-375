# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence
)

from .....base._check_2D_str_array import check_2D_str_array



def _val_2D_X(
    _X: Sequence[Sequence[str]],
    _require_all_finite:bool = True
) -> None:
    """Validate X.

    Must be 2D array-like of strings. Can be empty.

    Parameters
    ----------
    _X : Sequence[Sequence[str]]
        The text data.
    _require_all_finite : bool, default=True
        Whether to block non-finite values such as nan or infinity (True)
        or allow (False).

    Returns
    -------
    None

    """


    check_2D_str_array(_X, require_all_finite=_require_all_finite)






