# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)

import numbers


CaseSensitiveType: TypeAlias = bool | list[bool | None]



def _val_case_sensitive(
    _case_sensitive: CaseSensitiveType,
    _n_rows: int
) -> None:
    """Validate 'case_sensitive'.

    Must be boolean or a list-like of booleans and/or Nones. If list-like,
    the number of entries must equal the number of rows in the data.

    Parameters
    ----------
    _case_sensitive : bool | list[bool | None]
        Whether to do a case-sensitive search. If a list-like, the
        entries are applied to the corresponding row in the data.
    _n_rows : int
        The number of rows in the data.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    CaseSensitiveType:
        bool | list[bool | None]

    """


    assert isinstance(_n_rows, numbers.Integral)
    assert not isinstance(_n_rows, bool)
    assert _n_rows >= 0


    _err_msg = ("'case_sensitive' must be boolean or a list-like of "
        "booleans and/or Nones. \nwhen passed as a list-like, the number "
        "of entries must equal the number of rows in the data.")


    try:
        if isinstance(_case_sensitive, bool):
            raise UnicodeError
        if not isinstance(_case_sensitive, list):
            raise Exception
        if not all(map(
            isinstance,
            _case_sensitive,
            ((bool, type(None)) for _ in _case_sensitive)
        )):
            raise Exception
        if len(_case_sensitive) != _n_rows:
            raise TimeoutError
    except UnicodeError:
        pass
    except TimeoutError:
        raise ValueError(_err_msg)
    except Exception as e:
        raise TypeError(_err_msg)







