# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._validation._string_frequency import _val_string_frequency
from .._validation._n import _val_n

from .._get._get_longest_strings import _get_longest_strings



def _print_longest_strings(
    string_frequency:dict[str, int],
    lp:int,
    rp:int,
    n:int = 10
) -> None:
    """Print the longest strings in the 'string_frequency_' attribute
    and their frequencies to screen.

    Only available if TS parameter `store_uniques` is True. If False,
    `string_frequency` is empty, so print a message that uniques are not
    available.

    Parameters
    ----------
    string_frequency : dict[str, int]
        The dictionary holding all the unique strings and their
        frequencies seen by the fitted `TextStatistics` instance.
    lp : int
        The left padding for the display.
    rp : int
        The right padding for the display.
    n : int, default = 10
        The number of longest strings to print to screen.

    Returns
    -------
    None

    """


    _val_string_frequency(string_frequency)


    if not len(string_frequency):
        print(
            "Parameter 'store_uniques' is False, individual uniques have "
            "not been retained for display."
        )
        return

    _val_n(n)


    n = min(n, len(string_frequency))

    longest_string_dict = _get_longest_strings(string_frequency, n)


    print(f'\n TOP {n} LONGEST STRINGS OF {len(string_frequency)}:')

    _max_len = max(map(len, longest_string_dict.keys()))

    print(lp * ' ' + (f'STRING').ljust(_max_len + rp) + f'FREQUENCY')
    for k, v in longest_string_dict.items():
        print(lp * ' ' + f'{k}'.ljust(_max_len + rp) +f'{v}')

    del longest_string_dict, _max_len







