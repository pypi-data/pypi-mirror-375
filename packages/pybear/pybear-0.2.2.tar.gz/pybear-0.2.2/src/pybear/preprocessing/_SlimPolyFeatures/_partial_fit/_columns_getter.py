# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from pybear.preprocessing._SlimPolyFeatures._type_aliases import (
    CombinationsType,
    InternalXContainer
)

import numbers

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ....utilities._nan_masking import nan_mask



def _columns_getter(
    _X: InternalXContainer,
    _col_idxs: tuple[int, ...] | CombinationsType
) -> npt.NDArray[np.float64]:
    """Handles the mechanics of extracting and multiplying polynomial
    columns from the various allowed data container types.

    The container must be numpy ndarray, pandas dataframe, polars
    dataframe, or scipy csc only. Return extracted column(s) as a numpy
    array in row-major order. In the case of scipy sparse, the columns
    are converted to dense.

    Parameters
    ----------
    _X : InternalXContainer
        The data to extract columns from. The container must be numpy
        ndarray, pandas dataframe, polars dataframe, or scipy csc only.
        This module expects `_X` to be in a valid state when passed, and
        will not condition it.
    _col_idxs : tuple[int, ...] | CombinationsType
        The column index / indices to extract from `_X`.

    Returns
    -------
    _columns : NDArray[np.float64]
        The columns and/or polynomial columns from `_X` corresponding to
        the given indices in row-major order.

    """


    # validation & conditioning ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )

    # _col_idxs can be a tuple of poly idx ints, or a tuple
    # holding tuples of poly idx ints
    assert isinstance(_col_idxs, tuple)
    assert len(_col_idxs), f"'_col_idxs' cannot be empty"
    if all(map(
        isinstance, _col_idxs, (numbers.Integral for i in _col_idxs)
    )):
        assert all(map(lambda x: x in range(_X.shape[1]), _col_idxs)), \
            f"col idx out of range"
        _col_idxs = (_col_idxs, )
    elif all(map(
        isinstance, _col_idxs, (tuple for i in _col_idxs)
    )):
        for _tuple in _col_idxs:
            assert all(map(isinstance, _tuple, (int for i in _tuple)))
            assert all(map(lambda x: x in range(_X.shape[1]), _tuple)), \
                f"col idx out of range"
    else:
        raise TypeError(
            f"'_col_idxs' must be tuple of ints or tuple of tuples of ints"
        )
    # END validation & conditioning ** * ** * ** * ** * ** * ** * ** *

    # create a holder object to catch all the resulting vectors from
    # extraction and multiplication of all the polynomial idxs
    _poly = np.empty((_X.shape[0], 0), dtype=np.float64)

    for _poly_idxs in _col_idxs:

        _poly_idxs = list(_poly_idxs)

        if isinstance(_X, np.ndarray):
            _columns = _X[:, _poly_idxs]
        elif isinstance(_X, pd.DataFrame):
            # additional steps are taken at the bottom of this module if
            # the dataframe has funky nan-likes, causing _poly to leave
            # this step as dtype object
            _columns = _X.iloc[:, _poly_idxs].to_numpy()
        elif isinstance(_X, pl.DataFrame):
            # when pulling the same column 2+ times, polars cannot make
            # df polars.exceptions.DuplicateError: could not create a
            # new DataFrame: column with name 'd61193cc' has more than
            # one occurrence. need a workaround that doesnt copy the
            # full X. pull the unique columns, convert to np, then
            # create the og stack
            _unq_idxs = np.unique(_poly_idxs)
            # need to map idxs in X to future idxs in the uniques slice
            _lookup_dict = {}
            for _new_idx, _old_idx in enumerate(_unq_idxs):
                _lookup_dict[_old_idx] = _new_idx
            _columns = _X[:, _unq_idxs].to_numpy()
            _new_idxs = [int(_lookup_dict[_old_idx]) for _old_idx in _poly_idxs]
            _columns = _columns[:, _new_idxs]
            del _lookup_dict
        elif hasattr(_X, 'toarray'):
            # both _is_constant() and _build_poly() need vectors
            # extracted from ss to be full, not the stacked version
            # (ss.indices & ss.data hstacked). With all the various
            # applications that use _columns_getter, and all the various
            # forms that could be needed at those endpoints, it is
            # simplest just to standardize all to receive dense np, at
            # the cost of slightly higher memory swell than may otherwise
            # be necessary. Extract the columns from scipy sparse as
            # dense ndarray.
            _columns = _X[:, _poly_idxs].toarray()
        else:
            try:
                _columns = np.array(_X[:, _poly_idxs])
            except:
                raise TypeError(
                    f"invalid data container '{type(_X)}' that could not "
                    f"be sliced by numpy-style indexing and converted to "
                    f"ndarray."
                )


        # need to replace junky pdNA, np.prod cant take them.
        try:
            _columns[nan_mask(_columns)] = np.nan
        except:
            pass

        # now that the columns are extracted, multiply thru and stack to _poly
        _poly = np.hstack((_poly, _columns.prod(axis=1).reshape((-1, 1))))


    assert _poly.shape == (_X.shape[0], len(_col_idxs)), \
        f"{_poly.shape=}, ({_X.shape[0]=}, {len(_col_idxs)=})"


    # if pandas had funky nan-likes (or if X was np, ss, or pd, and
    # dtype was passed as object), then the dtype of _poly is
    # guaranteed to be object and ss cant take it. need to convert the
    # dtype to a numeric one. ultimately, for several reasons, the
    # executive decision was made to always build POLY as float64. if
    # there are nans in this, then it must be np.float64 anyway.

    _poly = np.ascontiguousarray(_poly).astype(np.float64)

    return _poly





