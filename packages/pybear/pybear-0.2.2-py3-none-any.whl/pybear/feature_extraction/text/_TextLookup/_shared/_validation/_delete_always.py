# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

from ......base._check_1D_str_sequence import check_1D_str_sequence



def _val_delete_always(
    _delete_always: Sequence[str] | None
) -> None:
    """Validate delete_always.

    Must be a 1D sequence of strings or None.

    Parameters
    ----------
    _delete_always : Sequence[str] | None
        A 1D sequence of strings that when there is a case-sensitive
        match against a word in the text, that word is removed from the
        body of text.

    Returns
    -------
    None

    """


    if _delete_always is None:
        return


    check_1D_str_sequence(_delete_always, require_all_finite=True)




