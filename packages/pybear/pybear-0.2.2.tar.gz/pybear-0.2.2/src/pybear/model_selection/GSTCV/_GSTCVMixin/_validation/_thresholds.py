# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import ThresholdsInputType

import numpy as np



def _val_thresholds(
    _thresholds: ThresholdsInputType,
    _is_from_kwargs: bool,
    _idx: int,
    _must_be_list_like:bool = True
) -> None:
    """Validate `_thresholds`.

    Validate `_thresholds` is

    1) None

    2) a single number

    3) a vector-like of numbers, not empty

    4) 0 <= all numbers <= 1.

    Parameters
    ----------
    _thresholds : ThresholdsInputType
        User-defined threshold(s).
    _is_from_kwargs : bool
        Whether `_thresholds` was passed via the __init__ kwarg or inside
        a param grid.
    _idx : int
        The index of the param grid associated with `_thresholds`.
        If `_thresholds` was not passed in param grid, a dummy `_idx`
        value of 0 is used, and cannot be accessed because the code routes
        through `_is_from_kwargs`.
    _must_be_list_like : bool, default = True
        Whether `thresholds` can be in the raw state as passed to init
        or must have already been conditioned into a list-like.

    Returns
    -------
    None

    """


    if not isinstance(_is_from_kwargs, bool):
        raise TypeError(f"'_is_from_kwargs' must be a bool")

    _err_msg = f"'_idx' must be an int >= 0"
    try:
        float(_idx)
        if isinstance(_idx, bool):
            raise Exception
        if not int(_idx) == _idx:
            raise Exception
        _idx = int(_idx)
        if _idx < 0:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg)
    except Exception as e:
        raise TypeError(_err_msg)

    del _err_msg

    # error messaging *** *** *** *** *** *** *** *** *** *** *** ***
    _base_msg = (
        f"must be \n1 - a 1D list-like of 1 or more numbers or 2 - a "
        f"single number \nand 0 <= threshold(s) <= 1"
    )
    if _is_from_kwargs:
        _err_msg = f"'thresholds' passed as a kwarg " + _base_msg
    else:
        _err_msg = f"'thresholds' passed as param to param_grid[{_idx}] " + _base_msg
    del _base_msg
    # END error messaging *** *** *** *** *** *** *** *** *** *** ***


    if _thresholds is None:
        if _must_be_list_like:
            raise TypeError(f"'thresholds' must be list-like but got {_thresholds}")
        return


    try:
        iter(_thresholds)
        if isinstance(_thresholds, (str, dict)):
            raise UnicodeError
        _dum_thresh = np.array(list(_thresholds), dtype=object)
        if len(_dum_thresh.shape) > 1:
            raise TimeoutError
        if len(_dum_thresh) == 0:
            raise TimeoutError
        try:
            list(map(float, _dum_thresh))
        except:
            raise UnicodeError
        # we have a 1D list-like of things that cast to float
        if any(map(isinstance, _dum_thresh, (bool for i in _dum_thresh))):
            raise UnicodeError
        if any(map(lambda x: x < 0, _dum_thresh)):
            raise TimeoutError
        if any(map(lambda x: x > 1, _dum_thresh)):
            raise TimeoutError
        del _dum_thresh
        # we have a legit 1D of numbers 0 <= x <= 1
        return
    except UnicodeError:
        raise TypeError(_err_msg)
    except TimeoutError:
        raise ValueError(_err_msg)
    except Exception as e:
        if _must_be_list_like:
            raise TypeError(f"'thresholds' must be list-like but got {_thresholds}")
        # is not iterable


    # can only get here if 'thresholds' is not iterable

    try:
        float(_thresholds)
        if isinstance(_thresholds, bool):
            raise Exception
        if _thresholds < 0 or _thresholds > 1:
            raise TimeoutError
        # we have a legit single float
        return
    except TimeoutError:
        raise ValueError(_err_msg)
    except Exception as e:
        raise TypeError(_err_msg)







