# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
import numpy.typing as npt

import numbers
import uuid

import numpy as np

from ....utilities import nan_mask



def _is_constant(
    _column: npt.NDArray[numbers.Number],
    _equal_nan: bool,
    _rtol: numbers.Real,
    _atol: numbers.Real
) -> uuid.UUID | Any:
    """Determine if a column holds a single value, subject to `_rtol`,
    `_atol`, and `_equal_nan`.

    If there is a single value, return the value. Otherwise, return a
    uuid4.

    Get the mean of all the values and compare against each of the
    values; if all the values are within rtol / atol of the mean, then
    the column is constant.

    If no nan-like values are present then the operation is
    straightforward as above. When nan-like values are present and
    `_equal_nan` is False, then the column is not constant. If
    `_equal_nan` is True, then perform the above operations on the
    non-nan-like values; if the column contains all nan-likes then
    return the nan value.

    Parameters
    ----------
    _column : NDArray[numbers.Number]
        A single column, drawn from `X` or produced by a product of
        multiple columns from `X`, as a numpy array.
    _equal_nan : bool
        If `_equal_nan` is True, exclude nan-likes from computations
        that discover constant columns. This essentially assumes that
        the nan value would otherwise be equal to the mean of the non-nan
        values in the same column. If `_equal_nan` is False and any
        value in a column is nan, do not assume that the nan value is
        equal to the mean of the non-nan values in the same column, thus
        making the column non-constant. This is in line with the normal
        numpy handling of nan values.
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.

    Returns
    -------
    out : uuid.uuid4 | Any
        If the column is not constant, returns a uuid4 identifier; if it
        is constant, returns the constant value.

    """


    # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    assert isinstance(_column, np.ndarray)
    assert isinstance(_equal_nan, bool)
    try:
        float(_rtol)
        assert _rtol >= 0
        float(_atol)
        assert _atol >= 0
    except:
        raise ValueError(
            f"'rtol' and 'atol' must be real, non-negative numbers"
        )

    # END validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    _nan_mask = nan_mask(_column)
    # if the column is all nans, just short circuit out
    if all(_nan_mask):
        return _column[0] if _equal_nan else uuid.uuid4()


    _has_nans = any(_nan_mask)

    # 4 cases:
    # has nan and _equal_nan
    # has nan and not _equal_nan
    # no nan and _equal_nan
    # no nan and not _equal_nan

    if _has_nans:
        if not _equal_nan:
            out = uuid.uuid4()
        elif _equal_nan:
            _not_nan_mask = np.logical_not(nan_mask(_column))
            _mean_value = np.mean(_column[_not_nan_mask].astype(np.float64))
            _allclose = np.allclose(
                _mean_value,
                _column[_not_nan_mask].astype(np.float64), # float64 is important
                rtol=_rtol,
                atol=_atol,
                equal_nan=True
            )

            out = _mean_value if _allclose else uuid.uuid4()
            del _not_nan_mask, _mean_value, _allclose

    elif not _has_nans:
        # no nans, _equal_nan doesnt matter
        _mean_value = np.mean(_column.astype(np.float64)) # float64 is important
        _allclose = np.allclose(
            _column.astype(np.float64),    # float64 is important
            _mean_value,
            rtol=_rtol,
            atol=_atol
        )
        out = _mean_value if _allclose else uuid.uuid4()
        del _mean_value, _allclose

    else:
        raise Exception(f"algorithm failure")


    del _has_nans, _nan_mask

    return out






