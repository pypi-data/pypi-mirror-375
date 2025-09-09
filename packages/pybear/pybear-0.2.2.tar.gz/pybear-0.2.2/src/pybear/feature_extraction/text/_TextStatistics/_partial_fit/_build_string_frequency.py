# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import numbers

from .....base._check_1D_str_sequence import check_1D_str_sequence



def _build_string_frequency(
    STRINGS:Sequence[str],
    case_sensitive:bool = False
) -> dict[str, int]:
    """Build a dictionary of the unique strings in `STRINGS` and their
    counts.

    Parameters
    ----------
    STRINGS : Sequence[str]
        The sequence of strings currently being fitted.
    case_sensitive : bool, default = False
        Whether to preserve the case of the characters when getting the
        uniques. When False, normalize the case of all characters.

    Returns
    -------
    _string_frequency : dict[str, int]
        A dictionary with the unique strings in STRINGS as keys and
        their respective counts as values.

    """


    check_1D_str_sequence(STRINGS, require_all_finite=False)

    if len(STRINGS) == 0:
        raise ValueError(
            f"'strings' must be passed as a list-like vector of "
            f"strings, cannot be empty."
        )

    if not isinstance(case_sensitive, bool):
        raise TypeError(f"'case_sensitive' must be boolean")

    # END VALIDATION ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _string_frequency = {}
    if case_sensitive:
        for _string in STRINGS:
            _string_frequency[str(_string)] = \
                _string_frequency.get(str(_string), 0) + 1
    elif not case_sensitive:
        for _string in STRINGS:
            _string_frequency[str(_string).upper()] = \
                _string_frequency.get(str(_string).upper(), 0) + 1

    # alphabetize
    for k in sorted(_string_frequency.keys()):
        _string_frequency[str(k)] = _string_frequency.pop(str(k))


    return _string_frequency






