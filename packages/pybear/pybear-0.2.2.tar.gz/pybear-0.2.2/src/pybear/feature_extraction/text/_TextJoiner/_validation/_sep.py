# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)
from .._type_aliases import XContainer

from .....base._check_1D_str_sequence import check_1D_str_sequence



def _val_sep(
    _sep: str | Sequence[str],
    _X: XContainer
) -> None:
    """Validate `sep`.

    Must be a string or a 1D sequence of strings. If a 1D sequence, then
    the length of the sequence must equal the number of rows in `X`.

    Parameters
    ----------
    _sep : str | Sequence[str]
        The character sequence to insert between individual strings
        when joining the 2D input data across rows. If a 1D sequence of
        strings, then the `sep` value in each position is used to join
        the corresponding row in `X`.
    _X : XContainer
        The (possibly ragged) 2D container of text to be joined across
        rows with the `sep` character string(s).

    Returns
    -------
    None

    """


    err_msg = (f"'sep' must be a string or a 1D sequence of strings whose "
               f"length equals the number of rows in X, got {type(_sep)}")

    if isinstance(_sep, str):
        pass
    else:
        check_1D_str_sequence(_sep, require_all_finite=True)

        if hasattr(_X, 'shape') and len(_sep) != _X.shape[0]:
            raise ValueError(err_msg)
        elif len(_sep) != len(_X):
            raise ValueError(err_msg)








