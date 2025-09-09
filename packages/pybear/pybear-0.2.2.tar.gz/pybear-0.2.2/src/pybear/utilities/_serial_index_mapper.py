# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from typing import Sequence

import numbers

import numpy as np



def serial_index_mapper(
    shape:Sequence[int],
    positions:Sequence[int]
) -> list[tuple[int, ...]]:
    """Map serial index positions to their zero-based Cartesian
    coordinates in an object of the given shape.

    For example in a 2D array of shape (3,3):
        serial index position 1 maps to (0,1)

        serial index position 5 maps to (1,2)

    In a 3D array of shape (2,2,2):
        serial index position 5 maps to (1, 0, 1)

    Parameters
    ----------
    shape : Sequence[int, ...]
        The dimensions of the object to map into.
    positions : Sequence[int]
        Vector of serialized index positions.

    Returns
    -------
    coordinates : list[tuple[int, ...]]
        The zero-based Cartesian coordinates for each given serialized
        index position.

    Examples
    --------
    >>> from pybear.utilities import serial_index_mapper
    >>> shape = (3,3,3)
    >>> positions = [4, 15, 25]
    >>> coordinates = serial_index_mapper(shape, positions)
    >>> print(coordinates)
    [(0, 1, 1), (1, 2, 0), (2, 2, 1)]

    """

    # shape ** * ** * ** * ** * ** ** * ** * ** * ** * ** ** * ** * ** *
    err_msg = (f"'shape' must be non-empty 1D list-like containing "
               f"non-negative integers")

    try:
        if isinstance(shape, (dict, str, type(None))):
            raise Exception
        shape = np.array(list(shape))
        if len(shape) == 0:
            raise UnicodeError
        if not np.array_equiv(shape, shape.ravel()):
            raise UnicodeError
        if not all(map(isinstance, shape, (numbers.Integral for i in shape))):
            raise UnicodeError
        if any([i < 0 for i in shape]):
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg
    # END shape ** * ** * ** * ** * ** * ** * ** * ** * ** ** * ** * **

    # positions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** ** * **
    err_msg = (f"'positions' must be non-empty 1D array-like "
               f"containing non-negative integers")

    try:
        if isinstance(positions, (dict, str, type(None))):
            raise Exception
        positions = np.array(list(positions))
        if len(positions) == 0:
            raise UnicodeError
        if not np.array_equiv(positions, positions.ravel()):
            raise UnicodeError
        if not all(map(isinstance, positions, (numbers.Integral for i in positions))):
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg


    if any(map(lambda x: x < 0 or x > np.prod(shape), positions)):
        raise ValueError(
            f"a serialized index position is out of bounds for an object "
            f"of size {np.prod(shape)}"
        )
    # END positions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def _recursive(
        _posn: int,
        _coordinates: list[int],
        ctr: int
    ) -> tuple[int, ...]:

        if ctr == 100:
            raise RecursionError(f"Recursion depth has surpassed 100")

        if len(_coordinates) == len(shape) - 1:
            _coordinates.append(int(_posn))
            return tuple(_coordinates)
        else:
            # len(COORDINATE) is the axis we are looking to find next
            _axis = len(_coordinates)
            _remaining_axes = shape[_axis + 1:]
            _current_axis_posn = int(_posn // np.prod(_remaining_axes))
            _coordinates.append(_current_axis_posn)
            _positions_consumed = _current_axis_posn * np.prod(_remaining_axes)
            if _positions_consumed == 0:
                # POSN = POSN
                pass
            else:
                _posn = _posn % _positions_consumed

            ctr += 1
            return _recursive(_posn, _coordinates, ctr)


    coordinates = []
    for POSN in positions:
        coordinates.append(_recursive(POSN, [], 1))


    return coordinates





