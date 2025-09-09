# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence
)

import numpy as np

from ._cast_to_ndarray import cast_to_ndarray as _cast_to_ndarray
from ._check_is_finite import check_is_finite
from ._check_scipy_sparse import check_scipy_sparse
from ._ensure_2D import ensure_2D as _ensure_2D
from ._check_dtype import check_dtype
from ._check_shape import check_shape
from ._set_order import set_order
from ._copy_X import copy_X as _copy_X



def validate_data(
    X,
    *,
    copy_X:bool = True,
    cast_to_ndarray:bool = False,
    accept_sparse:Sequence[
        Literal["csr", "csc", "coo", "dia", "lil", "dok", "bsr"]
        | Literal[False] | None
    ] = ("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
    dtype:Literal['numeric', 'str', 'any'] = 'any',
    require_all_finite:bool = True,
    cast_inf_to_nan:bool = True,
    standardize_nan:bool = True,
    allowed_dimensionality:Sequence[int] = (1,2),
    ensure_2d:bool = True,
    order:Literal['C', 'F'] = 'C',
    ensure_min_features:int = 1,
    ensure_max_features:int | None = None,
    ensure_min_samples:int = 1,
    sample_check:int | None = None
):
    """Validate characteristics of `X` and apply some select transformative
    operations.

    This module is intended for validation of `X` in methods of pybear
    estimators and transformers, but can be used in stand-alone
    applications.

    All the functionality carried out in this module is executed by
    individual modules, that is, this module is basically a central hub
    that unifies all the separate operations. Some of the individual
    modules may have particular requirements of `X` such as a specific
    container like a numpy array, or that the container expose methods
    like 'copy' or attributes like 'shape'. See the individual modules
    for specifics.

    This module can perform many checks and transformative operations in
    preparation for pybear estimators or transformers. See the Parameters
    section for an exhaustive list of the functionality.

    Parameters
    ----------
    X : array_like of shape (n_samples, n_features) or (n_samples,)
        The data to be validated.
    copy_X : bool, default=True
        Whether to operate directly on the passed `X` or create a copy.
    cast_to_ndarray : bool, default=False
        If True, convert the passed `X` to numpy ndarray.
    accept_sparse : Sequence[str] | Literal[False] | None
        default=("csr", "csc", "coo", "dia", "lil", "dok", "bsr").

        The scipy sparse matrix/array formats that are allowed. If no
        scipy sparse are allowed, literal False or None can be passed,
        and an exception will be raised if `X` is a scipy sparse object.
        Otherwise, must be a 1D vector-like (such as a Python list or
        tuple) containing some or all of the 3-character acronyms shown
        here. Not case sensitive. Entries cover both the 'matrix' and
        'array' formats, e.g., ['csr', 'csc'] will allow csr_matrix,
        csr_array, csc_matrix, and csc_array formats.
    dtype : Literal['numeric','str','any'], default='any'
        The allowed datatype of `X`. If 'numeric', data that cannot be
        coerced to a numeric datatype will raise a TypeError. If 'str',
        all data in `X` is must be strings or a TypeError is raised. If
        'any', no restrictions are imposed on the datatype of `X`.
    require_all_finite : bool, default=True
        If True, block data that has undefined values, in particular,
        nan-like and infinity-like values. If False, nan-like and
        infinity-like values are allowed.
    cast_inf_to_nan : bool, default=True
        If True, coerce any infinity-like values in the data to
        numpy.nan; if False, leave any infinity-like values as is.
    standardize_nan : bool, default=True
        If True, coerce all nan-like values in the data to numpy.nan; if
        False, leave all the nan-like values in the given state.
    allowed_dimensionality : Sequence[int], default = (1,2)
        The allowed dimension of `X`. All entries must be greater than
        zero and less than or equal to two. Examples: (1,)  {1,2}, [2].
    ensure_2d : bool, default=True
        Coerce the data to a 2-dimensional format. For example, a 1D
        numpy vector would be reshaped to a 2D numpy array; a 1D pandas
        series would be converted to a 2D pandas dataframe.
    order : Literal['C', 'F'], default='C'
        Only applicable if `X` is a numpy array or `cast_to_ndarray` is
        True. Sets the memory order of `X`. 'C' is row-major and 'F' is
        column-major. The default for numpy arrays is 'C', and major
        packages like scikit typically expect to see numpy arrays with
        'C' order. pybear recommends that this parameter be used with
        understanding of the potential performance implications of
        changing the memory order of `X` on downstream processes that
        may be designed for 'C' order.
    ensure_min_features : int, default=1
        The minimum number of features (columns) that must be in `X`.
    ensure_max_features : int | None, default = None
        The maximum number of features allowed in `X`; if not None, must
        be greater than or equal to `ensure_min_features`. If None, then
        there is no restriction on the maximum number of features in `X`.
    ensure_min_samples : int, default=1
        The minimum number of samples (rows) that must be in `X`. Ignored
        if `sample_check` is not None.
    sample_check : int | None = None
        The exact number of samples allowed in `X`. If not None, must be
        a non-negative integer. Use this to check, for example, that the
        number of samples in `y` equals the number of samples in `X`. If
        None, this check is not performed.

    Returns
    -------
    X : array_like of shape (n_samples, n_features) or (n_samples,)
        The validated, and possibly modified, data.

    Examples
    --------
    >>> from pybear.base import validate_data
    >>> import numpy as np
    >>> import pandas as pd
    >>> import scipy.sparse as ss
    >>> X_np = np.array([[0, 1], [2, 3], [4, 5]], dtype=np.int8)
    >>> X_pd = pd.DataFrame(data=X_np, columns=['A', 'B'])
    >>> X_ss = ss.csr_array(X_np)
    >>> kwargs = {
    ... 'copy_X': False,
    ... 'cast_to_ndarray': True,
    ... 'accept_sparse': False,
    ... 'dtype': 'any',
    ... 'require_all_finite': False,
    ... 'cast_inf_to_nan': False,
    ... 'standardize_nan': False,
    ... 'allowed_dimensionality': (1, 2),
    ... 'ensure_2d': False,
    ... 'order': 'C',
    ... 'ensure_min_features': 1,
    ... 'ensure_max_features': None,
    ... 'ensure_min_samples': 1,
    ... 'sample_check': None
    ... }
    >>>
    >>> # demonstrate pandas dataframe is cast to ndarray
    >>> out = validate_data(X_pd, **kwargs)
    >>> print(out)
    [[0 1]
     [2 3]
     [4 5]]
    >>>
    >>> # demonstrate scipy sparse is rejected
    >>> try:
    ...     validate_data(X_ss, **kwargs)
    ... except Exception as e:
    ...     print(repr(e)[:53])
    TypeError("X is <class 'scipy.sparse._csr.csr_array'>
    >>>
    >>> # demonstrate numpy ndarray passes and is not mutated
    >>> print(validate_data(X_np, **kwargs))
    [[0 1]
     [2 3]
     [4 5]]

    """

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # no validation for X! the entire module is for validation of X!

    # copy_X -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(copy_X, bool):
        raise TypeError(f"'copy_X' must be boolean.")
    # END copy_X -- -- -- -- -- -- -- -- -- -- --

    # cast_to_ndarray -- -- -- -- -- -- -- -- -- --
    if not isinstance(cast_to_ndarray, bool):
        raise TypeError(f"'cast_to_ndarray' must be boolean.")
    # END cast_to_ndarray -- -- -- -- -- -- -- -- --

    # # accept_sparse -- -- -- -- -- -- -- -- -- --
    # this is covered by check_scipy_sparse
    # # END accept_sparse -- -- -- -- -- -- -- -- --

    # # dtype -- -- -- -- -- -- -- -- -- -- -- --
    # this is covered by check_dtype()
    # # END dtype -- -- -- -- -- -- -- -- -- -- --

    # require_all_finite -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(require_all_finite, bool):
        raise TypeError(f"'require_all_finite' must be boolean.")
    # END require_all_finite -- -- -- -- -- -- -- -- -- -- --

    # cast_inf_to_nan -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(cast_inf_to_nan, bool):
        raise TypeError(f"'cast_inf_to_nan' must be boolean.")
    # END cast_inf_to_nan -- -- -- -- -- -- -- -- -- -- --

    # standardize_nan -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(standardize_nan, bool):
        raise TypeError(f"'standardize_nan' must be boolean.")
    # END standardize_nan -- -- -- -- -- -- -- -- -- -- --


    if require_all_finite and standardize_nan:
        raise ValueError(
            f"if :param: require_all_finite is True, then :param: "
            f"standardize_nan must be False."
        )

    if require_all_finite and cast_inf_to_nan:
        raise ValueError(
            f"if :param: require_all_finite is True, then :param: "
            f"cast_inf_to_nan must be False."
        )

    # allowed_dimensionality -- -- -- -- -- -- -- -- -- -- -- --
    # this is covered by check_shape()
    # END allowed_dimensionality -- -- -- -- -- -- -- -- -- -- --

    # ensure_2d -- -- -- -- -- -- -- -- -- -- -- --
    if not isinstance(ensure_2d, bool):
        raise TypeError(f"'ensure_2d' must be boolean.")
    # END ensure_2d -- -- -- -- -- -- -- -- -- -- --

    # order -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # this is covered by set_order()
    # order -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # # ensure_min_features -- -- -- -- -- -- -- -- -- -- -- -- --
    # this is handled by check_shape()
    # # END ensure_min_features -- -- -- -- -- -- -- -- -- -- -- --
    #
    # # ensure_max_features -- -- -- -- -- -- -- -- -- -- -- -- --
    # this is handled by check_shape()
    # # END ensure_max_features -- -- -- -- -- -- -- -- -- -- -- --
    #
    # # ensure_min_samples / sample_check -- -- -- -- -- -- -- -- -- --
    # this is handled by check_shape()
    # # END ensure_min_samples / sample_check -- -- -- -- -- -- -- -- --

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # requirements of X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # some attr/methods are not *absolutely* necessary, such as:
    # 'copy' is only called throughout validate_data and submodules if
    #   'copy_X' is True
    # 'astype' is only called by check_dtype() when 'dtype' is 'numeric'
    # 'reshape'/'to_frame' is only called if ensure_2D:True and X not 2D
    # but check_shape() is not optional, ensure_min_features and
    # ensure_min_samples must be passed, so 'shape' is a must, but it
    # is failing in other random ways prior to check_shape(). check it
    # here to standardize the error.
    try:
        X.shape
    except:
        raise ValueError(
            f"\nThe passed object does not have a 'shape' attribute. "
            f"\nAll pybear estimators and transformers require data-bearing "
            f"objects to have a 'shape' attribute, like numpy arrays, pandas "
            f"dataframes, and scipy sparse matrices / arrays."
        )
    # END requirements of X -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # avoid multiple copies of X. do not set 'copy_X' for each of the
    # functions to True! create only one copy of X, set copy_X to False
    # for all the functions.
    if copy_X:
        _X = _copy_X(X)
    else:
        _X = X
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # accept_sparse
    check_scipy_sparse(
        _X,
        allowed=accept_sparse
    )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if cast_to_ndarray:
        _X = _cast_to_ndarray(
            _X,
            copy_X=False
        )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if ensure_2d:
        _X = _ensure_2D(
            _X,
            copy_X=False
        )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if isinstance(_X, np.ndarray):
        _X = set_order(
            _X,
            order=order,
            copy_X=False
        )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if require_all_finite or cast_inf_to_nan or standardize_nan:

        # this must be before check_dtype to ensure that ndarrays have
        # only np.nans in them if standardize_nan is True. otherwise
        # an ndarray that is expected to have only np.nans in it will
        # fail a 'numeric' dtype check before the nans are standardized.

        _X = check_is_finite(
            _X,
            allow_nan=not require_all_finite,
            allow_inf=not require_all_finite,
            cast_inf_to_nan=cast_inf_to_nan,
            standardize_nan=standardize_nan,
            copy_X=False
        )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    check_dtype(
        _X,
        allowed=dtype
    )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    check_shape(
        _X,
        min_features=ensure_min_features,
        max_features=ensure_max_features,
        min_samples=ensure_min_samples,
        sample_check=sample_check,
        allowed_dimensionality=allowed_dimensionality
        # if n_features_in_ is 1, then dimensionality could be 1 or 2, 
        # for any number of features greater than 1 dimensionality must
        # be 2.
    )
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    return _X






