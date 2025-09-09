# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import re



def _val_ngrams(
    _ngrams: Sequence[Sequence[str | re.Pattern[str]]] | None
) -> None:
    """Validate ngrams.

    The series of string literals and/or re.compile objects that specify
    an n-gram. Can be None.

    Parameters
    ----------
    _ngrams : Sequence[Sequence[str | re.Pattern[str]]] | None
        A sequence of sequences, where each inner sequence holds a series
        of string literals and/or re.compile objects that specify an
        n-gram. Cannot be empty, and cannot have any n-grams with less
        than 2 entries. Can be None.

    Returns
    -------
    None

    """


    err_msg = (f"'ngrams' must be None or a sequence of sequences of "
               f"string literals and/or re.compile objects. \nE.g. "
               f"(('one', 'two'), ('three', 'four')). \ncannot be "
               f"empty, and cannot contain any n-gram sequences with "
               f"less than 2 entries.")


    if _ngrams is None:
        return


    # this validates that the outer container is 1D iterable
    try:
        iter(_ngrams)
        if isinstance(_ngrams, (str, dict)):
            raise Exception
        if len(_ngrams) == 0:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    # this validates the contents of the outer iterable
    for _inner in _ngrams:

        try:
            iter(_inner)
            if isinstance(_inner, (str, dict)):
                raise Exception
            if len(_inner) < 2:
                raise UnicodeError
            if not all(map(
                isinstance,
                _inner,
                ((str, re.Pattern) for _ in _inner)
            )):
                raise Exception
        except UnicodeError:
            raise ValueError(err_msg)
        except Exception as e:
            raise TypeError(err_msg)








