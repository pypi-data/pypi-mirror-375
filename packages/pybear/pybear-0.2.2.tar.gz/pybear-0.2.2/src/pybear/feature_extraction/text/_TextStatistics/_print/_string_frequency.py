# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

import numpy as np

from .._validation._n import _val_n
from .._validation._string_frequency import _val_string_frequency



def _print_string_frequency(
    string_frequency:dict[str, int],
    lp:int,
    rp:int,
    n:int = 10
) -> None:
    """Print the `string_frequency_` attribute to screen.

    Only available if TS parameter `store_uniques` is True. If False,
    `string_frequency` is empty, so print a message that uniques are not
    available.

    Parameters
    ----------
    string_frequency : dict[str, int]
        The dictionary holding the unique strings and their respective
        counts for all strings fitted on the `TextStatistics` instance.
    lp : int
        The left padding for the display.
    rp : int
        The right padding for the display.
    n : int, default = 10
        The number of most frequent strings to print.

    Returns
    -------
    None

    """


    _val_string_frequency(string_frequency)
    _val_n(n)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    if not len(string_frequency):
        print(
            "Parameter 'store_uniques' is False, individual uniques have "
            "not been retained for display."
        )
        return


    _max_len = max(map(len, string_frequency))

    _UNIQUES = np.fromiter(string_frequency, dtype=f"<U{_max_len}")
    _COUNTS = np.fromiter(string_frequency.values(), dtype=np.uint32)

    n = min(n, len(_UNIQUES))
    print(f'\n TOP {n} STRING FREQUENCY OF {len(_UNIQUES)}:')
    MASK = np.flip(np.argsort(_COUNTS))[:n]

    print(lp * ' ' + (f'STRING').ljust(_max_len + rp) + f'FREQUENCY')
    for i in range(n):
        print(lp * ' ' + f'{_UNIQUES[MASK][i]}'.ljust(_max_len + rp), end='')
        print(f'{_COUNTS[MASK][i]}')

    del _UNIQUES, _COUNTS, MASK









