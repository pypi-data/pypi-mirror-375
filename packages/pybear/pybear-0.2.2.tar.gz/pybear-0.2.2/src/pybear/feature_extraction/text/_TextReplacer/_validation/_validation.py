# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    XContainer,
    ReplaceType,
    CaseSensitiveType,
    FlagsType
)

from pybear.feature_extraction.text._TextReplacer._validation._replace import \
    _val_replace

from ...__shared._validation._1D_2D_X import _val_1D_2D_X
from ...__shared._validation._case_sensitive import _val_case_sensitive
from ...__shared._validation._flags import _val_flags



def _validation(
    _X: XContainer,
    _replace: ReplaceType,
    _case_sensitive: CaseSensitiveType,
    _flags: FlagsType
) -> None:
    """Centralized hub for validation.

    See the individual validation modules for more details.

    Parameters
    ----------
    _X : XContainer
        The data.
    _replace : ReplaceType
        The criteria for search and replacement.
    _case_sensitive : CaseSensitiveType
        Whether the search is case-sensitive.
    _flags : FlagsType
        The flags for the search.

    Returns
    -------
    None

    """


    _val_1D_2D_X(_X, _require_all_finite=False)


    _n_rows = _X.shape[0] if hasattr(_X, 'shape') else len(_X)

    _val_replace(_replace, _n_rows)

    _val_case_sensitive(_case_sensitive, _n_rows)

    _val_flags(_flags, _n_rows)

    del _n_rows







