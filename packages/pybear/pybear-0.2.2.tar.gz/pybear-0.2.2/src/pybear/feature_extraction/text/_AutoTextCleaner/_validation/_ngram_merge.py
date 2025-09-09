# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import NGramsType

# this is directly from NGramMerger
from ..._NGramMerger._validation._ngrams import _val_ngrams



def _val_ngram_merge(
    _ngram_merge: NGramsType | None
) -> None:
    """Validate ngram_merge.

    Can be None. Otherwise, a dictionary keyed with 'ngrams' and 'wrap'.
    'ngrams' is a sequence holding series of string literals and/or
    re.compile objects that specify an n-gram. 'wrap' is a boolean
    indicating whether to look for ngrams across the beginnings and ends
    of adjacent lines.

    Parameters
    ----------
    _ngram_merge : NGramsType | None
        Can be None. A dictionary keyed with 'ngrams' and  'wrap'.
        'ngrams' is a sequence of sequences, where each inner sequence
        holds a series of string literals and/or re.compile objects that
        specify an n-gram. Cannot be empty, and cannot have any n-grams
        with less than 2 entries. 'wrap' must be boolean.

    Returns
    -------
    None

    """


    if _ngram_merge is None:
        return

    err_msg = (f"'If 'ngram_merge' is passed, it must be a dictionary "
               f"keyed with 'ngrams' and 'wrap'. \n'ngrams' must be a "
               f"sequence of ngrams. see the NGramMerger docs. \n'wrap' "
               f"must be boolean.")

    if not isinstance(_ngram_merge, dict):
        _val_ngrams(_ngram_merge)

    if len(_ngram_merge) != 2:
        raise ValueError(err_msg)

    if 'ngrams' not in _ngram_merge:
        raise ValueError(err_msg)

    _val_ngrams(_ngram_merge['ngrams'])

    if 'wrap' not in _ngram_merge:
        raise ValueError(err_msg)

    if not isinstance(_ngram_merge['wrap'], bool):
        raise TypeError(err_msg)






