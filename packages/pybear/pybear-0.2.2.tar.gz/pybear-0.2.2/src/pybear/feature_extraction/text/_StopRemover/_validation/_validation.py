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

from ._match_callable import _val_match_callable

from ._exempt import _val_exempt

from ._supplemental import _val_supplemental

from ...__shared._validation._2D_X import _val_2D_X
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer



def _validation(
    _X: XContainer,
    _match_callable: Callable[[str, str], bool] | None,
    _remove_empty_rows: bool,
    _exempt: Sequence[str] | None,
    _supplemental: Sequence[str] | None,
    _n_jobs: int | None
) -> None:
    """Centralized hub for validating parameters for `StopRemover`.

    The brunt of validation is handled by the individual validation
    modules. See the individual modules for more details.

    Parameters
    ----------
    _X : XContainer
        The data from which to remove stop words.
    _match_callable : Callable[[str, str], bool] | None
        None to use the default `StopRemover` matching criteria, or a
        custom callable that defines what constitutes matches of words
        in the text against the stop words.
    _remove_empty_rows : bool
        Whether to remove any empty rows that may be left after the stop
        word removal process.
    _exempt : Sequence[str] | None
        Stop words that are exempted from the search. text that matches
        these words will not be removed.
    _supplemental : Sequence[str] | None
        Words to be removed in addition to the stop words.
    _n_jobs : int | None, default = -1
        The number of cores/threads to use when parallelizing the
        search for stop words in the rows of `X`. The default is to
        use processes but can be set by running `StopRemover` under a
        joblib parallel_config context manager. -1 uses all available
        cores/threads. None uses joblib's default number of cores/threads.

    Returns
    -------
    None

    """


    _val_2D_X(_X, _require_all_finite=False)

    _val_match_callable(_match_callable)

    _val_any_bool(_remove_empty_rows, 'remove_empty_rows')

    _val_exempt(_exempt)

    _val_supplemental(_supplemental)

    _val_any_integer(
        _n_jobs, 'n_jobs', _min=-1, _disallowed=[0], _can_be_None=True
    )







