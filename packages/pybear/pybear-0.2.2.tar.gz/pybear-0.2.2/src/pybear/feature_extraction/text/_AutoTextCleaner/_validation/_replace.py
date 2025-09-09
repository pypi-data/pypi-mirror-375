# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import ReplaceType

import re

# this is directly from _TextReplacer
from ..._TextReplacer._validation._replace import _val_replace as _TR_val_replace



def _val_replace(
    _replace: ReplaceType
) -> None:
    """Validate the 'replace' argument.

    Parameters
    ----------
    _replace : ReplaceType
        None, a find/replace pair, or a tuple of find/replace pairs.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    ReplaceType:
        None | PairType | tuple[PairType, ...]

    """


    # TR _replace allows lists. we just want the None/str/re.Pattern/tuple
    # part. so block anything else

    if not isinstance(_replace, (type(None), str, re.Pattern, tuple)):
        raise TypeError(
            f"'replace' must be None, a find/replace pair, or a tuple of "
            f"find/replace pairs."
        )


    _TR_val_replace(_replace, 1)






