# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence
)

from .....base._check_dtype import check_dtype



def _val_1D_2D_X(
    _X: Sequence[str] | Sequence[Sequence[str]],
    _require_all_finite:bool = True
) -> None:
    """Validate X.

    Must be 1D list-like or (possibly ragged) 2D array-like
    of strings. Can be empty.

    Parameters
    ----------
    _X : Sequence[str] | Sequence[Sequence[str]]
        The text data.
    _require_all_finite : bool, default=True
        Whether to block non-finite values such as nan or infinity
        (True) or allow (False).

    Returns
    -------
    None

    """


    check_dtype(_X, allowed='str', require_all_finite=_require_all_finite)






