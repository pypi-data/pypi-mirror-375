# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    NGramsType,
    NGramsWipType
)

from ...__shared._param_conditioner._param_conditioner import _param_conditioner



def _special_param_conditioner(
    _ngrams: NGramsType,
    _case_sensitive: bool,
    _flags: int | None
) -> NGramsWipType:
    """Convert any literal strings in the ngrams to re.compile objects.

    Apply any flags from 'case_sensitive' and 'flags' to all the compile
    objects, including those ngram patterns that may have already been
    passed as re.compile.

    Parameters
    ----------
    _ngrams : Sequence[Sequence[str | re.Pattern[str]]] | None
        A sequence of sequences, where each inner sequence holds a series
        of string literals and/or re.compile objects that specify an
        n-gram. Cannot be empty, and cannot have any n-grams with less
        than 2 entries. Can be None.
    _case_sensitive : bool
        Whether to do a case-sensitive search.
    _flags : int | None
        The global flags value(s) applied to the n-gram search. Must be
        None or an integer.

    Returns
    -------
    _wip_ngrams : list[tuple[re.Pattern[str], ...]] | None
        The ngrams with any literal strings converted to re.compile and
        any flags from 'case_sensitive' and 'flags' applied to the
        compile objects.

    """


    # we know from validation
    # --- 'ngrams' must be None or a 1D sequence of sequences of
    # string literals and/or re.compile objects. cannot be
    # empty, and cannot contain any n-gram sequences with
    # less than 2 entries.
    # --- 'case_sensitive' must be bool
    # --- 'flags' must be int | None



    # _param_conditioner wants to see list[tuple[str | re.Pattern], ...]
    if _ngrams is not None:
        _ngrams = list(map(tuple, _ngrams))


    _wip_ngrams = _param_conditioner(
        _ngrams,
        _case_sensitive,
        _flags,
        _order_matters=True,
        # need to rig _n_rows to fool it, ngrams could be None
        _n_rows=len(_ngrams or []),
        _name='ngrams'
    )

    if _wip_ngrams is not None:

        # when there is only one tuple in 'ngrams', _param_conditioner
        # is condensing that to return just the single tuple (as it should.)
        # so re-establish the outer list
        if isinstance(_wip_ngrams, tuple):
            _wip_ngrams = [_wip_ngrams]

        assert isinstance(_wip_ngrams, list)
        assert all(map(isinstance, _wip_ngrams, (tuple for _ in _wip_ngrams)))


    return _wip_ngrams




