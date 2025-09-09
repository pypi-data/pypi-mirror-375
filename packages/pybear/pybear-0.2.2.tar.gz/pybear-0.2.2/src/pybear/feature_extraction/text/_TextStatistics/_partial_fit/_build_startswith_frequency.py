# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._validation._string_frequency import _val_string_frequency



def _build_startswith_frequency(
    _string_frequency: dict[str, int]
) -> dict[str, int]:
    """Build a dictionary that contains the first character of every
    string in `_string_frequency` as keys and the number of times that
    that character appears as the first character of a string as the
    values.

    Parameters
    ----------
    _string_frequency : dict[str, int]
        The dictionary holding the unique strings passed to the current
        partial fit and their respective frequencies.

    Returns
    -------
    _startswith_frequency: dict[str, int]
        A dictionary that holds the first characters of every string
        passed to this partial fit and their respective number of
        appearances in the first position as values.

    """


    _val_string_frequency(_string_frequency)


    _startswith_frequency: dict[str: int] = {}

    for _string, _ct in _string_frequency.items():

        if len(_string) == 0:
            continue

        _startswith_frequency[str(_string[0])] = \
            int(_startswith_frequency.get(str(_string[0]), 0) + _ct)


    return _startswith_frequency


