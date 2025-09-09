# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterable,
    TypeAlias
)
import numpy.typing as npt
from .__type_aliases import (
    PythonTypes,
    NumpyTypes,
    PandasTypes,
    PolarsTypes
)

from copy import deepcopy

import numpy as np
import scipy.sparse as ss



# dok & lil intentionally omitted
ScipySparseTypes: TypeAlias = (
    ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
    | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
    | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
    | ss._bsr.bsr_array
)

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def inf_mask(
    X: XContainer
) -> npt.NDArray[bool]:
    """Return a boolean numpy array or vector indicating the locations
    of infinity-like values in the data.

    "Infinity-like values" include, at least, numpy.inf, -numpy.inf,
    numpy.PINF, numpy.NINF, math.inf, -math.inf, str('inf'), str('-inf'),
    float('inf'), float('-inf'), decimal.Decimal('Infinity'), and
    'decimal.Decimal('-Infinity').

    This module accepts Python lists, tuples, and sets, numpy arrays,
    pandas series and dataframes, polars series and dataframes, and all
    scipy sparse matrices/arrays except dok and lil formats. This module
    does not accept ragged Python built-in containers, numpy recarrays,
    or numpy masked arrays.

    In all cases, the given containers are ultimately coerced to a numpy
    representation of the data. The boolean mask is then generated from
    the numpy container. Numpy arrays are handled as is. Pandas objects
    are converted to a numpy array via the 'to_numpy' method. Polars
    objects are first cast to a pandas dataframe by the 'to_pandas'
    method. It is up to the user to ensure the particular infinity-like
    values you are using in a polars container are preserved when
    converted to a pandas dataframe by this method. The new pandas
    container is then handled in the same way as any other passed pandas
    container. For scipy sparse objects, the 'data' attribute (which is
    a numpy ndarray) is extracted.

    In the cases of 1D and 2D shaped objects of shape (n_samples, ) or
    (n_samples, n_features), return an identically shaped boolean numpy
    array. In the cases of scipy sparse objects, return a boolean numpy
    vector of shape equal to that of the 'data' attribute of the sparse
    object.

    'dok' is the only scipy sparse format that does not have a 'data'
    attribute, and for that reason it is not handled by `inf_mask`.
    scipy sparse 'lil' cannot be masked in an elegant way, and for that
    reason it is also not handled by `inf_mask`. All other scipy sparse
    formats only take numeric data.

    This module relies heavily on numpy.isinf to locate infinity-like
    values in float dtype data. All infinity-like forms mentioned above
    are found by this function in float dtype data.

    Of the third-party containers handled by this module, none of them
    allow for infinity-like values in integer dtype data. This makes for
    straightforward handling of these objects, in that every position in
    the returned boolean mask must be False.

    String and object dtype data are not handled by the numpy.isinf
    function. Fortunately, at creation of a string dtype numpy array,
    if there are float or string infinity-like values in it almost all
    of them are coerced to str('inf') or str('-inf'). The exception is
    decimal.Decimal('Infinity') and decimal.Decimal('-Infinity'), which
    are coerced to str('Infinity') and str('-Infinity'). Building a mask
    from this is straightforward. But object dtype numpy arrays do not
    make these conversions, so the float infinity-likes stay in the
    object array in float format. This poses a problem because
    numpy.isinf cannot take object formats, but it is very plausible
    that there are infinity-likes in it. So object dtype data are to
    cast to string dtype, which forces the conversion.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples, )
        The object for which to mask infinity-like representations.

    Returns
    -------
    mask : numpy.ndarray[bool]
        shape (n_samples, n_features) or (n_samples, ) or (n_non_zero_values, ),
        Indicates the locations of infinity-like representations in `X`
        via the value boolean True. Values that are not infinity-like
        are False.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list | tuple | set | list[list] | tuple[tuple]]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    ScipySparseTypes:
        ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
        | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
        | ss._bsr.bsr_array

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    See Also
    --------
    numpy.isinf
    numpy.inf
    numpy.PINF
    numpy.NINF
    math.inf
    decimal.Decimal

    Examples
    --------
    >>> from pybear.utilities import inf_mask
    >>> import numpy as np
    >>> X = np.arange(5).astype(np.float64)
    >>> X[1] = float('inf')
    >>> X[-1] = float('-inf')
    >>> X
    array([  0.,  inf,   2.,   3., -inf])
    >>> inf_mask(X)
    array([False,  True, False, False,  True])

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    _err_msg = (
        f"'obj' must be an array-like with a copy() or clone() method, "
        f"such as python built-ins, "
        f"\nnumpy arrays, pandas series/dataframes, polars "
        f"series/arrays, or scipy sparse matrices/arrays. "
        f"\nif passing a scipy sparse object, it cannot be dok or lil. "
        f"\nnumpy recarrays or masked arrays are not allowed."
    )

    try:
        iter(X)
        if isinstance(X, (str, dict)):
            raise Exception
        if isinstance(X, tuple):
            pass
            # tuple doesnt have copy()
            # notice the elif
        elif not hasattr(X, 'copy') and not hasattr(X, 'clone'):
            raise Exception
        if isinstance(X, (np.recarray, np.ma.MaskedArray)):
            raise Exception
        if hasattr(X, 'toarray'):
            if not hasattr(X, 'data'):  # ss dok
                raise Exception
            elif all(map(isinstance, X.data, (list for _ in X.data))):  # ss lil
                raise Exception
    except Exception as e:
        raise TypeError(_err_msg)

    # determine if python built-ins are ragged
    if isinstance(X, (list, tuple, set)):
        try:
            # if is all strings, get these iterables out of the equation
            if all(map(isinstance, X, (str for i in X))):
                raise Exception
            # so it cant be all strings, but there might be some strings.
            # of those that are not strings, if any are iterable it is
            # ragged so reject.
            if any(map(isinstance, X, (str for i in X))):
                if any(map(
                    lambda x: isinstance(x, Iterable),
                    [i for i in X if not isinstance(i, str)]
                )):
                    raise UnicodeError
            # cant be strings or a mix of strings and iters, so any iters means 2D
            list(map(iter, X))
            # if 2D, check for raggedness
            if len(set(map(len, X))) != 1:
                raise UnicodeError
        except UnicodeError:
            raise ValueError(
                f"inf_mask does not accept ragged python built-ins"
            )
        except Exception as e:
            # is 1D
            pass

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # create a numpy array with same dims as X -- -- -- -- -- -- -- --
    if hasattr(X, 'toarray'):
        M = X.data.copy()
    elif hasattr(X, 'clone'):
        # Polars uses zero-copy conversion when possible, meaning the
        # underlying memory is still controlled by Polars and marked
        # as read-only. NumPy and Pandas may inherit this read-only
        # flag, preventing modifications.
        M = X.to_pandas().copy()  # polars
    elif isinstance(X, (list, tuple, set)):
        # we cant just map list here, could have strings inside
        # but we do know its not ragged
        try:
            # if any strings inside, must be 1D
            if any(map(isinstance, X, (str for i in X))):
                raise Exception
            # so there cant be any strings inside. now if there are iterables
            # it must be 2D
            list(map(iter, X))
            raise MemoryError
        except MemoryError:
            # for 2D
            M = list(map(list, deepcopy(X)))
        except Exception as e:
            # for 1D
            M = list(deepcopy(X))

        M = np.array(M)
    else:
        M = X.copy()    # X.copy()  # numpy, pandas, and scipy


    try:
        M = M.to_numpy()   # works for pandas and polars
    except:
        pass
    # END create a numpy array with same dims as X -- -- -- -- -- -- --

    # want to be able to handle int dtype objects. if X is int dtype,
    # then it cant possibly have 'inf' int it. to avoid converting an int
    # dtype over to float64 (even if it would be only a transient state),
    # look to see if it is int dtype and just return a mask of Falses.
    if 'int' in str(M.dtype).lower():
        return np.zeros(M.shape).astype(bool)

    try:
        # np.isinf cannot take non-num dtype. try to coerce the data to
        # float64, if it wont go, try to handle it as string/object.
        # otherwise, if data is already float dtype, then we are good here.
        return np.isinf(M.astype(np.float64)).astype(bool)
    except:
        # fortunately, at creation of a str np array, if there are float
        # or str inf-likes in it, almost all of them are coerced to
        # str('inf') or str('-inf'). the exception is decimal.Decimal('Infinity')
        # and decimal.Decimal('-Infinity'), which are coerced to str('Infinity')
        # and str('-Infinity'). so this is elegant enough to handle. but
        # object dtype np arrays do not make these coersions, the float
        # inf-likes stay in the object array in float format. this poses
        # a problem because np.isinf cannot take object formats, but it
        # is very plausible that there are inf-likes in it. so need to
        # convert the object dtype to str, which will force the coersion.
        M = M.astype(str)
        M = (M == 'inf') + (M == '-inf') + (M == 'Infinity') + (M == '-Infinity')
        return M.astype(bool)





