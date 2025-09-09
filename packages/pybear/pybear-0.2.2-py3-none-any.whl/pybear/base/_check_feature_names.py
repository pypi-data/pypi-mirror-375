# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
import numpy.typing as npt

import warnings
import numpy as np

from ._get_feature_names import get_feature_names



# this parallels the check_feature_names method of sklearn BaseEstimator
# which is called by the _validate_data method of sklearn BaseEstimator
def check_feature_names(
    X: Any,
    feature_names_in_: npt.NDArray[object] | None,
    reset: bool
) -> npt.NDArray[object] | None:
    """Set or check the `feature_names_in_` attribute.

    pybear recommends setting `reset=True` in :meth:`fit` and in the
    first call to :meth:`partial_fit`. All other methods that validate
    `X` should set `reset=False`.

    If reset is True:
        Get the feature names from `X` and return. If `X` does not have
        valid string feature names, return None. `feature_names_in_`
        passed as a parameter to the function does not matter.

    If reset is False:
        When `feature_names_in_` exists and the checks of this module
        are satisfied then `feature_names_in_` is always returned.

        If `feature_names_in_` exists (a header was seen on first fit) and:
            `X` has a header:
            Validate that the feature names of `X` have the exact names
            and order as those seen during fit. If they are equal, return
            the feature names; if they are not equal, raise ValueError.

            `X` does not have a header:
            Warn and return `feature_names_in_`.

        If `feature_names_in_` does not exist and the checks of this
        module are satisfied then None is always returned regardless of
        any header that the current `X` may have.

        If `feature_names_in_` does not exist (a header was not seen on
        first fit) and:

            `X` has a header:  Warn and return None.

            `X` does not have a header: return None

    Parameters
    ----------
    X : array_like of shape (n_samples, n_features) or (n_samples, )
        The data from which to extract feature names. `X` will provide
        feature names if it is a dataframe constructed with a valid
        header of strings. Some objects that are known to yield feature
        names are pandas and polars dataframes. If `X` does not have a
        valid header then None is returned. Objects that are known to
        not yield feature names are numpy arrays and scipy sparse
        matrices/arrays.                  .
    feature_names_in_ : numpy.ndarray[object] of shape (n_features, )
        The feature names seen on the first fit, if an object with a
        valid header was passed on the first fit. None if feature names
        were not seen on the first fit.
    reset : bool
        Whether to reset the `feature_names_in_` attribute. If False,
        the feature names of `X` will be checked for consistency with
        feature names of data provided when reset was last True.

    Returns
    -------
    feature_names_in_ : numpy.ndarray[object] | None
        The validated feature names if feature names were seen the last
        time reset was set to True. None if the estimator/transformer
        did not see valid feature names at the first fit.

    Examples
    --------
    >>> from pybear.base import check_feature_names
    >>> import pandas as pd
    >>> import numpy as np
    >>> data = np.random.randint(0, 10, (5, 3))
    >>> feature_names_in_ = np.array(['a', 'b', 'c'])
    >>> X = pd.DataFrame(data=data, columns=list('abc'))

    # Verify accepts a valid header and returns it
    >>> check_feature_names(X, feature_names_in_=feature_names_in_, reset=False)
    array(['a', 'b', 'c'], dtype='<U1')

    """


    # passed_feature_names
    pfn: npt.NDArray[object] | None = get_feature_names(X)

    fni: npt.NDArray[object] | None = feature_names_in_


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # currently no validation of X is being done.
    # anticipate that this module might see...
    # python list of objects (low probability, but possible)
    # numpy-like 2D array
    # numpy-like 1D vector
    # pandas-like dataframe
    # pandas-like series
    # polars dataframe
    # polars series
    # any of the scipy sparse matrices / arrays (always 2D)


    try:
        if pfn is None:
            raise UnicodeError
        iter(pfn)
        if isinstance(pfn, (str, dict)):
            raise Exception
    except UnicodeError:
        pass
    except:
        raise TypeError(f"_columns like be a list-like iterable of strings")

    try:
        if fni is None:
            raise UnicodeError
        iter(fni)
        if isinstance(fni, (str, dict)):
            raise Exception
        assert all(map(isinstance, fni, (str for _ in fni)))
    except UnicodeError:
        pass
    except:
        raise TypeError(
            f"feature_names_in_ must be a list-like iterable of strings"
        )

    assert isinstance(reset, bool)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *f

    if reset:
        return pfn

    # v v v v if not resetting, check currently passed against previous v v v v
    if fni is None and pfn is None:
        # no feature names seen in fit and in X
        return

    if pfn is not None and fni is None:
        warnings.warn(
            f"X has feature names, but this instance was fitted without"
            " feature names."
        )
        return

    if pfn is None and fni is not None:
        warnings.warn(
            "X does not have feature names, but this instance was fitted "
            "with feature names."
        )
        return fni


    # validate the current feature names against the 'feature_names_in_' attribute
    base_err_msg = \
        f"The feature names should match those that were passed during fit. "

    if np.array_equiv(pfn, fni):
        return fni

    elif len(pfn) == len(fni) and np.array_equiv(sorted(pfn), sorted(fni)):

        # when out of order
        # ValueError: base_err_msg
        # Feature names must be in the same order as they were in fit.
        addon = (f"\nFeature names must be in the same order as they "
                 f"were in fit.")

    else:

        addon = ''

        UNSEEN = []
        for col in pfn:
            if col not in fni:
                UNSEEN.append(col)

        if len(UNSEEN) > 10:
            addon += (f"\n{len(UNSEEN)} new columns that were not seen "
                      f"during the first fit.")
        elif len(UNSEEN) > 0:
            addon += f"\nFeature names unseen at fit time:"
            for col in UNSEEN:
                addon += f"\n- {col}"
        del UNSEEN

        SEEN = []
        for col in fni:
            if col not in pfn:
                SEEN.append(col)
        if len(SEEN) > 10:
            addon += (f"\n{len(SEEN)} original columns not seen during "
                      f"this fit.")
        elif len(SEEN) > 0:
            addon += f"\nFeature names seen at fit time, yet now missing:"
            for col in SEEN:
                addon += f"\n- {col}"
        del SEEN


    raise ValueError(base_err_msg + addon)







