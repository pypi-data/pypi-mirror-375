# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_total_passes(
    _total_passes: int
) -> None:
    """Validate `total_passes`.

    Must be an integer >= 1.

    Parameters
    ----------
    _total_passes : int
        The number of grid-search passes to run. The actual number of
        passes run can be higher than this number under certain
        circumstances.

    Returns
    -------
    None

    """

    err_msg = f"'total_passes' must be an integer >= 1"
    try:
        float(_total_passes)
        if isinstance(_total_passes, bool):
            raise Exception
        if int(_total_passes) != _total_passes:
            raise Exception
        if _total_passes < 1:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except:
        raise TypeError(err_msg)


    del err_msg



