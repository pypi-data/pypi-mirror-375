# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import numpy as np

from ._delete_always import _val_delete_always
from ._replace_always import _val_replace_always
from ._skip_always import _val_skip_always
from ._split_always import _val_split_always

from ....__shared._validation._2D_X import _val_2D_X
from ....__shared._validation._any_bool import _val_any_bool



def _validation(
    _X,
    _update_lexicon: bool,
    _skip_numbers: bool,
    _auto_split: bool,
    _auto_add_to_lexicon: bool,
    _auto_delete: bool,
    _DELETE_ALWAYS: Sequence[str],
    _REPLACE_ALWAYS:dict[str, str],
    _SKIP_ALWAYS: Sequence[str],
    _SPLIT_ALWAYS: dict[str, Sequence[str]],
    _remove_empty_rows: bool,
    _verbose: bool
) -> None:
    """Validate `TextLookup` parameters.

    This is a centralized hub for validation. The brunt of the validation
    is handled by the individual modules. See their docs for more
    details.

    Manage the interdependency of parameters.

    `SKIP_ALWAYS`, `SPLIT_ALWAYS`, `DELETE_ALWAYS`, `REPLACE_ALWAYS`
    must not have common strings (case_sensitive).

    Parameters
    ----------
    _X: XContainer
        _update_lexicon : bool
        _skip_numbers : bool
        _auto_split : bool
        _auto_add_to_lexicon : bool
        _auto_delete : bool
        _DELETE_ALWAYS : Sequence[str]
        _REPLACE_ALWAYS :dict[str, str]
        _SKIP_ALWAYS : Sequence[str]
        _SPLIT_ALWAYS : dict[str, Sequence[str]]
        _remove_empty_rows : bool
        _verbose : bool


    Returns
    -------
    None


    """


    _val_2D_X(_X, _require_all_finite=False)

    _val_any_bool(_update_lexicon, 'update_lexicon')

    _val_any_bool(_skip_numbers, 'skip_numbers')

    _val_any_bool(_auto_split, 'auto_split')

    _val_any_bool(_auto_add_to_lexicon, 'auto_add_to_lexicon')

    _val_any_bool(_auto_delete, 'auto_delete')

    _val_delete_always(_DELETE_ALWAYS)

    _val_any_bool(_remove_empty_rows, 'remove_empty_rows')

    _val_replace_always(_REPLACE_ALWAYS)

    _val_skip_always(_SKIP_ALWAYS)

    _val_split_always(_SPLIT_ALWAYS)

    _val_any_bool(_verbose, 'verbose')


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



    if _auto_add_to_lexicon and not _update_lexicon:
        raise ValueError(
            f"'auto_add_to_lexicon' cannot be True if 'update_lexicon' is False"
        )

    if _update_lexicon and _auto_delete:
        raise ValueError(
            f"'update_lexicon' and 'auto_delete' cannot be True simultaneously"
        )



    # SKIP_ALWAYS, SPLIT_ALWAYS, DELETE_ALWAYS, REPLACE_ALWAYS must not
    # have common strings (case_sensitive).

    # DELETE_ALWAYS: Sequence[str] | None = None
    # REPLACE_ALWAYS: dict[str, str] | None = None
    # SKIP_ALWAYS: Sequence[str] | None = None
    # SPLIT_ALWAYS: dict[str, Sequence[str]] | None = None

    delete_always = list(_DELETE_ALWAYS) if _DELETE_ALWAYS else []
    replace_always_keys = list(_REPLACE_ALWAYS.keys()) if _REPLACE_ALWAYS else []
    skip_always = list(_SKIP_ALWAYS) if _SKIP_ALWAYS else []
    split_always_keys = list(_SPLIT_ALWAYS.keys()) if _SPLIT_ALWAYS else []

    ALL = np.hstack((
        delete_always,
        replace_always_keys,
        skip_always,
        split_always_keys
    )).tolist()

    if not np.array_equal(sorted(list(set(ALL))), sorted(ALL)):

        _ = np.unique(ALL, return_counts=True)
        __ = list(map(str, [k for k, v in zip(*_) if v >= 2]))

        raise ValueError(
            f"{', '.join(__)} appear more than once in the specially handled words."
        )


    del ALL




