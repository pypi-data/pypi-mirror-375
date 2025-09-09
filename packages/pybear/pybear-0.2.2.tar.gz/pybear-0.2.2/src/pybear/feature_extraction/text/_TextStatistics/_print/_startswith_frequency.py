# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np

from .._validation._startswith_frequency import _val_startswith_frequency



def _print_startswith_frequency(
    startswith_frequency: dict[str, int],
    lp: int,
    rp: int
) -> None:
    """Print the `startswith_frequency_` attribute to screen.

    Parameters
    ----------
    startswith_frequency : dict[str, int]
        The dictionary holding the unique first characters and the number
        of times those characters appeared in the first position for
        every string fitted on the `TextStatistics` instance.
    lp : int
        The left padding for the display.
    rp : int
        The right padding for the display.

    Returns
    -------
    None

    """


    _val_startswith_frequency(startswith_frequency)

    _UNIQUES = np.fromiter(startswith_frequency, dtype=f"<U1")
    # DONT USE np.int8 OR 16! NUMBERS TOO BIG!
    _COUNTS = np.fromiter(startswith_frequency.values(), dtype=np.uint32)

    COUNT_MASK = np.flip(np.argsort(_COUNTS))
    COUNT_SORTED_DICT = dict((zip(_UNIQUES[COUNT_MASK], _COUNTS[COUNT_MASK])))
    COUNT_SORTED_KEYS = np.fromiter(COUNT_SORTED_DICT.keys(), dtype='<U1')

    ALPHA_MASK = np.argsort(_UNIQUES)
    ALPHA_SORTED_DICT = dict((zip(_UNIQUES[ALPHA_MASK], _COUNTS[ALPHA_MASK])))
    ALPHA_SORTED_KEYS = np.fromiter(ALPHA_SORTED_DICT.keys(), dtype='<U1')


    del _UNIQUES, _COUNTS, COUNT_MASK, ALPHA_MASK

    print(f'\nOVERALL FIRST CHARACTER FREQUENCY:')

    for i in range(len(COUNT_SORTED_DICT)):
        _count_key = COUNT_SORTED_KEYS[i]
        _alpha_key = ALPHA_SORTED_KEYS[i]

        print(lp * ' ' + f"'{_count_key}' :".ljust(rp//2), end='')
        print(f'{COUNT_SORTED_DICT[_count_key]}'.ljust(rp//2), end='')
        print(lp * ' ' + f"'{_alpha_key}' :".ljust(rp//2), end='')
        print(f'{ALPHA_SORTED_DICT[_alpha_key]}')

    del _count_key, _alpha_key
    del COUNT_SORTED_DICT, COUNT_SORTED_KEYS, ALPHA_SORTED_DICT, ALPHA_SORTED_KEYS



