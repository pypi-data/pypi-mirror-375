# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)
from .._type_aliases import XContainer

from ...__shared._validation._2D_X import _val_2D_X
from ._sep import _val_sep



def _validation(
    _X: XContainer,
    _sep: str | Sequence[str]
) -> None:
    """Centralized hub for validation.

    See the individual modules for details.

    Parameters
    ----------
    _X : XContainer
        The (possibly ragged) 2D text data to be joined along rows into
        a 1D list of strings.
    _sep : str | Sequence[str] - The string character or 1D vector of
        string characters to insert between strings in each row of the
        given 2D text data. If a sequence of strings, the number of
        entries must equal the number of rows in the data.

    Returns
    -------
    None

    """


    _val_2D_X(_X, _require_all_finite=False)

    _val_sep(_sep, _X)









