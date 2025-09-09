# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    XContainer,
    ReturnDimType,
    ReplaceType,
    RemoveType,
    LexiconLookupType,
    NGramsType,
    GetStatisticsType
)

import numbers

from ...__shared._validation._1D_2D_X import _val_1D_2D_X
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer
from ...__shared._validation._any_string import _val_any_string


from ._get_statistics import _val_get_statistics
from ._remove import _val_remove
from ._replace import _val_replace
from ._lexicon_lookup import _val_lexicon_lookup
from ._return_dim import _val_return_dim
from ._ngram_merge import _val_ngram_merge



def _validation(
    _X: XContainer,
    _global_sep: str,
    _case_sensitive: bool,
    _global_flags: int | None,
    _remove_empty_rows: bool,
    _return_dim: ReturnDimType,
    _strip: bool,
    _replace: ReplaceType,
    _remove: RemoveType,
    _normalize: bool | None,
    _lexicon_lookup: LexiconLookupType | None,
    _remove_stops: bool,
    _ngram_merge: NGramsType | None,
    _justify: int | None,
    _get_statistics: GetStatisticsType | None
) -> None:
    """Validate the parameters for AutoTextCleaner.

    The brunt of the validation is handled by the submodules. See them
    for more information. This is a centralized hub for all the
    submodules.

    Parameters
    ----------
    _X:
        XContainer
    _global_sep:
        str
    _case_sensitive:
        bool
    _global_flags:
        int | None
    _remove_empty_rows:
        bool
    _return_dim:
        ReturnDimType
    _strip:
        bool
    _replace:
        ReplaceType
    _remove:
        RemoveType
    _normalize:
        bool | None
    _lexicon_lookup:
        LexiconLookupType | None
    _remove_stops:
        bool
    _ngram_merge:
        NGramsType | None
    _justify:
        int | None
    _get_statistics:
        GetStatisticsType | None

    Returns
    -------
    None

    """


    _val_1D_2D_X(_X, _require_all_finite=False)

    _val_any_string(_global_sep, 'global_sep', _can_be_None=False)

    _val_any_bool(_case_sensitive, 'case_sensitive', _can_be_None=False)

    _val_any_integer(_global_flags, 'global_flags', _can_be_None=True)

    _val_any_bool(_remove_empty_rows, 'remove_empty_rows', _can_be_None=False)

    _val_return_dim(_return_dim)

    # ############

    _val_any_bool(_strip, 'strip', _can_be_None=False)

    _val_replace(_replace)

    _val_remove(_remove)

    _val_any_bool(_normalize, 'normalize', _can_be_None=True)

    _val_lexicon_lookup(_lexicon_lookup)

    _val_any_bool(_remove_stops, 'remove_stops', _can_be_None=False)

    _val_ngram_merge(_ngram_merge)

    _val_any_integer(_justify, 'justify', _can_be_None=True)

    _val_get_statistics(_get_statistics)







