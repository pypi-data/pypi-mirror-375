# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XContainer
from typing import Any

import numpy as np
import pandas as pd

from ....utilities._nan_masking import nan_mask

from .._validation._X import _val_X



def _transform(
    _X: XContainer,
    _new_value: Any
) -> XContainer:
    """Map new values to the nan-like representations in X.

    If scipy sparse, cannot be dok or lil, it must have a `data`
    attribute.

    Parameters
    ----------
    _X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The object for which to replace nan-like representations.
    _new_value: Any
        The new value to put in place of the nan-like values. There is
        no validation for this value, the user is free to enter whatever
        they like. If there is a casting problem, i.e., the receiving
        object, the data, will not receive the given value, then any
        exceptions would be raised by the receiving object.

    Returns
    -------
    _X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The original data with new values in the locations previously
        occupied by nan-like values.

    """


    _val_X(_X)


    if isinstance(_X, (list, tuple)):
        _og_format = type(_X)
        # do nan_mask first on og_format so it will trip on ragged built-in
        _MASK = nan_mask(_X)
        _X = np.array(_X)
        _dim = len(_X.shape)
        _X[_MASK] = _new_value
        del _MASK
        if _dim == 1:
            _X = _og_format(_X)
        elif _dim == 2:
            _X = _og_format(map(_og_format, _X))
        del _og_format, _dim
    elif isinstance(_X, (np.ndarray, pd.Series, pd.DataFrame)):
        _X[nan_mask(_X)] = _new_value
    elif hasattr(_X, 'toarray'):
        # for scipy, need to mask the 'data' attribute
        _X.data[nan_mask(_X.data)] = _new_value
    elif hasattr(_X, 'clone'):
        _og_type = type(_X)
        _X = _X.to_numpy().copy()
        _X[nan_mask(_X)] = _new_value
        _X = _og_type(_X)
        del _og_type
    else:
        raise TypeError(f"unknown container {type(_X)} in transform.")


    return _X


