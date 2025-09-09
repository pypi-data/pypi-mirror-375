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



def _int_grid_mapper(
    _left: IntDataType,
    _right: IntDataType,
    _points: int
) -> IntGridType:
    """Given a left and right (minimum and maximum) value for a range,
    populate that range inclusive of `_left` and `_right` with the
    number of `_points` (approximately).

    Parameters
    ----------
    _left : IntDataType
        Left bound of the range.
    _right : IntDataType
        Right bound of the range.
    _points : int
        Number of points to put in the range; this algorithm will attempt
        to come as close as possible to this number and also preserve
        equal intervals as much as possible.

    Returns
    -------
    _OUT_GRID : IntGridType
        List of integers fulfilling the input criteria.

    """

    _left = int(_left)
    _right = int(_right)
    _points = int(_points)


    _len = _right - _left + 1

    if ((_len % 2 == 1) and (_points > (_right - _left) / 2 + 1)) or \
        ((_len % 2 == 0) and (_points > _len / 2)):

        _OUT_GRID = np.linspace(_left, _right, _right - _left + 1)

    else:
        _span = int(_right - _left)

        if _span == 0:
            raise ValueError(f"_right - _left == 0, meaning 1 point")

        elif _span == 1:
            _OUT_GRID = np.linspace(_left, _right, 2)

        elif _span == 2:
            _OUT_GRID = np.linspace(_left, _right, 3)

        elif _span == 3:
            _OUT_GRID = np.linspace(_left, _right, 4)

        else:

            # _points CANNOT BE 0, 1

            _OUT_GRID = np.arange(
                _left,
                _right + 1,
                int((_right - _left) / (_points - 1))
            )

            if _right not in _OUT_GRID:
                if _right - 1 in _OUT_GRID:
                    _OUT_GRID = np.insert(
                        _OUT_GRID[:-1],
                        len(_OUT_GRID[:-1]),
                        _right,
                        axis=0
                    )
                else:
                    _OUT_GRID = np.insert(
                        _OUT_GRID,
                        len(_OUT_GRID),
                        _right,
                        axis=0
                    )

    _OUT_GRID = list(map(int, _OUT_GRID.tolist()))


    return _OUT_GRID








