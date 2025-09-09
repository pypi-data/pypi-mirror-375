# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

from ......base._check_1D_str_sequence import check_1D_str_sequence



def _val_skip_always(
    _skip_always: Sequence[str] | None
) -> None:
    """Validate skip_always.

    Must be a 1D sequence of strings or None.

    Parameters
    ----------
    _skip_always : Sequence[str] | None
        A 1D sequence of strings that when there is a case-sensitive
        match against a word in the text, that word is skipped without
        further action and left in the body of text.

    Returns
    -------
    None

    """


    if _skip_always is None:
        return


    check_1D_str_sequence(_skip_always, require_all_finite=True)






