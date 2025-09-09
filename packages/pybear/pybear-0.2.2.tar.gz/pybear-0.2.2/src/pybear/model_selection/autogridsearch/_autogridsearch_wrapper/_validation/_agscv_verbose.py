# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_agscv_verbose(
    _agscv_verbose: bool
) -> None:
    """Validate `agscv_verbose`.

    Must be boolean.

    Parameters
    ----------
    _agscv_verbose : bool
        Whether to display additional helpful information during an
        agscv session.

    Returns
    -------
    None

    """


    if not isinstance(_agscv_verbose, bool):
        raise TypeError(f"'agscv_verbose' must be boolean")




