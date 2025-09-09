# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ._type_aliases import (
    XContainer,
    SepsType,
    CaseSensitiveType,
    MaxSplitsType,
    FlagsType
)

import numbers

from ..__shared._validation._1D_X import _val_1D_X
from ..__shared._validation._any_integer import _val_any_integer
from ..__shared._validation._pattern_holder import _val_pattern_holder
from ..__shared._validation._case_sensitive import _val_case_sensitive
from ..__shared._validation._flags import _val_flags



def _validation(
    _X: XContainer,
    _sep: SepsType,
    _case_sensitive: CaseSensitiveType,
    _maxsplit: MaxSplitsType,
    _flags: FlagsType
) -> None:
    """Centralized hub for validation.

    See the individual modules for more details.

    Beyond the individual modules' validation, this module also checks:
        1) cannot pass anything to `maxsplit` if `sep` is None
        2) cannot pass anything to `flags` if `sep` is None
        3) cannot pass a list to `case_sensitive` if `sep` is None

    Parameters
    ----------
    _X : XContainer
        The data, a 1D vector of strings.
    _sep : SepsType
        The literal string(s) and/or the re.compile object(s) to split
        with.
    _case_sensitive : CaseSensitiveType
        Whether the search for separators is case-sensitive.
    _maxsplit : MaxSplitType
        The maximum number of splits to perform working left to right.
    _flags : FlagsType
        The flag value(s) to be applied to the search for separators.

    Returns
    -------
    None
     
    """


    _val_1D_X(_X, _require_all_finite=False)

    _n_rows = _X.shape[0] if hasattr(_X, 'shape') else len(_X)

    _val_pattern_holder(_sep, _n_rows, 'sep')

    _val_case_sensitive(_case_sensitive, _n_rows)

    # maxsplit -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    err_msg = (f"'maxsplit' must be None, a single integer, or a LIST of "
        f"Nones and/or integers, whose length equals the number of strings "
        f"in the data.")
    _val_any_integer(_maxsplit, _name='maxsplit', _can_be_None=True)
    if isinstance(_maxsplit, (type(None), numbers.Integral)):
        pass
    elif isinstance(_maxsplit, list):
        if len(_maxsplit) != _n_rows:
            raise ValueError(err_msg)
    else:
        raise TypeError(err_msg)
    # END maxsplit -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _val_flags(_flags, _n_rows)

    del _n_rows

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    #########
    if _sep is None and isinstance(_case_sensitive, list):
        raise ValueError(
            f"cannot pass 'case_sensitive' as a list if 'sep' is not "
            f"passed."
        )

    #########
    if _sep is None and _maxsplit is not None:
        raise ValueError(f"cannot pass 'maxsplit' if 'sep' is not passed.")

    #########
    if _sep is None and _flags is not None:
        raise ValueError(f"cannot pass 'flags' if 'sep' is not passed.")










