# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Sequence
)
from .._type_aliases import XContainer

import numbers
import re

from ._ngrams import _val_ngrams
from ._ngcallable import _val_ngcallable

from ...__shared._validation._2D_X import _val_2D_X
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer
from ...__shared._validation._any_string import _val_any_string



def _validation(
    _X: XContainer,
    _ngrams: Sequence[Sequence[str | re.Pattern[str]] | None],
    _ngcallable: Callable[[list[str]], str] | None,
    _sep: str | None,
    _wrap: bool,
    _case_sensitive: bool,
    _remove_empty_rows: bool,
    _flags: int | None
) -> None:
    """Centralized hub for validation.

    See the individual modules for more details.

    Also blocks `ngcallable`, `sep`, and `flags` when `ngrams` is None.

    Parameters
    ----------
    _X : XContainer
        (possibly ragged) 2D array of strings.
    _ngrams : Sequence[Sequence[str | re.Pattern[str]]] | None
        A sequence of sequences, where each inner sequence holds a series
        of string literals and/or re.compile objects that specify an
        n-gram. Cannot be empty, and cannot have any n-grams with less
        than 2 entries. Can be None.
    _ngcallable : Callable[[list[str]], str] | None
        The callable applied to ngram sequences to produce a contiguous
        string sequence.
    _sep : str | None
        The separator that joins words in the n-grams.
    _wrap : bool
        Whether to look for pattern matches across the end of the current
        line and beginning of the next line.
    _case_sensitive : bool
        Whether to do a case-sensitive search.
    _remove_empty_rows : bool
        Whether to delete any empty rows that may occur during the
        merging process. A row could only become empty if `_wrap` is True.
    _flags : int | None
        The global flags value(s) applied to the n-gram search. Must be
        None or an integer. The values of the integers are not validated
        for legitimacy, any exceptions would be raised by re.fullmatch.

    Returns
    -------
    None

    """


    _val_2D_X(_X, _require_all_finite=False)

    _val_ngrams(_ngrams)

    _val_ngcallable(_ngcallable)

    _val_any_string(_sep, 'sep', _can_be_None=True)

    _val_any_bool(_wrap, 'wrap', _can_be_None=False)

    _val_any_bool(_case_sensitive, 'case_sensitive', _can_be_None=False)

    _val_any_bool(_remove_empty_rows, 'remove_empty_rows', _can_be_None=False)

    _val_any_integer(_flags, 'flags', _can_be_None=True)
    if not isinstance(_flags, (type(None), numbers.Integral)):
        raise TypeError(
            f"'flags' must be None or an integer. Cannot be a sequence."
        )

    if _ngrams is None:

        if _ngcallable is not None:
            raise ValueError(
                f"cannot pass 'ngcallable' when 'ngrams' is not passed."
            )

        if _sep is not None:
            raise ValueError(
                f"cannot pass 'sep' when 'ngrams' is not passed."
            )

        if _flags is not None:
            raise ValueError(
                f"cannot pass 'flags' when 'ngrams' is not passed."
            )



