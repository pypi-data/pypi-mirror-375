# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XContainer

import warnings

import numpy as np
import pandas as pd
import polars as pl



def _val_X(
    _X: XContainer
) -> None:
    """Validate the container type of the data.

    Cannot be None. Otherwise, `X` can be a numpy ndarray, a pandas
    dataframe, polars dataframe, or any scipy sparse matrix / array.

    All other validation of the data is handled in the individual
    methods by pybear.base.validate_data.

    Parameters
    ----------
    _X : XContainer of shape (n_samples, n_features)
        The data.

    Returns
    -------
    None

    """


    if not isinstance(_X, (np.ndarray, pd.DataFrame, pl.DataFrame)) \
            and not hasattr(_X, 'toarray'):
        raise TypeError(
            f"invalid container for X: {type(_X)}. \nX must be numpy array, "
            f"pandas dataframe, polars dataframe, or scipy sparce matrix / array."
        )

    if isinstance(_X, np.rec.recarray):
        raise TypeError(
            f"numpy recarrays are not accepted. "
            f"\npass your data as a standard numpy array."
        )

    if np.ma.isMaskedArray(_X):
        warnings.warn(
            f"numpy masked arrays are not blocked but they are not "
            f"tested. \nuse them at your own risk."
        )




