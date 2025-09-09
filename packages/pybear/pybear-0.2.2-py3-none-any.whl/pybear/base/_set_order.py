# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Literal
import numpy.typing as npt

import numpy as np

from ._copy_X import copy_X as _copy_X



def set_order(
    X: npt.NDArray,
    *,
    order: Literal['C', 'F']="C",
    copy_X: bool=True
) -> npt.NDArray:
    """Set the memory layout of `X`. `X` must be a numpy ndarray.

    'C' is row-major order, 'F' is column major order.

    For 1D and trivial 2D (shape=(10, 1) or (1, 10)) numpy arrays, the
    'flags' attribute will report both 'C_CONTIGUOUS' and 'F_CONTIGUOUS'
    as True. This is because these arrays are a single continuous block
    of memory with no dimensions to reorder. Both 'C_CONTIGUOUS' and
    'F_CONTIGUOUS' are True because there is no ambiguity in accessing
    elements — the memory layout trivially satisfies both definitions.

    Parameters
    ----------
    X : numpy.ndarray
        The numpy array for which to set the memory layout.
    order : Literal['c', 'C', 'f', 'F']
        The memory layout for `X`. 'C' is row-major order, 'F' is
        column-major order.
    copy_X : bool
        Whether to make a copy of `X` when setting the memory layout or
        operate directly on the passed `X`.

    Returns
    -------
    X : numpy.ndarray
        `X` in the desired memory layout.

    Examples
    --------
    >>> from pybear.base import set_order
    >>> import numpy as np
    >>> X = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.int8)
    >>> print(X.flags['C_CONTIGUOUS'])
    True
    >>> print(X.flags['F_CONTIGUOUS'])
    False
    >>> out = set_order(X, order='F', copy_X=True)
    >>> print(out.flags['C_CONTIGUOUS'])
    False
    >>> print(out.flags['F_CONTIGUOUS'])
    True

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if not isinstance(X, np.ndarray):
        raise TypeError(f"'X' must be a numpy ndarray.")

    err_msg = f"'order' must be a string literal 'C' or 'F', not case sensitive."
    if not isinstance(order, str):
        raise TypeError(err_msg)

    order = order.upper()

    if order not in ['C', 'F']:
        raise ValueError(err_msg)

    del err_msg

    if not isinstance(copy_X, bool):
        raise TypeError(f"'copy_X' must be boolean.")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if copy_X:
        _X = _copy_X(X)
    else:
        _X = X

    if order == 'C':
        _X = np.ascontiguousarray(_X)
    elif order == 'F':
        _X = np.asfortranarray(_X)

    return _X




