# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InternalXContainer,
    DataType
)

import itertools

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from .._partial_fit._columns_getter import _columns_getter
from .._partial_fit._parallel_dtypes_unqs_cts import _parallel_dtypes_unqs_cts



def _get_dtypes_unqs_cts(
    _X: InternalXContainer
) -> tuple[str, dict[DataType, int]]:
    """Parallelized collection of dtypes, uniques, and counts for every
    column in `X`.

    Parameters
    ----------
    _X : InternalXContainer
        The data. must be numpy array, pandas dataframe, polars dataframe,
        or scipy csc matrix/array.

    Returns
    -------
    DTYPE_UNQS_CTS_TUPLES : list[tuple[str, dict[DataType, int]]]
        A list of tuples, one tuple for each column in `X`. Each tuple
        holds the MCT-assigned dtype for the column and a dictionary
        with the uniques in the column as keys and their respective
        frequencies as values.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # no longer using joblib. even with sending chunks of X instead of
    # single columns across joblib it still wasnt a benefit. The cost of
    # serializing the data is not worth it for the light task of getting
    # uniques from a column.

    # the original attempt at this was passing all col indices in _X to
    # columns_getter and passing the whole thing as np to _pduc. It
    # turned out that this was creating a brief but huge spike in RAM
    # because a full copy of the entire _X was being made. so trade off
    # by pulling smaller chunks of _X and passing to _pduc... this gives
    # the benefit of less calls to _columns_getter & _pduc than would be
    # if pulling one column at a time, still with some memory spike but
    # much smaller, and get some economy of scale with the speed of
    # scanning a ndarray chunk.
    # number of columns to pull and scan in one pass of the :for: loop
    _n_cols = 10
    DTYPE_UNQS_CTS_TUPLES = []
    for i in range(0, _X.shape[1], _n_cols):
        DTYPE_UNQS_CTS_TUPLES.append(
            _parallel_dtypes_unqs_cts(
                _columns_getter(
                    _X,
                    tuple(range(i, min(i + _n_cols, _X.shape[1])))
                )
            )
        )

    DTYPE_UNQS_CTS_TUPLES = list(itertools.chain(*DTYPE_UNQS_CTS_TUPLES))

    assert all(map(
        isinstance,
        DTYPE_UNQS_CTS_TUPLES,
        (tuple for i in DTYPE_UNQS_CTS_TUPLES)
    ))

    # DTYPE_UNQS_CTS_TUPLES is list[tuple[str, dict[DataType, int]]]
    # the idxs of the list match the column idxs of the data


    return DTYPE_UNQS_CTS_TUPLES




