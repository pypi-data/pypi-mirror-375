# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Iterable

import numpy as np



def _val_y(
    _y: Iterable[int]  # not SKYType... see the notes.
) -> None:
    """Validate `_y`.

    `_y` must be single label and binary in [0, 1]. This validation is
    fairly loose in that it allows *any* 1D container that is binary in
    0 and 1. If there is a problem with the container let the estimator
    raise it.

    Parameters
    ----------
    _y : vector-like of shape (n_samples,) or (n_samples, 1)
        The target for the data.

    Returns
    -------
    None

    """


    # y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    try:
        y_shape = _y.shape
    except:
        try:
            y_shape = np.array(list(_y)).shape
        except:
            raise TypeError(f"'y' must have a 'shape' attribute.")


    _err_msg = (
        f"GSTCV can only perform thresholding on vector-like binary targets "
        f"with values in [0,1]. \nPass 'y' as a vector of 0's and 1's."
    )

    if len(y_shape) == 1:
        pass
    elif len(y_shape) == 2:
        if y_shape[1] != 1:
            raise ValueError(_err_msg)
    else:
        raise ValueError(_err_msg)

    if hasattr(_y, 'shape'):
        _unique = set(np.unique(_y))
    else:
        _unique = set(np.unique(list(_y)))

    if not _unique.issubset({0, 1}):
        raise ValueError(_err_msg)

    del _unique




