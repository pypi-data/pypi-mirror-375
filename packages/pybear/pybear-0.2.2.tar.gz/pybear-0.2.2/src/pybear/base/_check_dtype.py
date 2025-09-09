# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    TypeAlias
)
from .__type_aliases import (
    PythonTypes,
    NumpyTypes,
    PandasTypes,
    PolarsTypes,
    ScipySparseTypes
)

import numpy as np

from ._check_1D_num_sequence import check_1D_num_sequence
from ._check_2D_num_array import check_2D_num_array
from ._check_1D_str_sequence import check_1D_str_sequence
from ._check_2D_str_array import check_2D_str_array

from ..utilities._nan_masking import nan_mask
from ..utilities._inf_masking import inf_mask

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def check_dtype(
    X:XContainer,
    allowed:Literal['numeric', 'str', 'any'] = 'any',
    require_all_finite:bool = False
) -> None:
    """Check that the passed data is of an allowed datatype.

    If not, raise TypeError. Allowed dtypes are 'any', 'numeric', and
    'str'. If all checks pass then return None.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The data to be checked for allowed datatype.
    allowed : Literal['numeric', 'str', 'any'], default='any'
        The allowed datatype for the data. If 'numeric', only allow
        values that are instances of numbers.Number. If not, raise
        TypeError. If 'str', all data in `X` must be and instance of str
        or a TypeError is raised. If 'any', allow any datatype.
    require_all_finite : bool, default=False
        If True, raise an exception if there are any nan-like or
        infinity-like values in the data. This means that all elements
        in the data must be of the required dtype. If False, nan-likes
        and infinity-likes are allowed, and all other values (the finite
        values) must be of the required dtype.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    ScipySparseTypes:
        ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
        | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
        | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
        | ss.bsr_matrix | ss.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes |
        ScipySparseTypes

    Examples
    --------
    >>> from pybear.base import check_dtype
    >>> X = [1, 3, 5, np.nan]
    >>> check_dtype(X, allowed='numeric', require_all_finite=False)
    >>> try:
    ...     check_dtype(X, allowed='str', require_all_finite=False)
    ... except TypeError as e:
    ...     print(repr(e))
    TypeError('Expected a 1D sequence of string-like values. ')
    >>> try:
    ...     check_dtype(X, allowed='numeric', require_all_finite=True)
    ... except ValueError as e:
    ...     print(repr(e))
    ValueError('Got non-finite values when not allowed.')

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    err_msg = f"'allowed' must be literal 'numeric', 'str', or 'any'."

    if not isinstance(allowed, str):
        raise TypeError(err_msg)

    allowed = allowed.lower()

    if allowed not in ['numeric', 'str', 'any']:
        raise ValueError(err_msg)

    del err_msg

    if not isinstance(require_all_finite, bool):
        raise TypeError(f"'require_all_finite' must be bool")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if allowed == 'any':

        if not require_all_finite:
            return
        elif require_all_finite:
            if np.any(nan_mask(X)) or np.any(inf_mask(X)):
                raise ValueError(f"Got non-finite values when not allowed.")

    elif allowed == 'numeric':

        # ValueError for non-finite when disallowed
        # TypeError for bad container and bad dtype -- these 2 raises
        # need to be separated
        try:
            check_2D_num_array(
                X,
                require_all_finite=require_all_finite
            )
        except ValueError as v:
            raise(v) from None
        except TypeError as t:

            _base = f"Expected a 2D array of number-like values."
            _bad_container = f"Accepted containers are 2D python lists,"

            # this should be in both
            assert _base in str(t)

            if _bad_container not in str(t):
                # then raised for bad dtype
                raise t from None
            elif _bad_container in str(t):
                pass  # go to 1D
            else:
                raise Exception(
                    f"unexpected exception string from check_2D_num_array()"
                )

            try:
                check_1D_num_sequence(
                    X,
                    require_all_finite=require_all_finite
                )
            except ValueError as v:
                raise v from None
            except TypeError as t:
                _base = f"Expected a 1D sequence of number-like values."
                _bad_container = f"Accepted containers are python lists,"

                # this should be in both
                assert _base in str(t)

                if _bad_container not in str(t):
                    # then raised for bad dtype
                    raise t from None
                elif _bad_container in str(t):
                    # not expecting this to ever be raised
                    # this would mean that a 2D is a valid container but
                    # one of its 1D constituents is not
                    raise Exception(
                        f"unexpected container exception from check_1D_num_sequence()"
                    )
                else:
                    raise Exception(
                        f"unexpected exception string from check_2D_num_array()"
                    )
            except Exception as e:
                raise Exception(f'got error other than Type or Value --- {e}')
        except Exception as e:
            raise Exception(f'got error other than Type or Value --- {e}')

    elif allowed == 'str':

        # ValueError for non-finite when disallowed
        # TypeError for bad container and bad dtype -- these 2 raises
        # need to be separated
        try:
            check_2D_str_array(
                X,
                require_all_finite=require_all_finite
            )
        except ValueError as v:
            raise(v) from None
        except TypeError as t:

            _base = f"Expected a 2D array of string-like values."
            _bad_container = f"Accepted containers are 2D python lists,"

            # this should be in both
            assert _base in str(t)

            if _bad_container not in str(t):
                # then raised for bad dtype
                raise t from None
            elif _bad_container in str(t):
                pass  # go to 1D
            else:
                raise Exception(
                    f"unexpected exception string from check_2D_str_array()"
                )

            try:
                check_1D_str_sequence(
                    X,
                    require_all_finite=require_all_finite
                )
            except ValueError as v:
                raise v from None
            except TypeError as t:
                _base = f"Expected a 1D sequence of string-like values."
                _bad_container = f"Accepted containers are python lists,"

                # this should be in both
                assert _base in str(t)

                if _bad_container not in str(t):
                    # then raised for bad dtype
                    raise t from None
                elif _bad_container in str(t):
                    # not expecting this to ever be raised
                    # this would mean that a 2D is a valid container but
                    # one of its 1D constituents is not
                    raise Exception(
                        f"unexpected container exception from check_1D_str_sequence()"
                    )
                else:
                    raise Exception(
                        f"unexpected exception string from check_2D_str_array()"
                    )
            except Exception as e:
                raise Exception(f'got error other than Type or Value --- {e}')
        except Exception as e:
            raise Exception(f'got error other than Type or Value --- {e}')
    else:
        raise Exception






