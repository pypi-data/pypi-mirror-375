# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import RemoveType

import re

from ...__shared._validation._pattern_holder import _val_pattern_holder



def _val_remove(
    _remove: RemoveType
) -> None:
    """Validate '_remove'.

    Must be:
    None,
    a literal string,
    a regex pattern in a re.compile object,
    OR
    a tuple of literal strings and/or regex patterns in re.compile objects.

    Regex patterns are not validated here, any exception would be raised
    by the re method/function they are being passed to.

    Parameters
    ----------
    _remove : RemoveType
        The literal strings or re.compile objects used to match patterns
        in the data. When None, no matches are sought. If a single
        literal or re.compile object, that is searched on the entire
        dataset. If a tuple of string literals and/or re.compile objects,
        then each of them is searched on the entire dataset.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    RemoveType:
        None | FindType | tuple[FindType, ...]

    """


    # _val_pattern_holder allows lists. we just want the None/str/re.Pattern/tuple
    # part. so block anything else

    if not isinstance(_remove, (type(None), str, re.Pattern, tuple)):
        raise TypeError(
            f"'remove' must be None, a literal string, a re.compile object, "
            f"or a tuple of literal strings and/or re.compile objects."
        )


    _val_pattern_holder(_remove, 1, _name='remove')



