# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from .._type_aliases import CombinationsType

import numbers

import numpy as np
import joblib

from ._parallel_column_comparer import _parallel_column_comparer



@joblib.wrap_non_picklable_objects
def _parallel_chunk_comparer(
    _chunk1: npt.NDArray[numbers.Number],
    _chunk1_X_indices: CombinationsType,
    _chunk2: npt.NDArray[numbers.Number],
    _chunk2_X_indices: CombinationsType,
    _rtol: numbers.Real,
    _atol: numbers.Real,
    _equal_nan: bool
) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Compare the columns in `_chunk1` against the columns in `_chunk2`
    for equality, subject to `_rtol`, `_atol`, and `_equal_nan`.
    `_chunk1` and `_chunk2` must be ndarray.

    Parameters
    ----------
    _chunk1 : npt.NDArray[numbers.Number]
        A chunk of polynomial columns made from X to be compared
        column-by-column against another chunk of polynomial columns
        made from X for equality.
    _chunk1_X_indices : CombinationsType
        The column indices in X that made each respective column in
        `_chunk1`.
    _chunk2 : npt.NDArray[numbers.Number]
        The other chunk of polynomial columns made from X.
    _chunk2_X_indices : CombinationsType
        The column indices in X that made each respective column in
        `_chunk2`.
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _equal_nan : bool
        When comparing pairs of columns row by row:

        If `_equal_nan` is True, exclude from comparison any rows where
        one or both of the values is/are nan. If one value is nan, this
        essentially assumes that the nan value would otherwise be the
        same as its non-nan counterpart. When both are nan, this
        considers the nans as equal (contrary to the default numpy
        handling of nan, where numpy.nan != numpy.nan) and will not in
        and of itself cause a pair of columns to be considered unequal.
        If equal_nan is False and either one or both of the values in
        the compared pair of values is/are nan, consider the pair to be
        not equivalent, thus making the column pair not equal. This is
        in line with the normal numpy handling of nan values.

    Return
    ------
    _pairs : list[tuple[tuple[int, ...], tuple[int, ...]]]
        The polynomial column indices for the pairs of columns that are
        equal between `_chunk1` and `_chunk2`.

    """


    # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    assert isinstance(_chunk1, np.ndarray)
    assert isinstance(_chunk2, np.ndarray)

    assert isinstance(_chunk1_X_indices, tuple)
    assert all(map(
        isinstance, _chunk1_X_indices, (tuple for i in _chunk1_X_indices)
    ))
    assert len(_chunk1_X_indices) == _chunk1.shape[1]

    assert isinstance(_chunk2_X_indices, tuple)
    assert all(map(
        isinstance, _chunk2_X_indices, (tuple for i in _chunk2_X_indices)
    ))
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
    for _chunk1_idx, _X1_idxs in enumerate(_chunk1_X_indices):

        _column1 = _chunk1[:, _chunk1_idx].ravel()

        for _chunk2_idx, _X2_idxs in enumerate(_chunk2_X_indices):

            # do not double count. which half of the triangle that is
            # skipped depends on how the chunks are made in _get_dupls.
            # _get_dupls is scanning the upper right triangle of the grid,
            # so skip any remnants that are from the lower left.
            if len(_X2_idxs) < len(_X1_idxs):
                continue
            if len(_X1_idxs) == len(_X2_idxs) and _X2_idxs <= _X1_idxs:
                continue

            _column2 = _chunk2[:, _chunk2_idx].ravel()

            if _parallel_column_comparer(
                _column1, _column2, _rtol, _atol, _equal_nan
            ):
                _pairs.append((_X1_idxs, _X2_idxs))


    return _pairs



