# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias,
)
from .__type_aliases import (
    NumpyTypes,
    PandasTypes,
    PolarsTypes,
    ScipySparseTypes
)

import numbers

from ._num_features import num_features
from ._num_samples import num_samples


XContainer: TypeAlias = \
    NumpyTypes | PandasTypes | PolarsTypes | ScipySparseTypes



def check_shape(
    X: XContainer,
    min_features: int=1,
    max_features: int | None = None,
    min_samples: int=1,
    sample_check: int | None = None,
    allowed_dimensionality: Sequence[int] = (1, 2)
) -> tuple[int, ...]:
    """Check the shape of a data-bearing object against user-defined
    criteria.

    `X` must have a 'shape' method.

    The number of samples in `X` must be greater than or equal to
    `min_samples`.

    If `sample_check` is not None (must be an integer greater than or
    equal to `min_samples`), the number of samples in `X` must equal
    `sample_check`.

    The number of features in `X` must be greater than or equal to
    `min_features`.

    If `max_features` is not None (must be an integer greater than or
    equal to `min_features`), then number of features in `X` cannot
    exceed `max_features`.

    The dimensionality of `X` must be one of the allowed values in
    `allowed_dimensionality`.

    Parameters
    ----------
    X : XContainer of shape (n_samples, n_features) or (n_samples,)
        The data-bearing object for which to get and validate the shape.
        Must have a 'shape' attribute.
    min_features : int
        The minimum number of features required in `X`; must be greater
        than or equal to zero.
    max_features : int | None
        The maximum number of features allowed in `X`; if not None, must
        be greater than or equal to `min_features`. If None, then there
        is no restriction on the maximum number of features in `X`.
    min_samples : int
        The minimum number of samples required in `X`; must be greater
        than or equal to zero. Ignored if `sample_check` is not None.
    sample_check : int | None
        The exact number of samples allowed in `X`. If not None, must be
        a non-negative integer. Use this to check, for example, that the
        number of samples in y equals the number of samples in `X`. If
        None, this check is not performed.
    allowed_dimensionality : Sequence[int]
        The allowed dimensionalities of `X`. All entries must be greater
        than zero and less than or equal to two.

    Raises
    ------
        ValueError:

            The number of dimensions of `X` is not allowed.

            The number of samples in `X` does not match `sample_check`.

            The number of samples in `X` is below `min_samples`.

            The number of features in `X` is below `min_features`.

            The number of features in `X` is above `max_features`.

    Returns
    -------
    shape : tuple[int, ...]
        The shape of `X`.

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
    >>> from pybear.base import check_shape
    >>> import numpy as np
    >>> X = np.random.randint(0, 10, (5, 3))
    >>> kwargs = {'min_features': 1, 'max_features': None, 'min_samples': 1,
    ...     'sample_check': None, 'allowed_dimensionality': (2, )}
    >>>
    >>> # Demonstrate a valid container passes and returns the shape
    >>> print(check_shape(X, **kwargs))
    (5, 3)
    >>>
    >>> # Demonstrate an invalid container raises ValueError
    >>> X = np.random.randint(0, 10, (5,))
    >>> try:
    ...     check_shape(X, **kwargs)
    ... except Exception as e:
    ...     print(repr(e))
    ValueError('The dimensionality of the passed object must be in (2,). Got 1.')

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if not hasattr(X, 'shape'):
        raise TypeError("the passed object must have a 'shape' attribute.")

    err_msg = f"'min_features' must be a non-negative integer"
    if not isinstance(min_features,  numbers.Integral):
        raise TypeError(err_msg)
    if isinstance(min_features, bool):
        raise TypeError(err_msg)
    if min_features < 0:
        raise ValueError(err_msg)
    del err_msg

    if max_features is not None:
        err_msg = (f"'max_features' must be None or a non-negative integer "
            f"greater than or equal to 'min_features'")
        if not isinstance(max_features,  numbers.Integral):
            raise TypeError(err_msg)
        if isinstance(max_features, bool):
            raise TypeError(err_msg)
        if max_features < min_features:
            raise ValueError(err_msg)
        del err_msg

    if sample_check is None:
        err_msg = f"'min_samples' must be a non-negative integer"
        if not isinstance(min_samples,  numbers.Integral):
            raise TypeError(err_msg)
        if isinstance(min_samples, bool):
            raise TypeError(err_msg)
        if min_samples < 0:
            raise ValueError(err_msg)
    elif sample_check is not None:
        err_msg = (f"'sample_check' must be None or a non-negative integer.")
        if not isinstance(sample_check, numbers.Integral):
            raise TypeError(err_msg)
        if isinstance(sample_check, bool):
            raise TypeError(err_msg)
        if sample_check < 0:
            raise ValueError(err_msg)
        del err_msg

    err_msg = (f"'allowed_dimensionality' must be a vector-like sequence "
        f"of integers greater than zero and less than three.")
    try:
        __ = allowed_dimensionality

        if isinstance(__, numbers.Integral):
            if isinstance(__, bool):
                raise Exception
            __ = (__, )
        iter(__)
        if isinstance(__, (str, dict)):
            raise Exception
        if not all(map(isinstance, __, (numbers.Integral for _ in __))):
            raise Exception
        if any(map(isinstance, __, (bool for _ in __))):
            raise Exception
        if not all(map(lambda x: x > 0, __)):
            raise UnicodeError
        if not all(map(lambda x: x <= 2, __)):
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except:
        raise TypeError(err_msg)
    allowed_dimensionality = __
    del __
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if len(X.shape) not in allowed_dimensionality:
        raise ValueError(
            f"The dimensionality of the passed object must be in "
            f"{allowed_dimensionality}. Got {len(X.shape)}."
        )

    _samples = num_samples(X)
    _features = num_features(X)

    if sample_check is not None:
        if _samples != sample_check:
            raise ValueError(
                f"passed object has {_samples} samples, but :param: "
                f"sample_check requires there be exactly {sample_check} "
                f"samples"
            )
    elif sample_check is None:
        if _samples < min_samples:
            raise ValueError(
                f"passed object has {_samples} sample(s), minimum required "
                f"is {min_samples}"
            )


    if _features < min_features:
        raise ValueError(
            f"passed object has {_features} samples, minimum required is "
            f"{min_features}"
        )

    if max_features is not None and _features > max_features:
        raise ValueError(
            f"passed object has {_features} features, maximum allowed is "
            f"{max_features}"
        )


    return X.shape





