# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XContainer

from ...__shared._validation._1D_2D_X import _val_1D_2D_X
from ...__shared._validation._any_bool import _val_any_bool



def _validation(
    _X: XContainer,
    _store_uniques: bool
) -> None:
    """Centralized hub for validation.

    See the individual modules for more details.

    Parameters
    ----------
    _X : XContainer
        The text data. Must be a 1D list-like or 2D array-like of strings.
    _store_uniques : bool
        If True, all attributes and print methods are fully informative.
        If False, the `string_frequencies_` and `uniques_` attributes
        are always empty, and functionality that depends on these
        attributes have reduced capability.

    Returns
    -------
    None

    """


    # leave raf False, TextStatistics needs to take anything
    _val_1D_2D_X(_X, _require_all_finite=False)

    _val_any_bool(_store_uniques, 'store_uniques')






