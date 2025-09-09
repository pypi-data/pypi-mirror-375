# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



class NotFittedError(ValueError, AttributeError):
    """Exception class to raise if estimator is used before fitting.

    This class inherits from both ValueError and AttributeError to help
    with exception handling.

    Examples
    --------
    >>> from pybear.preprocessing import ColumnDeduplicator as CDT
    >>> from pybear.base.exceptions import NotFittedError
    >>> import numpy as np
    >>> X = np.random.randint(0, 10, (5,3))
    >>> try:
    ...     CDT().transform(X)
    ... except NotFittedError as e:
    ...     print(e)  # doctest:+SKIP
    This ColumnDeduplicator instance is not fitted yet.
    Call 'fit' with appropriate arguments before using this estimator.

    """

