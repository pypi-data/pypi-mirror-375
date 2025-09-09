# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XContainer



def _partial_fit(
    _X: XContainer
) -> int:
    """Get the number of features in `X`.

    Parameters
    ----------
    X : XContainer
        The data.

    Returns
    -------
    n_features : int
        The number of features in `X`.

    """


    if hasattr(_X, 'shape'):
        return _X.shape[1]
    else:
        return max(map(len, _X))







