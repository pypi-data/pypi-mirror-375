# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._validation._startswith_frequency import _val_startswith_frequency



def _merge_startswith_frequency(
    _current_startswith_frequency: dict[str, int],
    _startswith_frequency: dict[str, int]
) -> dict[str, int]:
    """Merge the unique first characters and counts in the current
    partial fit's startswith frequency dictionary with those found in
    all previous partial fits of the `TextStatistics` instance.

    Parameters
    ----------
    _current_startswith_frequency : dict[str, int]
        The unique first characters and their counts found in the current
        partial fit.
    _startswith_frequency : dict[str, int]
        The unique first characters and their counts found in all
        previous partial fits on the `TextStatistics` instance.

    Returns
    -------
    _startswith_frequency : dict[str, int]
        The merged unique first characters and counts for all strings
        seen across all partial fits of the `TextStatistics` instance.

    """

    _val_startswith_frequency(_current_startswith_frequency)

    # _startswith_frequency will be {} on first pass
    _val_startswith_frequency(_startswith_frequency)


    for k, v in _current_startswith_frequency.items():

        _startswith_frequency[str(k)] = (_startswith_frequency.get(str(k), 0) + v)


    return _startswith_frequency





