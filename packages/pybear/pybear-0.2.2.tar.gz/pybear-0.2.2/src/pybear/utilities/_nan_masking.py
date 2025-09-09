# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
import numpy.typing as npt
from .__type_aliases import (
    PythonTypes,
    NumpyTypes,
    PandasTypes,
    PolarsTypes
)

from copy import deepcopy
import numbers

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl



# dok and lil are left out intentionally
ScipySparseTypes: TypeAlias = (
    ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
    | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
    | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
    | ss._bsr.bsr_array
)

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def nan_mask_numerical(
    X: XContainer
) -> npt.NDArray[bool]:
    """Return a boolean numpy array or vector indicating the locations
    of nan-like representations in the data.

    "nan-like representations" include, at least, numpy.nan, pandas.NA,
    None, and string representations of "nan". In the cases of Python
    native, numpy, pandas, and polars objects of shape (n_samples,
    n_features) or (n_samples, ), return an identically shaped numpy
    array. In the cases of scipy sparse objects, return a vector with
    shape equal to that of the 'data' attribute of the sparse object.

    This function accepts Python lists, tuples, and sets, numpy arrays,
    pandas dataframes and series, polars dataframes and series, and all
    scipy sparse matrices/arrays except dok and lil formats. It does not
    accept any ragged Python built-ins, numpy recarrays, or numpy masked
    arrays. Data must be able to cast to numpy numerical dtypes.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples, )
        The object for which to locate nan-like representations.

    Returns
    -------
    mask : numpy.ndarray[bool]
        shape (n_samples, n_features) or (n_samples, ) or (n_non_zero_values, )

        Indicates nan-like representations in `X` via the value boolean
        True. Values that are not nan-like are False.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.DataFrame | pandas.Series

    PolarsTypes:
        polars.DataFrame | polars.Series

    ScipySparseTypes:
        ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
        | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
        | ss._bsr.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    Examples
    --------
    >>> from pybear.utilities import nan_mask_numerical
    >>> import numpy as np
    >>> X = np.arange(6).astype(np.float64)
    >>> X[1] = np.nan
    >>> X[-2] = np.nan
    >>> X
    array([ 0., nan,  2.,  3., nan,  5.])
    >>> nan_mask_numerical(X)
    array([False,  True, False, False,  True, False])

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    _err_msg = (
        f"'X' must be an array-like with a copy() or clone() method, "
        f"such as python built-ins, \nnumpy arrays, scipy sparse matrices "
        f"or arrays, pandas dataframes/series, polars dataframes/series. "
        f"\nif passing a scipy sparse object, it cannot be dok or lil. "
        f"\nnumpy recarrays and masked arrays are not allowed."
    )

    try:
        iter(X)
        if isinstance(X, (str, dict)):
            raise Exception
        if isinstance(X, tuple):
            # tuple doesnt have copy() method, but is OK
            # notice the elif
            pass
        elif not hasattr(X, 'copy') and not hasattr(X, 'clone'):
            # copy for builtins, numpy, pandas, and scipy; clone for polars
            raise Exception
        if isinstance(X, (np.recarray, np.ma.MaskedArray)):
            raise Exception
        if hasattr(X, 'toarray'):
            if not hasattr(X, 'data'): # ss dok
                raise Exception
            elif all(map(isinstance, X.data, (list for _ in X.data))): # ss lil
                raise Exception
    except:
        raise TypeError(_err_msg)

    del _err_msg

    if isinstance(X, (list, tuple, set)):
        _err_msg = (
            f"nan_mask_numerical expected all number-like values. "
            f"\ngot at least one non-nan string."
        )

        # cant have strings except str(nan)

        # find out if it is 1D
        _is_1D = False
        try:
            assert np.array(list(X)).shape == np.array(list(X)).ravel().shape
            _is_1D = True
        except:
            pass

        if _is_1D:
            try:
                pd.Series(list(X)).astype(np.float64)
                # we have a 1D that has no strings, at least.
                # could have junky nans or None, or whatever else
            except:
                raise TypeError(_err_msg)
        elif not _is_1D:
            # prove not ragged
            if len(set(map(len, X))) != 1:
                raise ValueError(
                    f"nan_mask_numerical does not accept ragged arrays"
                )
            # we have a non-ragged 2D of somethings
            try:
                pd.DataFrame(list(map(list, X))).astype(np.float64)
            except:
                raise TypeError(_err_msg)
            # we have a non-ragged 2D of things that can cast to float
        del _err_msg, _is_1D
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    if hasattr(X, 'toarray'):
        M = X.data.copy()
    elif hasattr(X, 'clone'):
        # Polars uses zero-copy conversion when possible, meaning the
        # underlying memory is still controlled by Polars and marked
        # as read-only. NumPy and Pandas may inherit this read-only
        # flag, preventing modifications.
        # THE ORDER IS IMPORTANT HERE. CONVERT TO PANDAS FIRST, THEN COPY.
        M = X.to_pandas().copy()  # polars
    elif isinstance(X, (list, tuple, set)):
        try:
            if all(map(lambda x: str(x).lower == 'nan', X)):
                raise Exception
            if any(map(isinstance, X, ((numbers.Number, str) for i in X))):
                raise Exception
            M = list(map(list, deepcopy(X)))
        except Exception as e:
            M = list(deepcopy(X))

        M = np.array(M).astype(np.float64)
    else:
        M = X.copy()  # numpy and pandas


    try:
        M = M.to_numpy()
    except:
        pass

    M[(M == 'nan')] = np.nan

    return pd.isna(M.astype(np.float64))


def nan_mask_string(
    X: PythonTypes | NumpyTypes | PandasTypes | PolarsTypes
) -> npt.NDArray[bool]:
    """In all cases, return an identically shaped boolean numpy array or
    vector indicating the locations of nan-like representations in the
    data.

    "nan-like representations" include, at least, pandas.NA, pandas.NaT,
    None (of type None, not string "None"), and string representations
    of "nan". This function does not accept scipy sparse matrices or
    arrays, as dok and lil formats are not handled globally in the
    nan_mask functions, and the remaining sparse objects can only contain
    numeric data.

    This function accepts Python lists, tuples, and sets, numpy arrays,
    pandas dataframes and series, and polars dataframes and series. It
    does not accept any ragged Python built-ins, numpy recarrays, or
    numpy masked arrays.

    Parameters
    ----------
    X : PythonTypes | NumpyTypes | PandasTypes | PolarsTypes
        shape (n_samples, n_features) or (n_samples,)

        The object for which to locate nan-like representations.

    Returns
    -------
    mask : numpy.ndarray[bool] of shape (n_samples, n_features) or (n_samples)
        Indicates nan-like representations in `X` via the value boolean
        True. Values that are not nan-like are False.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.DataFrame | pandas.Series

    PolarsTypes:
        polars.DataFrame | polars.Series

    Examples
    --------
    >>> from pybear.utilities import nan_mask_string
    >>> X = list('abcde')
    >>> X[0] = 'nan'
    >>> X[2] = 'nan'
    >>> X
    ['nan', 'b', 'nan', 'd', 'e']
    >>> nan_mask_string(X)
    array([ True, False,  True, False, False])

    """

    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    _err_msg = (
        f"'X' must be an array-like with a copy() or clone() method, "
        f"\nsuch as python built-ins, pandas dataframes/series, numpy "
        f"arrays, or polars dataframes/series. \n'X' cannot be a scipy "
        f"sparse matrix or array. \nnumpy recarrays and masked arrays "
        f"are not allowed."
    )

    try:
        iter(X)
        if isinstance(X, (str, dict)):
            raise Exception
        if isinstance(X, tuple):
            pass
            # tuple doesnt have copy() method
            # notice the elif
        elif not hasattr(X, 'copy') and not hasattr(X, 'clone'):
            # copy for numpy, pandas, and scipy; clone for polars
            raise Exception
        if isinstance(X, (np.recarray, np.ma.MaskedArray)):
            raise Exception
        if hasattr(X, 'toarray'):
            raise Exception
    except:
        raise TypeError(_err_msg)

    del _err_msg

    if isinstance(X, (list, set, tuple)):

        try:
            if all(map(isinstance, X, (str for i in X))):
                raise Exception
            # this will except if X is not 2D, because cant be all strings
            list(map(iter, X))
            # prove not ragged
            if len(set(map(len, X))) != 1:
                raise UnicodeError
            # we have a non-ragged 2D of somethings
        except UnicodeError:
            raise ValueError(
                f"nan_mask_string does not accept ragged arrays"
            )
        except Exception as e:
            # we have a 1D list-like of strings
            pass

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # create a numpy array with same dims as X -- -- -- -- -- -- -- --
    if hasattr(X, 'clone'):
        # Polars uses zero-copy conversion when possible, meaning the
        # underlying memory is still controlled by Polars and marked
        # as read-only. NumPy and Pandas may inherit this read-only
        # flag, preventing modifications.
        # Tests did not expose this as a problem like it did for numerical().
        # just to be safe though, do this the same way as numerical().
        M = X.to_pandas().copy()  # polars
    elif isinstance(X, (list, tuple, set)):
        # we cant just map list here, if 1D it is full of strings
        # if one is str, assume all entries are not list-like
        # what about non-str nans
        if any(map(isinstance, X, (str for i in X))):
            M = list(deepcopy(X))
        elif any(map(lambda x: str(x).lower() == 'nan', X)):
            M = list(deepcopy(X))
        elif any(map(lambda x: x is None, X)):
            M = list(deepcopy(X))
        else:
            # otherwise, assume all entries are list-like
            M = list(map(list, deepcopy(X)))

        M = np.array(M)
    else:
        M = X.copy()  # numpy, pandas, and scipy
    # END create a numpy array with same dims as X -- -- -- -- -- -- --

    try:
        M[pd.isna(M)] = 'nan'
    except:
        pass

    try:
        M = M.to_numpy()
    except:
        pass

    M = np.char.replace(np.array(M).astype(str), 'None', 'nan')

    M = np.char.replace(M, '<NA>', 'nan')

    M = np.char.replace(M, 'NaT', 'nan')

    M = np.char.upper(M)

    return (M == 'NAN').astype(bool)


def nan_mask(
    X: XContainer
) -> npt.NDArray[bool]:
    """This function combines pybear :func:`nan_mask_numerical` and
    :func:`nan_mask_string`, giving a centralized location for masking
    numerical and non-numerical data.

    For full details, see the docs for `nan_mask_numerical` and
    `nan_mask_string`.

    Briefly, when passing numerical or non-numerical data, this function
    accepts Python built-ins, numpy arrays, pandas dataframes/series,
    and polars dataframes/series of shape (n_samples, n_features) or
    (n_samples, ) and returns an identically sized numpy array of
    booleans indicating the locations of nan-like representations. Also,
    when passing numerical data, this function accepts scipy sparse
    matrices / arrays of all formats except dok and lil. In that case,
    a numpy boolean vector of shape identical to that of the sparse
    object's 'data' attribute is returned. "nan-like representations"
    include, at least, np.nan, pandas.NA, pandas.NaT, None (of type
    None, not string "None"), and string representations of "nan".
    This function does not accept any ragged Python built-ins, numpy
    recarrays, or numpy masked arrays.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The object for which to locate nan-like representations.

    Returns
    -------
    mask : numpy.ndarray[bool]
        shape (n_samples, n_features) or (n_samples,) or (n_non_zero_values, )

        Indicates the locations of nan-like representations in `X` via
        the value boolean True. Values that are not nan-like are False.

    Notes
    -----
    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.DataFrame | pandas.Series]

    PolarsTypes:
        polars.DataFrame | polars.Series]

    ScipySparseTypes:
        ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
        | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
        | ss._bsr.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    Examples
    --------
    >>> from pybear.utilities import nan_mask
    >>> import numpy as np
    >>> X1 = np.arange(6).astype(np.float64)
    >>> X1[0] = np.nan
    >>> X1[-1] = np.nan
    >>> X1
    array([nan,  1.,  2.,  3.,  4., nan])
    >>> nan_mask(X1)
    array([ True, False, False, False, False,  True])

    >>> X2 = list('vwxyz')
    >>> X2[0] = 'nan'
    >>> X2[2] = 'nan'
    >>> X2
    ['nan', 'w', 'nan', 'y', 'z']
    >>> nan_mask(X2)
    array([ True, False,  True, False, False])

    """


    if isinstance(X, (str, dict)) \
            and not isinstance(X,(ss.dok_matrix, ss.dok_array)):
        raise TypeError(f"only list-like or array-like objects are allowed.")

    try:
        if isinstance(X, (list, tuple, set)):
            pd.DataFrame(list(X)).to_numpy().astype(np.float64)
            # if did not except
            raise IndexError
        elif hasattr(X, 'astype'):  # numpy, pandas, and scipy
            if isinstance(X,
                (ss.dok_matrix, ss.lil_matrix, ss.dok_array, ss.lil_array)
            ):
                raise UnicodeError
            X.astype(np.float64)
            # if did not except
            raise MemoryError
        elif hasattr(X, 'cast'):  # polars
            X.cast(pl.Float64)
            # if did not except
            raise TimeoutError
        else:
            raise NotImplementedError
    except UnicodeError:
        raise TypeError(f"'X' cannot be scipy sparse dok or lil")
    except NotImplementedError:
        raise TypeError(f"invalid type {type(X)} in nan_mask")
    except IndexError:
        # do this out from under the try in case this excepts
        return nan_mask_numerical(X)
    except MemoryError:
        # do this out from under the try in case this excepts
        return nan_mask_numerical(X.astype(np.float64))
    except TimeoutError:
        # polars -- do this out from under the try in case this excepts
        return nan_mask_numerical(X.cast(pl.Float64))
    except Exception as e:
        return nan_mask_string(X)








