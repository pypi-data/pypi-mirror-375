# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers
import itertools

from .._type_aliases import XWipContainer



def _transform(
    _X: XWipContainer,
    _fill: str,
    _n_features: int
) -> list[list[str]]:
    """Pad ragged `X` vector with fill value to make a full array.

    Returns a Python list of Python lists of strings.

    Parameters
    ----------
    _X : XWipContainer
        The data to be padded to a structured array.
    _fill : str
        The string value to fill void space with.
    _n_features : int
        The number of features to create for the padded data.

    Returns
    -------
    _X : XWipContainer
        `X` padded with fill value to a full array.

    Notes
    -----
    XWipContainer:
        list[list[str]]

    """


    assert isinstance(_fill, str)
    assert isinstance(_n_features, numbers.Integral)


    # _n_features cannot be less than features in _X, would have been
    # incremented to match, unless trfm data was not seen during fit
    if max(map(len, _X)) > _n_features:
        raise ValueError(
            f"the data presently passed to transform has at least one "
            f"example with more strings than any seen during fitting, "
            f"and also has more strings than the current setting for "
            f"'n_features'."
        )


    # _fill must be a string per validation, even though fillvalue need
    # not be a string
    _X = list(map(list, zip(*itertools.zip_longest(*_X, fillvalue=_fill))))


    _shortfall = _n_features - len(_X[0])
    if _shortfall:

        _addon = [_fill for _ in range(_shortfall)]

        for _idx in range(len(_X)):
            _X[_idx] += _addon

        del _addon

    del _shortfall


    return _X







