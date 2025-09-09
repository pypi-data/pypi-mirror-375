# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_total_passes_is_hard(
    _total_passes_is_hard: bool
) -> None:
    """Validate `_total_passes_is_hard`.

    Must be boolean.

    Parameters
    ----------
    _total_passes_is_hard : bool
        Whether the number of agscv passes is fixed or can increase based
        on the number of shifts needed.

    Returns
    -------
    None

    """


    if not isinstance(_total_passes_is_hard, bool):
        raise TypeError("'total_passes_is_hard' must be boolean")





