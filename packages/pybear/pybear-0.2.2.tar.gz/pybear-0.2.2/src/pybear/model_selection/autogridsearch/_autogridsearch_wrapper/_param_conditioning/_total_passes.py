# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _cond_total_passes(
    _total_passes: int
) -> int:
    """Standardize `total_passes` to Python integer.

    Parameters
    ----------
    _total_passes : int
        The number of passes of grid search to perform.

    Returns
    -------
    total_passes : int
        `total_passes` as Python integer.

    """


    return int(_total_passes)



