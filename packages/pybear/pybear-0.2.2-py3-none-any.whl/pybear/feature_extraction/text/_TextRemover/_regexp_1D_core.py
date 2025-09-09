# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from ._type_aliases import (
    WipRemoveType,
    RowSupportType
)

import numpy as np

import re



def _regexp_1D_core(
    _X: list[str],
    _rr: WipRemoveType,
    _from_2D: bool
) -> tuple[list[str], RowSupportType]:
    """Remove unwanted strings from a 1D list of strings using regular
    expressions.

    `remove` passed as literal strings and `case_sensitive` were
    converted to re.compile in :func:`_param_conditioner`.

    Parameters
    ----------
     _X : list[str]
        A Python list of tokenized strings.
    _rr : WipRemoveType
        The pattern(s) by which to identify strings to be removed.
    _from_2D : bool
        Whether this is a row from 2D data. If False, the data was
        passed as 1D and `_X` is the `X` passed to transform. If `_X` is
        a row from 2D data, then `_rr` as list is disallowed.

    Returns
    -------
    tuple[list[str], RowSupportType]:
        the data with unwanted strings removed and a boolean vector
        indicating which indices of the data were kept. If the `X`
        passed to transform was 1D, this is ultimately the `row_support_`
        attribute that is visible through the API. If `X` was 2D, this
        should be discarded.

    Notes
    -----

    **Type Aliases**

    WipRemoveType:
        WipPatternType | list[WipPatternType]

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    assert isinstance(_X, list)
    assert all(map(isinstance, _X, (str for _ in _X)))

    # _rr is validated immediately after it is made

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    _row_support: npt.NDArray[bool] = np.ones(len(_X), dtype=bool)


    # condition re.Pattern so that all Patterns are in a tuple
    if isinstance(_rr, re.Pattern):
        _rr = (_rr, )


    if _rr is None:
        return _X, _row_support

    elif isinstance(_rr, tuple):
        for _idx in range(len(_X)-1, -1, -1):
            for _pattern in _rr:
                if re.fullmatch(_pattern, _X[_idx]):
                    _X.pop(_idx)
                    _row_support[_idx] = False
                    break

    elif isinstance(_rr, list):

        if _from_2D:
            raise TypeError(f"a list rr is being used on a row from a 2D X")

        for _idx in range(len(_X)-1, -1, -1):

            # use recursion
            # send the one string back into this module in a list
            # if that list comes back empty, we know to delete

            if isinstance(_rr[_idx], list):
                raise TypeError

            _out = _regexp_1D_core([_X[_idx]], _rr[_idx], _from_2D=False)[0]

            if len(_out) == 0:
                _X.pop(_idx)
                _row_support[_idx] = False

    else:
        raise Exception


    return _X, _row_support







