# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from .._type_aliases import OverallStatisticsType


def _print_overall_statistics(
    overall_statistics: OverallStatisticsType,
    lp: int,
    rp: int
) -> None:
    """Print the `overall_statistics_` attribute to screen.

    Parameters
    ----------
    overall_statistics : dict[str, numbers.Real]
        The dictionary holding statistics about all the strings fitted
        on the `TextStatistics` instance, such as number of strings,
        average length of strings, maximum length string, etc.
    lp : int
        The left padding for the display.
    rp : int
        The right padding for the display.

    Returns
    -------
    None

    """


    print(f'\nSTATISTICS:')
    for _description, _value in overall_statistics.items():
        print(f' ' * lp + str(_description).ljust(2 * rp), _value)






