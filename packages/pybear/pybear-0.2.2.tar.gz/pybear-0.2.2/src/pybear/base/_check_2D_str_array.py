# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterable,
    Sequence,
    TypeAlias
)
from .__type_aliases import (
    Python2DTypes,
    Numpy2DTypes,
    Pandas2DTypes,
    Polars2DTypes
)

import pandas as pd
import polars as pl

from ._check_1D_str_sequence import check_1D_str_sequence



XContainer: TypeAlias = \
    Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes



def check_2D_str_array(
    X:XContainer[str],
    require_all_finite:bool = False
) -> None:
    """Validate things that are expected to be 2D arrays of strings.

    Accepts 2D Python built-ins, numpy arrays, pandas dataframes,
    and polars dataframes. Python built-ins can be ragged. When
    `require_all_finite` is True, every element in the array must be
    an instance of str; a ValueError will be raised if there are any
    nan-like or infinity-like values. If `require_all_finite` is False,
    non-finite values are ignored and only the finite values must be
    an instance of str. If all checks pass then None is returned.

    Parameters
    ----------
    X : XContainer[str]
        Something that is expected to be a 2D array of strings.
    require_all_finite : bool, default=False
        If True, disallow all non-finite values, such as nan-like or
        infinity-like values.

    Raises
    ------
    TypeError:
        For invalid container.
    ValueError:
        For non-finite values when `require_all_finite` is True.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    Python2DTypes:
        list[list] | tuple[tuple]

    Numpy2DTypes:
        numpy.ndarray

    Pandas2DTypes:
        pandas.DataFrame

    Polars2DTypes:
        polars.DataFrame

    XContainer:
        Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes

    Examples
    --------
    >>> from pybear.base import check_2D_str_array
    >>> import numpy as np
    >>> X = np.random.choice(list('abcde'), (37, 13)).astype('<U4')
    >>> X[0][8] = 'nan'
    >>> X[31][3] = '-inf'
    >>> check_2D_str_array(X, require_all_finite=False)
    >>> try:
    ...     check_2D_str_array(X, require_all_finite=True)
    ... except ValueError as e:
    ...     print(e)
    Got non-finite values when not allowed.

    """


    _err_msg = f"Expected a 2D array of string-like values. "
    _addon = (
        f"\nAccepted containers are 2D python lists, tuples, and sets, "
        f"\nnumpy 2D arrays, pandas dataframes, and polars dataframes."
    )


    # block disallowed containers -- -- -- -- -- -- -- -- -- -- -- -- --
    if isinstance(X, (pd.Series, pl.Series)):
        raise TypeError(_err_msg + _addon)

    if hasattr(X, 'toarray'):   # scipy
        raise TypeError(_err_msg + _addon)

    try:
        # must be iterable
        iter(X)
        # cant be string or dict
        if isinstance(X, (str, dict)):
            raise Exception
        # handle anything with shape attr directly
        if hasattr(X, 'shape') and len(getattr(X, 'shape')) == 2:
            # if X is already 'nice', then skip out, but there's a chance
            # X may be a ragged ndarray dtype == object, keep testing
            raise UnicodeError
        if any(map(isinstance, X, ((str, dict) for _ in X))):
            raise Exception
        if not all(map(isinstance, X, (Iterable for _ in X))):
            raise Exception
    except UnicodeError:
        pass
    except Exception as e:
        raise TypeError(_err_msg + _addon)
    # END block disallowed containers -- -- -- -- -- -- -- -- -- -- --

    # define function to manage error handling -- -- -- -- -- -- -- --
    def _exception_helper(
        _X_object,
        _require_all_finite: Sequence[bool],
    ) -> None:

        """
        The errors raised below come from 1D files. Override with
        new error message for 2D. This verbiage needs to be managed to
        handle errors correctly in check_dtype().
        """


        nonlocal _err_msg

        _callable = check_1D_str_sequence
        _fxn_name = _callable.__name__

        try:
            list(map(
                _callable,
                _X_object,
                (require_all_finite for _ in _X_object)
            ))
            # this could raise for
            # ValueError - non-finite when not allowed
            # TypeError - bad container or bad dtype
        except ValueError as v:
            raise v from None
        except TypeError as t:

            _base = f"Expected a 1D sequence of string-like values."
            _bad_container = f"Accepted containers are python lists,"

            # this should be in both
            assert _base in str(t)

            if _bad_container not in str(t):
                # then raised for bad dtype
                raise TypeError(_err_msg)
            elif _bad_container in str(t):
                # this is for bad container
                # not expecting this to ever raise!
                raise Exception(
                    f"unexpected container error from {_fxn_name}"
                )
            else:
                raise Exception(
                    f"unexpected exception string from {_fxn_name}"
                )

        except Exception as e:
            raise Exception(
                f"{_fxn_name} raised for reason other than TypeError or "
                f"ValueError."
            )
    # END helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if isinstance(X, pd.DataFrame):   # pandas
        # to keep sporadic problems out of test, do this in the same way
        # as np and python-native, which is as rows.
        _exception_helper(
            X.values,
            (require_all_finite for _ in range(X.shape[0]))
        )
    elif isinstance(X, pl.DataFrame):   # polars
        # to keep sporadic problems out of test, do this in the same way
        # as np and python-native, which is as rows.
        _exception_helper(
            X.rows(),
            (require_all_finite for _ in range(X.shape[0]))
        )
    else:
        _exception_helper(
            X,
            (require_all_finite for _ in X)
        )





