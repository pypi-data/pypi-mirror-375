# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_int import (
    IntDataType,
    IntGridType
)

import numpy as np

from ._int_linspace_gap_gt_1_soft import _int_linspace_gap_gt_1_soft



def _int_linspace_gap_gt_1_hard(
    _SINGLE_GRID: IntGridType,
    _posn: int,
    _hard_min: IntDataType,
    _hard_max: IntDataType
) -> tuple[IntDataType, IntDataType]:
    """Determine the left and right bounds using
    :func:`_int_linspace_gap_gt_1_soft` then truncate left and right as
    necessary based on `_hard_min` and `_hard_max`. Interstitial values
    are determined by another module.

    Parameters
    ----------
    _SINGLE_GRID : IntGridType
        The last round's search grid for a single integer parameter.
        `_SINGLE_GRID` must be sorted ascending, and is presumed to be
        by :func:`_param_conditioning._params` (at least initially).
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _hard_min : IntDataType
        The minimum value in the first round's search grid. Ignored if
        not hard.
    _hard_max : IntDataType
        The maximum value in the first round's search grid. Ignored if
        not hard.

    Returns
    -------
    __ : tuple[IntDataType, IntDataType]
        _left : IntDataType
            The minimum value for the next search grid after application
            of the hard minimum.
        _right : IntDataType
            The maximum value for the next search grid after application
            of the hard maximum.

    """

    # _hard_min < 1 handled by _validate_int_float_linlogspace, but do it
    # again here anyway

    if _hard_min < 1:
        raise ValueError(f"hard min < 1")

    if (np.array(_SINGLE_GRID) < _hard_min).any():
        raise ValueError(f"_SINGLE_GRID < hard min")

    if (np.array(_SINGLE_GRID) > _hard_max).any():
        raise ValueError(f"_SINGLE_GRID > hard max")


    _left, _right = _int_linspace_gap_gt_1_soft(_SINGLE_GRID, _posn)


    # apply hard min and max

    _left = max(_hard_min, _left)
    _right = min(_hard_max, _right)


    return _left, _right






