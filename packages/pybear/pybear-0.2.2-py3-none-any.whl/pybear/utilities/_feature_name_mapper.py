# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)
import numpy.typing as npt

from copy import deepcopy
import numbers
import numpy as np
import pandas as pd

from ._nan_masking import nan_mask_numerical



def feature_name_mapper(
    feature_names: Sequence[str] | Sequence[int] | None,
    feature_names_in: Sequence[str] | None,
    positive: bool | None = True
) -> npt.NDArray[np.int32]:
    """Map a vector of feature names `feature_names` against the full set
    of feature names provided by `feature_names_in`.

    Return the index positions of the given feature names with respect
    to their position in `feature_names_in`. Can be returned as positive
    indices, e.g. [0,3,4], or negative indices, e.g. [-4,-2,-1], or as
    given.

    Parameters
    ----------
    feature_names : Sequence[str] | Sequence[int] | None
        The feature names to be mapped to index positions. If None,
        returns None. If an empty 1D sequence, returns the same. If
        passed as integers without a `feature_names_in` reference,
        returns the original. if passed as integers with a
        `feature_names_in` reference, the index values are validated
        against the dimensions of the `feature_names_in` vector and
        mapped to all positive or all negative values based on `positive`.
        If passed as strings without a `feature_names_in` reference,
        raises exception. If passed as strings with a `feature_names_in`
        reference, the string values are mapped to the index positions
        in the `feature_names_in` vector and mapped to all positive or
        all negative values based on `positive`. If passed as string
        values and a value is not in `feature_names_in`, raises exception.
    feature_names_in : Sequence[str] | None
        If not None, a 1D list-like containing strings that are the
        feature names of a data-bearing container.
    positive : bool | None
        Whether to return the mapped indices as all positive or all
        negative integers. if None, leave the indices as is.

    Returns
    -------
    indices : numpy.ndarray[np.int32]
        The given feature names mapped to index positions.

    Examples
    --------
    >>> from pybear.utilities import feature_name_mapper
    >>> import numpy as np
    >>> data = np.random.randint(0, 10, (5, 3))
    >>> columns = np.array(['A', 'B', 'C'])
    >>> feature_names = np.array(['A', 'C'])
    >>> out = feature_name_mapper(
    ...     feature_names, columns, positive=False
    ... )
    >>> print(out)
    [-3 -1]

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # feature_names_in -- -- -- -- -- -- -- -- -- -- -- -- --
    try:
        if feature_names_in is None:
            raise UnicodeError
        iter(feature_names_in)
        if isinstance(feature_names_in, (str, dict, pd.DataFrame)):
            raise Exception
        if len(np.array(list(feature_names_in)).shape) != 1:
            raise Exception
        if len(feature_names_in) == 0:
            raise Exception
        if not all(map(
            isinstance,
            feature_names_in,
            (str for i in feature_names_in)
        )):
            raise Exception
    except UnicodeError:
        pass
    except:
        raise TypeError(
            f"if not None, 'feature_names_in' must be a 1D list-like "
            f"containing strings that are the feature names of a "
            f"data-bearing container. \n'feature_names_in' cannot be "
            f"empty."
        )
    # END feature_names_in -- -- -- -- -- -- -- -- -- -- -- --

    # positive -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(positive, (bool, type(None))):
        raise TypeError(f"'positive' must be boolean or None")
    # END positive -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # we know that
    # --'feature_names_in' is None or a 1D ndarray of strings, len >= 1
    # --'positive' is bool


    if feature_names is None:
        return

    # feature_names -- -- -- -- -- -- -- -- -- -- -- -- -- --
    try:
        iter(feature_names)
        if isinstance(feature_names, (str, dict, pd.DataFrame)):
            raise Exception
        if len(np.array(list(feature_names), dtype=object).shape) != 1:
            raise Exception
        if not all(map(
            isinstance,
            feature_names,
            ((numbers.Integral, str) for i in feature_names)
        )):
            raise Exception
    except:
        raise TypeError(
            f"if not None, 'feature_names' must be a 1D list-like of "
            f"strings or integers"
        )
    # END feature_names -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if len(feature_names) == 0:
        return np.array([], dtype=np.int32)

    # we now also know that 'feature_names'
    # --is a 1D array of integers or strings
    # --cannot be empty
    # --cannot be None
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # if list-like, validate contents are all str or all int ** * ** *

    err_msg = (f"'feature_names' must contain all integers indicating "
        f"column indices or all strings indicating column names")

    # do not use .astype(np.float64) to check if is num/str!
    # ['0787', '5927', '4060', '2473'] will pass and be treated as
    # column indices when they are actually column headers.
    is_str = False
    if all(map(isinstance, feature_names, (str for _ in feature_names))):
        is_str = True
    elif all(map(
        isinstance, feature_names, (numbers.Real for _ in feature_names)
    )):
        # ensure all are integers
        if any(map(isinstance, feature_names, (bool for _ in feature_names))):
            raise TypeError(err_msg)
        if np.any(nan_mask_numerical(
                np.array(list(feature_names), dtype=np.float64)
        )):
            raise TypeError(err_msg)
        if not all(map(lambda x: int(x)==x, feature_names)):
            raise TypeError(err_msg)
    else:
        raise TypeError(err_msg)
    # END if list-like validate contents are all str or all int ** * **

    # we know that
    # --'feature_names_in' is None or a 1D ndarray of strings, len >= 1
    # --'positive' is bool
    # -- 'feature_names' is a 1D array of all integers or all strings

    if is_str:

        # _feature_names_in is not necessarily available, could be None
        if feature_names_in is None:
            raise ValueError(
                f"when 'feature_names' is passed with strings, "
                f"'feature_names_in' must be a 1D list-like containing "
                f"strings that are the feature names of a data-bearing "
                f"container. \n'feature_names_in' cannot be None."
            )

        _n_features_in = len(feature_names_in)

        indices = []
        for idx, _column in enumerate(feature_names):

            if _column not in feature_names_in:
                raise ValueError(
                    f"'feature_names' column '{_column}' is not in "
                    f"'feature_names_in'"
                )

            # CONVERT COLUMN NAMES TO COLUMN INDEX
            MASK = (np.array(feature_names_in) == _column)
            indices.append(int(np.arange(_n_features_in)[MASK][0]))

        del is_str, _n_features_in, idx, _column, MASK


    # at this point we know that feature_names is a vector of all integers

    try:
        indices
    except:
        indices = deepcopy(feature_names)

    # we have to account for feature_names could have been passed as
    # integers and feature_names_in could still be None
    if feature_names_in is None:
        # without knowing feature_names_in, all we have is an 'indices'
        # vector with integers that may be all positive, all negative,
        # or a mix of both, and we cant validate the values. so just
        # return it.
        return np.array(list(indices), dtype=np.int32)
    elif feature_names_in is not None:
        # must be 1D ndarray of strings, len >= 1
        _n_features_in = len(feature_names_in)
        if min(indices) < -_n_features_in:
            raise ValueError(
                f"column index {min(indices)} is out of bounds for a "
                f"feature name vector with {_n_features_in} features"
            )
        if max(indices) >= _n_features_in:
            raise ValueError(
                f"column index {max(indices)} is out of bounds for a "
                f"feature name vector with {_n_features_in} features"
            )

        if positive is None:
            pass
        elif positive is True:
            # make sure all are positive
            indices = [
                x + (_n_features_in if x < 0 else 0) for x in indices
            ]
        elif positive is False:
            # make sure all are negative
            indices = [
                x - (_n_features_in if x > -1 else 0) for x in indices
            ]

        return np.array(list(indices), dtype=np.int32)


    # if we get here, algorithm failure
    raise Exception






