# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence
)

from .....base._check_1D_str_sequence import check_1D_str_sequence



def _val_1D_X(
    _X: Sequence[str],
    _require_all_finite:bool = True
) -> None:
    """Validate X.

    Must be 1D list-like of strings. Can be empty.

    Parameters
    ----------
    _X : Sequence[str]
        The text data.
    _require_all_finite : bool, default=True
        Whether to block non-finite values such as nan or infinity
        (True) or allow (False).

    Returns
    -------
    None

    """


    check_1D_str_sequence(_X, require_all_finite=_require_all_finite)






