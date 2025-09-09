# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._validation._string_frequency import _val_string_frequency



def _build_character_frequency(
    _string_frequency: dict[str, int]
) -> dict[str, int]:
    """Build a dictionary that contains all the unique characters in
    `_string_frequency` as keys and the number of times that that
    character appears as the values.

    Parameters
    ----------
    _string_frequency : dict[str, int]
        The dictionary holding the unique strings passed to the current
        partial fit and their respective frequencies.

    Returns
    -------
    _character_frequency: dict[str, int]
        A dictionary that holds the unique characters passed to this
        partial fit and their respective number of appearances as values.

    """

    _val_string_frequency(_string_frequency)


    _character_frequency: dict[str: int] = {}

    for _string, _ct in _string_frequency.items():
        for _char in str(_string):
            _character_frequency[_char] = \
                (_character_frequency.get(_char, 0) + _ct)

    _character_frequency = dict((zip(
        map(str, _character_frequency.keys()),
        map(int, _character_frequency.values())
    )))


    return _character_frequency


