# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers



def _val_verbose(
    _verbose:numbers.Real,
    _can_be_raw_value:bool = False
) -> None:
    """Validate `verbose`, the amount of verbosity to display to screen
    during the grid search.

    Must be number-like >= 0 , non-numbers are rejected.

    Parameters
    ---------
    _verbose : numbers.Real
        The amount of verbosity to display to screen during the grid
        search.

    Returns
    -------
    None

    """


    _err_msg = f"verbose must be a number-like >= 0. "

    _addon = ''

    try:
        float(_verbose)
        if _verbose < 0:
            raise UnicodeError
        # -- -- for _can_be_raw_value -- -- -- --
        if not _can_be_raw_value:
            _addon = f'got {_verbose} but raw value is disallowed'
            if not isinstance(_verbose, int) or isinstance(_verbose, bool):
                raise Exception
            if _verbose > 10:
                raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg + _addon)
    except Exception as e:
        raise TypeError(_err_msg + _addon)


    del _err_msg





