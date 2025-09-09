# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XWipContainer


def _transform(
    _X: list[list[str]],
    _sep: list[str]
) -> XWipContainer:
    """Convert each row of strings in `_X` to a single string, joining on
    the string character sequence(s) provided by the `sep` parameter.

    Returns a Python list of strings.

    Parameters
    ----------
    _X : list[list[str]]
        The (possibly ragged) 2D container of text to be joined along
        rows using the `sep` character string(s). `_X` should have
        been converted to a list-of-lists in the transform method of
        the :class:`TextJoiner` main module.
    _sep:
        list[str] - the 1D Python list of strings to use to join the
        strings in the data. The length is identical to the number of
        rows in the data, and each string in _sep is used to join the
        corresponding sequence of strings in the data.

    Returns
    -------
    X_tr : list[str]
        A single list containing strings, one string for each row in the
        original `X`.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    assert isinstance(_X, list)
    assert all(map(isinstance, _X, (list for _ in _X)))
    assert isinstance(_sep, list)
    assert all(map(isinstance, _sep, (str for _ in _sep)))

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    for r_idx in range(len(_X)):
        _X[r_idx] = _sep[r_idx].join(_X[r_idx])


    return _X







