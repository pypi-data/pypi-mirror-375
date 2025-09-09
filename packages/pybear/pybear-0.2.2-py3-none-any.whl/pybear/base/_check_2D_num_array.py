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
    Polars2DTypes,
    ScipySparseTypes
)

import numbers

import pandas as pd
import polars as pl
import scipy.sparse as ss

from ._check_1D_num_sequence import check_1D_num_sequence



XContainer: TypeAlias = \
    Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes | ScipySparseTypes



def check_2D_num_array(
    X:XContainer[numbers.Number],
    require_all_finite:bool = False
) -> None:
    """Validate things that are expected to be 2D arrays of numbers.

    Accepts 2D Python built-ins, numpy arrays, pandas dataframes, polars
    dataframes, and all scipy sparse matrices/arrays. Python built-ins
    can be ragged. When `require_all_finite` is True, every element in
    the array must be an instance of numbers.Number; a ValueError will
    be raised if there are any nan-like or infinity-like values. If
    `require_all_finite` is False, non-finite values are ignored and
    only the finite values must be an instance of numbers.Number. If all
    checks pass then None is returned.

    Parameters
    ----------
    X : XContainer[numbers.Number]
        Something that is expected to be a 2D array of numbers.
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

    ScipySparseTypes:
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
        | ss.bsr_matrix | ss.bsr_array

    XContainer:
        Python2DTypes | Numpy2DTypes | Pandas2DTypes | Polars2DTypes
        | ScipySparseTypes

    Examples
    --------
    >>> from pybear.base import check_2D_num_array
    >>> import numpy as np
    >>> X = np.random.randint(0, 10, (37, 13)).astype(np.float64)
    >>> X[0][8] = np.nan
    >>> X[31][3] = np.inf
    >>> check_2D_num_array(X, require_all_finite=False)
    >>> try:
    ...     check_2D_num_array(X, require_all_finite=True)
    ... except ValueError as e:
    ...     print(e)
    Got non-finite values when not allowed.

    """


    _err_msg = f"Expected a 2D array of number-like values. "
    _addon = (
        f"\nAccepted containers are 2D python lists, tuples, and sets, "
        f"\nnumpy 2D arrays, pandas dataframes, polars dataframes, and all "
        f"\nscipy sparse matrices/arrays."
    )


    # block disallowed containers -- -- -- -- -- -- -- -- -- -- -- -- --
    if isinstance(X, (pd.Series, pl.Series)):
        raise TypeError(_err_msg + _addon)

    try:
        # dok gets a free pass
        if isinstance(X, (ss.dok_matrix, ss.dok_array)):
            raise UnicodeError
        # must be iterable
        iter(X)
        # cant be string or dict
        if isinstance(X, (str, dict)):
            raise Exception
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

        _callable = check_1D_num_sequence
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

            _base = f"Expected a 1D sequence of number-like values."
            _bad_container = f"Accepted containers are Python lists,"

            # this should be in both
            assert _base in str(t)

            if _bad_container not in str(t):
                # then raised for bad dtype
                raise TypeError(_err_msg)
            elif _bad_container in str(t):
                # this is for bad container
                # not expecting this to ever raise!
                raise Exception(f"unexpected container error from {_fxn_name}")
            else:
                raise Exception(f"unexpected exception string from {_fxn_name}")

        except Exception as e:
            raise Exception(
                f"{_fxn_name} raised for reason other than TypeError or "
                f"ValueError."
            )
    # END helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    if hasattr(X, 'toarray'):   # ss
        _exception_helper(
            X.tocsr().data.reshape((1, -1)),  # as 2D is important
            (require_all_finite, )
        )
    elif isinstance(X, pd.DataFrame):   # pandas
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





