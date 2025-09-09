# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_int import (
    IntDataType,
    IntGridType
)



def _int_linspace_gap_gt_1_soft(
    _SINGLE_GRID: IntGridType,
    _posn: int,
) -> tuple[IntDataType, IntDataType]:
    """Determine the left and right bounds for a soft linspace integer
    with non-unit interval based on whether the best result from
    `GridSearchCV` landed on a left or right edge or in the middle of
    last round's search grid.

    Apply the universal integer lower bound of 1 to the left bound.
    Interstitial values are determined by another module.

    Parameters
    ----------
    _SINGLE_GRID : IntGridType
        The last round's search grid for a single soft integer parameter.
        `_SINGLE_GRID` must be sorted ascending, and is presumed to be
        by :func:`_param_conditioning._params` (at least initially).
    _posn : int
        The index position in the previous round's grid where the best
        value fell.

    Returns
    -------
    __ : tuple[IntDataType, IntDataType]
        _left : IntDataType
            The minimum value for the next search grid (may be changed
            by another algorithm later).
        _right : IntDataType
            The maximum value for the next search grid (may be changed
            by another algorithm later).

    """

    if _posn == 0:
        _left1 = _SINGLE_GRID[0]
        _right = _SINGLE_GRID[1]
        _left = _left1 - (_right - _left1)
        _right = max(_right - 1, _left1 + 1)
        del _left1

    elif _posn == len(_SINGLE_GRID) - 1:
        _left = _SINGLE_GRID[-2]
        _right1 = _SINGLE_GRID[-1]
        _right = _right1 + (_right1 - _left)
        _left = min(_left + 1, _right1 - 1)
        del _right1

    else:
        _best = _SINGLE_GRID[_posn]
        _left = min(
            # _SINGLE_GRID[_posn - 1] + 1,
            _SINGLE_GRID[_posn - 1] + (_best - _SINGLE_GRID[_posn - 1]) // 2,
            _best - 1
        )
        _right = max(
            # _SINGLE_GRID[_posn + 1] - 1,
            _SINGLE_GRID[_posn + 1] - (_SINGLE_GRID[_posn + 1] - _best) // 2,
            _best + 1
        )


    # apply universal lower bound
    _left = max(1, _left)


    return _left, _right





