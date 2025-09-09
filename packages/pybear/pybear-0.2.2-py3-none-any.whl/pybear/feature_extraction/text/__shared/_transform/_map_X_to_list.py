# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias
)
import numpy.typing as npt

import numpy as np
import pandas as pd
import polars as pl



Python1DTypes: TypeAlias = list[str] | tuple[str] | set[str]

Numpy1DTypes: TypeAlias = npt.NDArray[str]

Pandas1DTypes: TypeAlias = pd.Series

Polars1DTypes: TypeAlias = pl.Series

Dim1Types: TypeAlias = \
    Python1DTypes | Numpy1DTypes | Pandas1DTypes | Polars1DTypes

Python2DTypes: TypeAlias = Sequence[Sequence[str]]

Numpy2DTypes: TypeAlias = npt.NDArray[str]

Pandas2DTypes: TypeAlias = pd.DataFrame

Polars2DTypes: TypeAlias = pl.DataFrame

Dim2Types: TypeAlias = \
    Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes



def _map_X_to_list(
    _X: Dim1Types | Dim2Types
) -> list[str] | list[list[str]]:
    """
    Convert the given 1D or (possibly ragged) 2D container of strings
    into list[str] for 1D or list[list[str]] for 2D.

    Parameters
    ----------
    _X : Dim1Types | Dim2Types
        The 1D or (possibly ragged) 2D data container to be converted to
        list[str] or list[list[str]].

    Returns
    -------
    _X : list[str] | list[list[str]]
        The data container mapped to list[str] for 1D or list[list[str]]
        for 2D containers.

    Notes
    -----

    **Type Aliases**

    Python1DTypes:
        list[str] | tuple[str] | set[str]

    Numpy1DTypes:
        numpy.ndarray[str]

    Pandas1DTypes:
        pandas.Series

    Polars1DTypes:
        polars.Series

    Dim1Types:
        Python1DTypes | Numpy1DTypes | Pandas1DTypes | Polars1DTypes

    Python2DTypes:
        Sequence[Sequence[str]]

    Numpy2DTypes:
        numpy.ndarray[str]

    Pandas2DTypes:
        pandas.DataFrame

    Polars2DTypes:
        polars.DataFrame

    Dim2Types:
        Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes

    """


    if hasattr(_X, 'shape'):
        if isinstance(_X, pd.DataFrame):
            # let np cast nan-likes
            _X = _X.to_numpy().astype(str)
            _X = list(map(list, _X))
        elif isinstance(_X, pl.DataFrame):
            # let  np cast nan-likes
            _X = _X.to_numpy().astype(str)
            _X = list(map(list, _X))
        elif len(_X.shape) == 1:
            _X = list(map(str, np.array(list(_X)).astype(str).tolist()))
        elif len(_X.shape) == 2:
            _X = list(map(lambda x: list(map(str, x)), _X))
        else:
            raise ValueError(
                f'disallowed data container dimensions ({len(_X.shape)}) '
                f'in _map_X_to_list()'
            )
    else:
        # does not have 'shape' attribute. must be py built-in.
        # could have nans in it.
        # if can cast to ndarray must be 1D or non-ragged 2D.
        try:
            # if it does cast, it should coerce any nans, then convert it
            # back to py list
            _X = np.array(list(_X)).astype(str)
            if len(_X.shape) == 1:
                _X = list(map(str, _X.tolist()))
            elif len(_X.shape) == 2:
                _X = list(map(lambda x: list(map(str, x)), _X))
            else:
                raise ValueError(
                    f'disallowed data container dimensions ({len(_X.shape)}) '
                    f'in _map_X_to_list()'
                )
        except:
            # must be ragged 2D py
            # loop over the inner vectors, convert to np.ndarray to let it
            # coerce any nan-likes, then covert back to lists

            _X = list(_X)

            for idx in range(len(_X)):
                _X[idx] = list(map(str, np.array(list(_X[idx])).astype(str).tolist()))


    return _X






