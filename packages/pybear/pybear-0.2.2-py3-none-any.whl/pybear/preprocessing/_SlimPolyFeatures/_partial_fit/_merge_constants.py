# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import PolyConstantsType

import numbers

import numpy as np


def _merge_constants(
    _old_constants: PolyConstantsType | None,
    _new_constants: PolyConstantsType,
    _rtol: numbers.Real,
    _atol: numbers.Real
) -> PolyConstantsType:
    """Merge the constants found in the current partial fit with those
    found in previous partial fits.

    The number of constant columns can only stay the same or decrease on
    later partial fits, never increase.

    This works for both `X_constants_` and `poly_constants_`.

    Parameters
    ----------
    _old_constants : PolyConstantsType | None
        The column indices of constant columns found in previous partial
        fits and the values in the columns.
    _new_constants : PolyConstantsType
        The column indices of constant columns found in the current
        partial fit and the values in the columns.
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.

    Returns
    -------
    _final_constants : PolyConstantsType
        The compiled column indices and values of constant columns found
        over all partial fits.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_old_constants, (dict, type(None)))
    if _old_constants and len(_old_constants):
        for _tuple in _old_constants:
            assert isinstance(_tuple, tuple)
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    assert isinstance(_new_constants, dict)    # can never be None
    if len(_new_constants):
        for _tuple in _new_constants:
            assert isinstance(_tuple, tuple)
            assert all(map(isinstance, _tuple, (int for _ in _tuple)))

    try:
        float(_rtol)
        float(_atol)
        if isinstance(_rtol, bool) or isinstance(_atol, bool):
            raise Exception
    except:
        raise AssertionError
    assert _rtol >= 0
    assert _atol >= 0
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # if _old_constants is None, can only be the first pass, so just
    # return _new_constants
    if _old_constants is None:
        return _new_constants
    # if _old_constants is not None, then cannot be the first pass, and
    # if _old_constants is empty, then there were no constants previously
    # and there cannot be new constants
    elif _old_constants == {}:
        return _old_constants
    else:  # _old_constants is dict that is not empty

        # Constant columns can only stay the same or decrease on later
        # partial fits, never increase.
        _final_constants: PolyConstantsType = {}

        for _col_idx_tuple, _value in _old_constants.items():

            # for a column of constants to carry forward, the currently
            # found indices must be in the previously found indices, and
            # the value of the constant must be the same

            if _col_idx_tuple in _new_constants:
                # need to handle nan - dont use dict.get here
                if str(_value) == 'nan' and \
                        str(_new_constants[_col_idx_tuple]) == 'nan':
                    _final_constants[_col_idx_tuple] = _value
                elif _new_constants[_col_idx_tuple] == _value:
                    # this should get strings (or ints, or maybe some floats)
                    _final_constants[_col_idx_tuple] = _value
                elif np.isclose(
                    _new_constants[_col_idx_tuple],
                    _value,
                    rtol=_rtol,
                    atol=_atol
                ):
                    # this should get floats
                    _final_constants[_col_idx_tuple] = _value


        # verify that outgoing constants were in old and new constants:
        for _col_idx_tuple, _value in _final_constants.items():
            assert _col_idx_tuple in _old_constants
            assert _col_idx_tuple in _new_constants
            # need to handle nan
            if str(_value) == 'nan':
                assert str(_value) == str(_old_constants[_col_idx_tuple])
                assert str(_value) == str(_new_constants[_col_idx_tuple])
            else:
                try:
                    float(_value)
                    is_num = True
                except:
                    is_num = False

                if is_num:
                    assert np.isclose(_value, _old_constants[_col_idx_tuple])
                    assert np.isclose(_value, _new_constants[_col_idx_tuple])
                elif not is_num:
                    assert _value == _old_constants[_col_idx_tuple]
                    assert _value == _new_constants[_col_idx_tuple]


        return _final_constants




