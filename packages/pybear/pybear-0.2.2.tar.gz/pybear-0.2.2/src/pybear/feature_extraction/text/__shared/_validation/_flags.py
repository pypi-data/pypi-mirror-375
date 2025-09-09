# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)

import numbers

from ._any_integer import _val_any_integer



FlagType: TypeAlias = int | None



def _val_flags(
    _flags: FlagType | list[FlagType],
    _n_rows: int
) -> None:
    """Validate the 'flags' parameter.

    Must be integer, None, or list of integer / None. If a list, the
    length must match the number of rows in X.

    Parameters
    ----------
    _flags : FlagType | list[FlagType]
        The flags argument for re methods/functions when re.Pattern
        objects are being used (either globally on all the data or a row
        of the data.) Must be None or an integer, or a list of Nones
        and/or integers. When passed as a list, the length must match
        the number of rows in the data. The values of the integers are
        not validated for legitimacy, any exceptions would be raised by
        the re method it is passed to.
    _n_rows : int
        The number of rows in the data.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    FlagType:
        int | None

    """


    assert isinstance(_n_rows, numbers.Integral)
    assert not isinstance(_n_rows, bool)
    assert _n_rows >= 0

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _err_msg = (
        f"'flags' must be None, an integer, or a LIST that contains any "
        f"combination of Nones and/or integers whose length matches the "
        f"number of rows in the data."
    )

    if isinstance(_flags, (type(None), numbers.Integral)) \
            and not isinstance(_flags, bool):
        return

    if not isinstance(_flags, list):
        raise TypeError(_err_msg)

    if len(_flags) != _n_rows:
        raise ValueError(_err_msg)

    _val_any_integer(
        _flags, _name='flags', _can_be_bool=False, _can_be_None=True
    )

    del _err_msg




