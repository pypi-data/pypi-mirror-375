# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InternalXContainer,
    KeepType
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from .._partial_fit._columns_getter import _columns_getter

from ....utilities._nan_masking import nan_mask



def _remove_intercept(
    _X_inv: InternalXContainer,
    _keep: KeepType
) -> InternalXContainer:
    """Remove an intercept previously appended by `InterceptManager`.

    If `keep` was a dictionary during fitting/transform, then a column
    of constants was appended to the data after the removal of all
    the other constant columns that were in the data. That column
    needs to be removed first to do an inverse_transform. The core
    IM :func:`_inverse_transform` function expects that that column is
    not present.

    Parameters
    ----------
    _X_inv : XContainer
        Technically, at the point where this module is called in
        `IM.inverse_transform`, `X` is still `X_tr`. `X_tr` is
        midstream in the process of becoming `X_inv`. So although called
        `X_inv` here, it is technically still `X_tr`, which is data that
        has been transformed.
    _keep : KeepType
        The strategy for handling the constant columns. See 'The keep
        Parameter' section for a lengthy explanation of the `keep`
        parameter.

    Returns
    -------
    _X_inv : XContainer
        The transformed data reverted back to the pre-transform state,
        with the full set of original constant columns, if any.

    """


    assert isinstance(_X_inv,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )


    if isinstance(_keep, dict):

        _are_equal = False

        _unqs = np.unique(_columns_getter(_X_inv, _X_inv.shape[1] - 1))

        _key = list(_keep.keys())[0]

        _base_err = (
            f":param: 'keep' is a dictionary but the last column of "
            f"the data to be inverse transformed does not match."
            f"\nkeep={_keep}, but last column "
        )
        if all(nan_mask(_unqs)):
            if all(nan_mask([[_keep[_key]]])):
                _are_equal = True
            else:
                raise ValueError(_base_err + f"is nan.")
        elif len(_unqs) == 1:
            try:
                _are_equal = (float(_keep[_key]) == float(_unqs[0]))
            except:
                _are_equal = (_keep[_key] == _unqs[0])

            if not _are_equal:
                raise ValueError(_base_err + f"value = {_unqs[0]}.")
        else:
            raise ValueError(_base_err + f"is not constant.")

        del _unqs, _base_err


        if _are_equal:
            if isinstance(_X_inv, np.ndarray):
                _X_inv = np.delete(_X_inv, -1, axis=1)
            elif isinstance(_X_inv, pd.DataFrame):
                _X_inv = _X_inv.drop(columns=[_key])
            elif isinstance(_X_inv, pl.DataFrame):
                _X_inv = _X_inv.drop(_key)
            elif hasattr(_X_inv, 'toarray'):
                _X_inv = _X_inv[:, list(range(_X_inv.shape[1] - 1))]
            else:
                raise Exception


    return _X_inv



