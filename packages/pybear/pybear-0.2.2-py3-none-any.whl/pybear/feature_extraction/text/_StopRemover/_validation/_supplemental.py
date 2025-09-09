# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

from .....base._check_1D_str_sequence import check_1D_str_sequence



def _val_supplemental(_supplemental: Sequence[str] | None) -> None:
    """Validate `supplemental`.

    Must be Sequence[str] or None.

    Parameters
    ----------
    _supplemental : Sequence[str] | None
        Stop words that are supplemental from being removed.

    Returns
    -------
    None

    """


    if _supplemental is None:
        return


    check_1D_str_sequence(_supplemental, require_all_finite=False)






