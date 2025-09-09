# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

from ......base._check_1D_str_sequence import check_1D_str_sequence



def _val_split_always(
    _split_always: dict[str, Sequence[str]] | None
) -> None:
    """Validate split_always.

    Must be None or a dictionary with strings as keys and sequences of
    strings as values.

    Parameters
    ----------
    _split_always : dict[str, Sequence[str]] | None
        None or a dictionary with strings as keys and sequences of
        strings as values. When a key in the dictionary is a
        case-sensitive match against a word in the text, the matching
        word is removed and the corresponding words in the sequence are
        inserted, starting in the position of the original word.

    Returns
    -------
    None

    """


    if _split_always is None:
        return


    try:
        if not isinstance(_split_always, dict):
            raise Exception
        for k, v in _split_always.items():
            if not isinstance(k, str):
                raise Exception
            try:
                iter(v)
                check_1D_str_sequence(v, require_all_finite=True)
            except:
                raise Exception
    except:
        raise TypeError(
            f"'split_always' must be None or a dictionary with strings "
            f"as keys and sequences of strings as values."
        )





