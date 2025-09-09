# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
from .__type_aliases import (
    NumpyTypes,
    PandasTypes,
    PolarsTypes,
    ScipySparseTypes
)

from ._num_features import num_features


XContainer: TypeAlias = \
    NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def check_n_features(
    X: XContainer,
    n_features_in_: int | None,
    reset: bool
) -> int:
    """Set the `n_features_in_` attribute, or check against it.

    pybear recommends calling `reset=True` in `fit` and in the first
    call to `partial_fit`. All other methods that validate `X` should
    set `reset=False`.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The input data, with a 'shape' attribute.
    n_features_in_ : int | None
        The number of features in the data. If this attribute exists,
        it is an integer. If it does not exist, it is None.
    reset : bool
        If True:
            The `n_features_in_` attribute is set to `X.shape[1]`.

        If False:
            If `n_features_in_` exists check it is equal to `X.shape[1]`.

            If `n_features_in_` does *not* exist the check is skipped.

    Raises
    ------
    ValueError:
        If `X` has no columns (is empty along the column axis).

        If `reset=False` and the number of features in `X` does not equal
            `n_features_in_`.

    Returns
    -------
    n_features : int
        The number of features in `X`.

    Notes
    -----

    **Type Aliases**

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
        NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes

    Examples
    --------
    >>> from pybear.base import check_n_features
    >>> import numpy as np
    >>> X = np.random.randint(0, 10, (8, 5))
    >>> check_n_features(X, n_features_in_=None, reset=True)
    5
    >>> try:
    ...     check_n_features(X, n_features_in_=4, reset=False)
    ... except Exception as e:
    ...     print(repr(e))
    ValueError('X has 5 feature(s), but expected 4.')

    """

    n_features = num_features(X)

    # this is somewhat arbitrary, in that there is nothing following in
    # this module that requires this. there is nothing in the near
    # periphery that will be impacted if this is changed / removed.
    if n_features == 0:
        raise ValueError("X does not contain any features")

    if reset:
        return n_features

    # reset must be False for all below v v v v v v v v v v v
    if n_features_in_ is None:
        return

    if n_features != n_features_in_:
        raise ValueError(
            f"X has {n_features} feature(s), but expected {n_features_in_}."
        )

    # if get to here, n_features must == n_features_in__
    return int(n_features)




