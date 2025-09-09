# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._validation._character_frequency import _val_character_frequency



def _merge_character_frequency(
    _current_character_frequency: dict[str, int],
    _character_frequency: dict[str, int]
) -> dict[str, int]:
    """Merge the unique first characters and counts in the current
    partial fit's character frequency dictionary with those found in
    all previous partial fits of the TextStatistics instance.

    Parameters
    ----------
    _current_character_frequency : dict[str, int]
        The unique characters and their counts found in the current
        partial fit.
    _character_frequency : dict[str, int]
        The unique characters and their counts found in all previous
        partial fits on the `TextStatistics` instance.

    Returns
    -------
    _character_frequency : dict[str, int]
        The merged unique characters and counts for all strings seen
        across all partial fits of the `TextStatistics` instance.

    """

    _val_character_frequency(_current_character_frequency)

    # _character_frequency will be {} on first pass
    _val_character_frequency(_character_frequency)


    for k, v in _current_character_frequency.items():

        _character_frequency[str(k)] = (_character_frequency.get(str(k), 0) + v)


    return _character_frequency





