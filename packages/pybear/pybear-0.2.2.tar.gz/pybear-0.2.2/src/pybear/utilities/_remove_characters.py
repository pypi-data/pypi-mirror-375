# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt

import operator
import functools

import numpy as np

from ..base._check_1D_str_sequence import check_1D_str_sequence
from ..base._check_2D_str_array import check_2D_str_array



def remove_characters(
    X: list[str] | list[list[str]] | npt.NDArray[str],
    *,
    allowed_chars:str | None = None,
    disallowed_chars:str | None = None
) -> list[str] | list[list[str]] | npt.NDArray[str]:
    """Remove characters that are not allowed or are explicitly disallowed
    from 1D or 2D text data.

    `allowed_chars` and `disallowed_chars` cannot simultaneously be
    strings and cannot simultaneously be None.

    Parameter
    ---------
    X : list[str] | list[list[str]] | npt.NDArray[str]]
        The data from which to remove unwanted characters.
    allowed_chars : str | None, default=None
        The characters that are to be kept; cannot be passed if
        disallowed_chars is passed.
    disallowed_chars : str | None, default=None
        The characters that are to be removed; cannot be passed if
        allowed_chars is passed.

    Returns
    -------
    X : list[str] | list[list[str]] | npt.NDArray[str]]
        The data with unwanted characters removed.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if allowed_chars is None and disallowed_chars is None:
        raise ValueError(
            f"Must specify at least one of 'allowed_chars' or 'disallowed_chars'"
        )
    elif allowed_chars is not None and disallowed_chars is not None:
        raise ValueError(
            f"Cannot enter both 'allowed_chars' and 'disallowed_chars'. "
            f"Only one or the other.'"
        )
    elif allowed_chars is not None:
        if not isinstance(allowed_chars, str):
            raise TypeError(f"'allowed_chars' must be str")
        if len(allowed_chars) == 0:
            raise ValueError(f"'allowed_chars' cannot be an empty string")
    elif disallowed_chars is not None:
        if not isinstance(disallowed_chars, str):
            raise TypeError(f"'disallowed_chars' must be str")
        if len(disallowed_chars) == 0:
            raise ValueError(f"'disallowed_chars' cannot be an empty string")


    _is_2D = False
    try:
        check_1D_str_sequence(X)
    except:
        try:
            check_2D_str_array(X)
            _is_2D = True
        except:
            raise TypeError(
                f"X must be a 1D vector of strings or a 2D array of "
                f"strings, got {type(X)}."
            )
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    allowed_chars = allowed_chars or ''
    disallowed_chars = disallowed_chars or ''


    def _remover_decorator(foo):
        """A wrapping function that serves to find the unique characters
        to remove and then remove them from the data using the wrapped
        function.
        """


        @functools.wraps(foo)
        def _remover(_X):

            nonlocal allowed_chars, disallowed_chars

            UNIQUES = ''
            for i in _X:
                UNIQUES = str("".join(np.unique(list(UNIQUES + i))))

            for char in UNIQUES:
                if (len(allowed_chars) and char not in allowed_chars) \
                        or char in disallowed_chars:
                    _X = foo(_X, char)

            del UNIQUES

            return _X

        return _remover


    @_remover_decorator
    def _list_remover(_X, _char):  # _X must be 1D
        return list(map(operator.methodcaller("replace", _char, ''), _X))


    @_remover_decorator
    def _ndarray_remover(_X, _char):
        return np.char.replace(_X.astype(str), _char, '')



    if not _is_2D:  # MUST BE LIST OF strs

        if isinstance(X, list):
            X = [_ for _ in _list_remover(X) if _ != '']

        elif isinstance(X, np.ndarray):
            X = _ndarray_remover(X)
            X = X[(X != '')]

    elif _is_2D:

        if isinstance(X, list):

            for row_idx, list_of_strings in enumerate(X):
                X[row_idx] = \
                    [_ for _ in _list_remover(list_of_strings) if _ != '']

        elif isinstance(X, np.ndarray):

            for row_idx, vector_of_strings in enumerate(X):
                X[row_idx] = _ndarray_remover(vector_of_strings)
                # if this is a full array it will throw a fit for cannot
                # cast shorter vector into the full array
                try:
                    X[row_idx] = X[row_idx][(X[row_idx] != '')]
                except:
                    pass


    return X




