# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import numbers

import numpy as np



def _val_predict_proba(
    _predict_proba: Sequence[numbers.Real],
    _len: int
) -> None:
    """Validate `_predict_proba` is a vector-like of numbers whose
    length matches the rows in X, and 0 <= all numbers <= 1.

    Parameters
    ----------
    _predict_proba : Sequence[numbers.Real]
        The predict proba output of the estimator.
    _len : int
        The number of examples in the X passed to `predict_proba`.

    Returns
    -------
    None

    """


    if not isinstance(_len, numbers.Integral) or isinstance(_len, bool):
        raise TypeError(f"'_len' must be an integer > 0")

    if _len < 1:
        raise ValueError(f"'_len' must be an integer > 0")


    _err_msg = (
        f"the output of the estimator's predict_proba method must "
        f"\n1) be a 1D list-like of numbers and 0 <= numbers <= 1, and "
        f"\n2) have the same length as the number of samples passed to "
        f"predict_proba."
    )


    # if dask, convert to np
    try:
        _dum_pp = _predict_proba.compute()
    except:
        _dum_pp = _predict_proba

    try:
        _dum_pp = _dum_pp.to_numpy()
    except:
        pass



    try:
        iter(_dum_pp)
        if isinstance(_dum_pp, (str, dict)):
            raise Exception
        _dum_pp = np.array(list(_dum_pp), dtype=object)
        if len(_dum_pp.shape) in [1, 2]:
            if len(_dum_pp.shape) == 2 and _dum_pp.shape[1] != 1:
                raise UnicodeError
            _dum_pp = _dum_pp.ravel()
        else:
            raise UnicodeError
        if len(_dum_pp) == 0:
            raise UnicodeError
        try:
            list(map(float, _dum_pp))
        except:
            raise Exception
        # we have a 1D list-like of things that cast to float
        if any(map(isinstance, _dum_pp, (bool for i in _dum_pp))):
            raise UnicodeError
        if any(map(lambda x: x < 0, _dum_pp)):
            raise UnicodeError
        if any(map(lambda x: x > 1, _dum_pp)):
            raise UnicodeError
        del _dum_pp
        # we have a legit 1D of numbers 0 <= x <= 1
        return
    except UnicodeError:
        raise ValueError(_err_msg)
    except Exception as e:
        raise TypeError(_err_msg)


    del _dum_pp





