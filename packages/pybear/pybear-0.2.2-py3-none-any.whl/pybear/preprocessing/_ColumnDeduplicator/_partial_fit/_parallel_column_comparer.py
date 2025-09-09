# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Any
import numpy.typing as npt

import numbers

import numpy as np

from ....utilities._nan_masking import nan_mask



def _parallel_column_comparer(
    _column1: npt.NDArray[Any],
    _column2: npt.NDArray[Any],
    _rtol: numbers.Real,
    _atol: numbers.Real,
    _equal_nan: bool
) -> list[bool]:
    """ Compare `column1` against `column2` for equality, subject to
    `rtol`, `atol`, and `equal_nan`. `column1` and `column2` must be
    ndarray.

    Parameters
    ----------
    _column1 : npt.NDArray[Any]
        A column from `X` to compare against another column from `X` for
        equality.
    _column2 : npt.NDArray[Any]
        The other column from `X`.
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
    _match : bool
        Whether the pair of columns are equal.

    """


    # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    assert isinstance(_column1, np.ndarray)
    __ = _column1.shape
    assert len(__) == 1 or (len(__) == 2 and __[1] == 1)
    del __
    assert isinstance(_column2, np.ndarray)
    __ = _column2.shape
    assert len(__) == 1 or (len(__) == 2 and __[1] == 1)
    del __

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

    # get dtypes and reshape column1 & column2 ** ** ** ** ** ** ** **
    _column1 = _column1.ravel()

    try:
        # float64 RAISES ValueError ON STR DTYPES, IN THAT CASE MUST BE STR
        _column1.astype(np.float64)
        _column1_is_num = True
    except:
        _column1_is_num = False


    _column2 = _column2.ravel()

    try:
        # float64 RAISES ValueError ON STR DTYPES, IN THAT CASE MUST BE STR
        _column2.astype(np.float64)
        _column2_is_num = True
    except:
        _column2_is_num = False
    # END get dtypes and reshape column1 & column2 ** ** ** ** ** ** **


    MASK1 = nan_mask(_column1)
    MASK2 = nan_mask(_column2)
    NOT_NAN_MASK = np.logical_not((MASK1 + MASK2).astype(bool))
    del MASK1, MASK2

    _match: bool

    if _column1_is_num and _column2_is_num:

        if _equal_nan:
            _match = np.allclose(
                _column1[NOT_NAN_MASK].astype(np.float64),
                _column2[NOT_NAN_MASK].astype(np.float64),
                rtol=_rtol,
                atol=_atol
            )

        elif not _equal_nan:
            _match = np.allclose(
                _column1.astype(np.float64),
                _column2.astype(np.float64),
                rtol=_rtol,
                atol=_atol
            )

    elif not _column1_is_num and not _column2_is_num:

        if _equal_nan:
            _match = np.array_equal(
                _column1[NOT_NAN_MASK].astype(object),
                _column2[NOT_NAN_MASK].astype(object)
            )

        elif not _equal_nan:
            if not all(NOT_NAN_MASK):
                _match = False
            else:
                _match = np.array_equal(
                    _column1.astype(object), _column2.astype(object)
                )

    else:
        # if one column is num and another column is not num, cannot be
        # equal
        _match = False


    del _column1_is_num, _column2_is_num, NOT_NAN_MASK


    return _match



