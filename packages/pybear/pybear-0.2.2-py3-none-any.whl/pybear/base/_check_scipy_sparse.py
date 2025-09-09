# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Literal,
    Sequence,
)

import scipy.sparse as ss



def check_scipy_sparse(
    X: Any,
    allowed: (
        Literal[False] | None
        | Sequence[Literal["csr", "csc", "coo", "dia", "lil", "dok", "bsr"]]
    )
) -> None:
    """Check whether a passed data container is a scipy sparse matrix /
    array.

    If it is, check the type against the allowed types specified by the
    user in `allowed`. If `X` is not a scipy sparse container, skip all
    checks and return None. If `X` is an allowed scipy sparse container,
    return None. If `X` is a disallowed scipy container, do not recast
    the passed container to a valid scipy sparse container but raise a
    TypeError.

    Parameters
    ----------
    X : array_like of shape (n_samples, n_features) or (n_samples, )
        The data to be checked whether it is an allowed scipy sparse
        matrix / array. This parameter is not checked for being a valid
        data container. It only undergoes checks if it is a scipy sparse
        container.
    allowed : Literal[False] | None | Sequence[str]
        If None or False, disallow any scipy sparse containers. Otherwise,
        a vector-like sequence of literals indicating the types of scipy
        sparse matrices / arrays that are allowed.  Valid literals are
        'csr', 'csc', 'coo', 'dia', 'lil', 'dok', and 'bsr'. If a
        disallowed scipy sparse type is passed it is not recast to a
        valid type, but a TypeError is raised.

    Raises
    ------
    TypeError:
        If `allowed` is None or False and `X` is a scipy sparse container.

        If `X` is a scipy sparse container but not one of the allowed
        containers.

    Returns
    -------
    None

    Examples
    --------
    >>> from pybear.base import check_scipy_sparse
    >>> import numpy as np
    >>> import scipy.sparse as ss
    >>> X_np = np.random.uniform(0, 1, (5, 3))
    >>> X_csc = ss.csc_array(X_np)
    >>> print(check_scipy_sparse(X_csc, ['csc', 'csr', 'coo']))
    None
    >>> try:
    ...     check_scipy_sparse(X_csc, False)
    ... except Exception as e:
    ...     print(repr(e)[:53])
    TypeError("X is <class 'scipy.sparse._csc.csc_array'>

    """

    # all of this just to validate :param: 'allowed'

    err_msg = (f":param: 'allowed' must be None, literal False, or a "
        f"vector-like sequence of literals indicating the types of scipy "
        f"sparse containers that are allowed. see the docs for the valid "
        f"literals accepted in the :param: 'allowed' sequence.")

    try:
        if allowed is None:
            raise UnicodeError
        if allowed is False:
            raise UnicodeError
        iter(allowed)
        if isinstance(allowed, (str, dict)):
            raise Exception
        if not all(map(isinstance, allowed, (str for _ in allowed))):
            raise Exception
        allowed = list(map(str.lower, allowed))
        valid = ["csr", "csc", "coo", "dia", "lil", "dok", "bsr"]
        for _ in allowed:
            if _ not in valid:
                raise MemoryError
        del valid
    except UnicodeError:
        pass
    except MemoryError:
        raise ValueError(err_msg)
    except:
        raise TypeError(err_msg)

    del err_msg

    _is_scipy_sparse: bool = hasattr(X, 'toarray')

    if not _is_scipy_sparse:
        return
    elif _is_scipy_sparse:

        if allowed in [None, False]:
            raise TypeError(
                f"X is {type(X)} but scipy sparse is disallowed."
            )

        allowed_dtypes = []
        for _ss in allowed:
            if _ss == "csr":
                allowed_dtypes.extend((ss.csr_matrix, ss.csr_array))
            elif _ss == "csc":
                allowed_dtypes.extend((ss.csc_matrix, ss.csc_array))
            elif _ss == "coo":
                allowed_dtypes.extend((ss.coo_matrix, ss.coo_array))
            elif _ss == "dia":
                allowed_dtypes.extend((ss.dia_matrix, ss.dia_array))
            elif _ss == "lil":
                allowed_dtypes.extend((ss.lil_matrix, ss.lil_array))
            elif _ss == "dok":
                allowed_dtypes.extend((ss.dok_matrix, ss.dok_array))
            elif _ss == "bsr":
                allowed_dtypes.extend((ss.bsr_matrix, ss.bsr_array))


        if type(X) not in allowed_dtypes:
            raise TypeError(
                f"X of type {type(X)} is not in allowed scipy sparse "
                f"containers: {', '.join(allowed)}."
            )

        del allowed_dtypes





