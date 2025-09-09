# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Any
import numpy.typing as npt

import numbers

import numpy as np
import joblib

from ._parallel_column_comparer import _parallel_column_comparer



@joblib.wrap_non_picklable_objects
def _parallel_chunk_comparer(
    _chunk1: npt.NDArray[Any],
    _chunk1_X_indices: tuple[int, ...],
    _chunk2: npt.NDArray[Any],
    _chunk2_X_indices: tuple[int, ...],
    _rtol: numbers.Real,
    _atol: numbers.Real,
    _equal_nan: bool
) -> list[tuple[int, int]]:
    """Compare the columns in `chunk1` against the columns in `chunk2`
    for equality, subject to rtol, atol, and equal_nan. `chunk1` and
    `chunk2` must be ndarray.

    Parameters
    ----------
    _chunk1 : npt.NDArray[Any]
        A chunk of columns from `X` to be compared column-by-column
        against another chunk of columns from `X` for equality.
    _chunk1_X_indices : tuple[int, ...]
        The `X` column indices that correspond to the columns in `chunk1`.
    _chunk2 : npt.NDArray[Any]
        The other chunk of columns from `X`.
    _chunk2_X_indices : tuple[int, ...]
        The `X` column indices that correspond to the columns in `chunk2`.
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _equal_nan : bool
        When comparing pairs of columns row by row:

        If `equal_nan` is True, exclude from comparison any rows where
        one or both of the values is/are nan. If one value is nan, this
        essentially assumes that the nan value would otherwise be the
        same as its non-nan counterpart. When both are nan, this
        considers the nans as equal (contrary to the default numpy
        handling of nan, where numpy.nan != numpy.nan) and will not in
        and of itself cause a pair of columns to be considered unequal.
        If `equal_nan` is False and either one or both of the values in
        the compared pair of values is/are nan, consider the pair to be
        not equivalent, thus making the column pair not equal. This is
        in line with the normal numpy handling of nan values.

    Returns
    -------
    _pairs : list[tuple[int, int]]
        The `X` column indices for the pairs of columns that are equal
        between `chunk1` and `chunk2`.

    """


    # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    assert isinstance(_chunk1, np.ndarray)
    assert isinstance(_chunk2, np.ndarray)

    assert isinstance(_chunk1_X_indices, tuple)
    assert all(map(isinstance, _chunk1_X_indices, [int] * _chunk1.shape[1]))
    assert len(_chunk1_X_indices) == _chunk1.shape[1]

    assert isinstance(_chunk2_X_indices, tuple)
    assert all(map(isinstance, _chunk2_X_indices, [int] * _chunk2.shape[1]))
    assert len(_chunk2_X_indices) == _chunk2.shape[1]

    try:
        float(_rtol)
        assert _rtol >= 0
        float(_atol)
        assert _atol >= 0
    except:
        raise ValueError(
            f"'rtol' and 'atol' must be real, non-negative numbers"
        )

    assert isinstance(_equal_nan, bool)
    # END validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    _pairs = []
    for _chunk1_idx, _X1_idx in enumerate(_chunk1_X_indices):

        _column1 = _chunk1[:, _chunk1_idx].ravel()

        for _chunk2_idx, _X2_idx in enumerate(_chunk2_X_indices):

            if _X2_idx <= _X1_idx:
                # do not double count
                continue

            _column2 = _chunk2[:, _chunk2_idx].ravel()


            if _parallel_column_comparer(
                _column1, _column2, _rtol, _atol, _equal_nan
            ):
                _pairs.append((_X1_idx, _X2_idx))


    return _pairs



