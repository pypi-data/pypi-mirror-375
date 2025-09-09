# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import string

import numpy as np

from ._validate_word_input import _validate_word_input



def _identify_sublexicon(
    WORDS:str | Sequence[str],
    file_validation:bool = True
) -> list[str]:
    """Identify the files that need to be accessed to make changes to
    the pybear lexicon.

    These should be found by the first letter of the word(s) in WORDS.

    Parameters
    ----------
    WORDS : str | Sequence[str]
        The word or sequence of words passed to a pybear Lexicon method.
    file_validation : bool, default = True
        Whether to block first characters that are not allowed in the
        formal pybear lexicon. I.e., only allow ABCDEF..... etc.

    """


    if not isinstance(file_validation, bool):
        raise TypeError(f"'file_validation' must be boolean")

    _validate_word_input(
        WORDS,
        character_validation=False,
        majuscule_validation=False
    )


    if isinstance(WORDS, str):
        _WORDS = [WORDS]
    else:
        _WORDS = WORDS


    _unq_first_chars = np.unique(list(map(lambda x: x[0], _WORDS)))

    _unq_first_chars = sorted(list(map(str, _unq_first_chars)))

    if file_validation:

        for _char in _unq_first_chars:

            if _char not in string.ascii_letters:
                raise ValueError(
                    f"when looking for sub-lexicons to update, all first "
                    f"characters of words must be one of the 26 letters in "
                    f"the English alphabet. Got {_char}."
                )


    return _unq_first_chars




