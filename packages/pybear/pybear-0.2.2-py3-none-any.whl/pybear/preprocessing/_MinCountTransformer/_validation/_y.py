# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import YContainer

import warnings

import numpy as np
import pandas as pd
import polars as pl



def _val_y(
    _y: YContainer
) -> None:
    """Validate the target for the data is a valid data container.

    If y is not passed (i.e is py None) then this validation is bypassed.
    Numpy ndarrays, pandas dataframes, pandas series, polars dataframes,
    and polars series are allowed. This validation is only performed
    for `transform` and is necessary because y may be reduced along the
    sample axis.

    Parameters
    ----------
    _y : YContainer of shape (n_samples, n_features) or (n_samples,)
        The target for the data.

    Returns
    -------
    None

    """


    if not isinstance(
        _y,
        (type(None), np.ndarray, pd.DataFrame, pd.Series,
        pl.DataFrame, pl.Series)
    ):
        raise TypeError(f'invalid data container for y, {type(_y)}.')

    if isinstance(_y, np.rec.recarray):
        raise TypeError(
            f"MCT does not accept numpy recarrays. "
            f"\npass your data as a standard numpy array."
        )

    if np.ma.isMaskedArray(_y):
        warnings.warn(
            f"MCT does not block numpy masked arrays but they are not tested. "
            f"\nuse them at your own risk."
        )



