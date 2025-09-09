# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence
)

import string

import numpy as np



def _validate_word_input(
    WORDS:str | Sequence[str],
    character_validation:bool = True,
    majuscule_validation:bool = True
) -> None:
    """Validate the `WORDS` parameter passed to pybear Lexicon methods.

    `WORDS` must be a string or a 1D sequence of strings. Read about
    `character_validation` and `majuscule_validation` in the Parameters
    section.

    Parameters
    ----------
    WORDS : str | Sequence[str]
        The word or sequence of words to append to the pybear lexicon.
    character_validation : bool, default = True
        Whether to apply pybear lexicon character validation to the word
        or sequence of words. pybear lexicon allows only the 26 letters
        in the English language, no others. No spaces, no hypens, no
        apostrophes. If True, any non-alpha characters will raise an
        exception during validation. If False, any string character is
        accepted.
    majuscule_validation : bool, default = True
        Whether to apply pybear lexicon majuscule validation to the word
        or sequence of words. The pybear lexicon requires all characters
        be majuscule, i.e., EVERYTHING MUST BE UPPER-CASE. If True,
        any non-majuscule characters will raise an exception during
        validation. If False, any case is accepted.

    Returns
    -------
    None

    """


    if not isinstance(character_validation, bool):
        raise TypeError(f"'character_validation' must be boolean")

    if not isinstance(majuscule_validation, bool):
        raise TypeError(f"'majuscule_validation' must be boolean")


    err_msg = (f"'WORDS' must a string or a 1D sequence of strings. "
               f"a 1D sequence cannot be empty.")

    try:
        iter(WORDS)
        if isinstance(WORDS, dict):
            raise Exception
        if isinstance(WORDS, str):
            raise UnicodeError
        if len(np.array(list(WORDS)).shape) != 1:
            raise Exception
        if not all(map(isinstance, WORDS, (str for _ in WORDS))):
            raise Exception
        if len(WORDS) == 0:
            raise Exception
    except UnicodeError:
        if len(WORDS) == 0:
            raise TypeError(err_msg)
    except:
        raise TypeError(err_msg)


    if character_validation or majuscule_validation:

        if isinstance(WORDS, str):
            _WORDS = [WORDS]
        else:
            _WORDS = WORDS


    if character_validation:

        for _word in _WORDS:
            for _char in _word:

                if _char not in string.ascii_letters:
                    raise ValueError(
                        f"when 'character_validation' is True, only the "
                        f"26 characters of the English alphabet are "
                        f"allowed. Got '{_char}' in '{_word}'."
                    )

    if majuscule_validation:

        for _word in _WORDS:
            for _char in _word:

                if _char.upper() != _char:
                    raise ValueError(
                        f"when 'majuscule_validation' is True, all "
                        f"characters must be equal to the python "
                        f"str.upper() version of themselves. Got '{_char}' "
                        f"in '{_word}'."
                    )






