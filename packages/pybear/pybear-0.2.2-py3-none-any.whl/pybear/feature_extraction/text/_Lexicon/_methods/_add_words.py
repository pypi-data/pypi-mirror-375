# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)

import os

import numpy as np

from ._validate_word_input import _validate_word_input
from ._identify_sublexicon import _identify_sublexicon


# MODULE FOR APPENDING NEW WORDS TO A SUB-LEXICON


def _add_words(
    WORDS:str | Sequence[str],
    lexicon_folder_path:str,
    character_validation:bool = True,
    majuscule_validation:bool = True,
    file_validation:bool = True
) -> None:
    """Silently update the pybear lexicon text files with the given words.

    Words that are already in the lexicon are silently ignored. This is
    very much a case-sensitive operation.

    The 'validation' parameters allow you to disable the pybear lexicon
    rules. The pybear lexicon does not allow any characters that are
    not one of the 26 letters of the English alphabet. Numbers, spaces,
    and punctuation, for example, are not allowed in the formal pybear
    lexicon. Also, the pybear lexicon requires that all entries in the
    lexicon be MAJUSCULE, i.e., upper-case. The published pybear
    lexicon will always follow these rules. When the validation is
    used it ensures the integrity of the lexicon. However, the user can
    override this validation for local copies of pybear by setting
    `character_validation`, `majuscule_validation`, and / or
    `file_validation` to False. If you want your lexicon to have strings
    that contain numbers, spaces, punctuation, and have different cases,
    then set the validation to False and add your strings to the lexicon
    via this method.

    pybear stores words in the lexicon text files based on the first
    character of the string. So a word like 'APPLE' is stored in a
    file named 'lexicon_A' (this is the default pybear way.) A word
    like 'apple' would be stored in a file named 'lexicon_a'. Keep in
    mind that the pybear lexicon is built with all capitalized words
    and file names and these are the only ones that exist out of the
    box. If you were to turn off the `majuscule_validation` and
    `file_validation` and pass the word 'apple' to this method, it
    will NOT append 'APPLE' to the 'lexicon_A' file, a new lexicon
    file called 'lexicon_a' will be created and the word 'apple' will
    be put into it.

    The Lexicon instance reloads the lexicon from disk and refills
    the attributes when update is complete.

    Parameters
    ----------
    WORDS : str | Sequence[str] - the word or words to be added to the
        pybear lexicon. Cannot be an empty string or an empty sequence.
        Words that are already in the lexicon are silently ignored.
    lexicon_folder_path : str - the path to the directory that holds
        the lexicon text files.
    character_validation : bool, default = True
        Whether to apply pybear lexicon character validation to the word
        or sequence of words. pybear lexicon allows only the 26 letters
        in the English language, no others. No spaces, no hyphens, no
        apostrophes. If True, any non-alpha characters will raise an
        exception during validation. If False, any string character is
        accepted.
    majuscule_validation : bool, default = True
        Whether to apply pybear lexicon majuscule validation to the word
        or sequence of words. The pybear lexicon requires all characters
        be majuscule, i.e., EVERYTHING MUST BE UPPER-CASE. If True,
        any non-majuscule characters will raise an exception during
        validation. If False, any case is accepted.
    file_validation : bool, default = True
        Whether to apply pybear lexicon file name validation to the
        word or sequence of words. The formal pybear lexicon only allows
        words to start with the 26 upper-case letters of the English
        alphabet (which then dictates the file name in which it will
        be stored). If True, any disallowed characters in the first
        position will raise an exception during validation. If False,
        any character is accepted, which may then necessitate that a
        file be created.

    Returns
    -------
    None

    """


    if not isinstance(lexicon_folder_path, str):
        raise TypeError(f"'lexicon_folder_path' must be a string")

    if not isinstance(character_validation, bool):
        raise TypeError(f"'character_validation' must be boolean")

    if not isinstance(majuscule_validation, bool):
        raise TypeError(f"'majuscule_validation' must be boolean")

    if not isinstance(file_validation, bool):
        raise TypeError(f"'file_validation' must be boolean")

    _validate_word_input(
        WORDS,
        character_validation=character_validation,
        majuscule_validation=majuscule_validation
    )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    file_base = f'lexicon_'

    file_identifiers: list[str] = \
        _identify_sublexicon(
            WORDS,
            file_validation=file_validation
        )


    if isinstance(WORDS, str):
        _WORDS = [WORDS]
    else:
        _WORDS = WORDS

    for file_letter in file_identifiers:

        full_path = os.path.join(
            lexicon_folder_path,
            file_base + file_letter + '.txt'
        )

        try:
            # this will except because of 'r' if file doesnt exist
            with open(full_path, 'r') as f:
                raw_text = np.fromiter(f, dtype='<U40')
        except:
            # if we are creating a file because of a non-alpha character,
            # that would have been caught by _identify_sublexicon if
            # file_validation is on. so if we are at this point, just
            # create file without worry.
            raw_text = []
            with open(full_path, 'w') as f:
                # just create and dont put anything in it, let it go thru
                # the shared process below.
                f.close()

        if len(raw_text) == 0:
            OLD_SUB_LEXICON = []
        else:
            # this will except if raw_text is empty
            OLD_SUB_LEXICON = np.char.replace(raw_text, f'\n', f'')

        del raw_text

        PERTINENT_WORDS = [w for w in _WORDS if w[0] == file_letter]

        NEW_LEXICON = np.hstack((OLD_SUB_LEXICON, PERTINENT_WORDS))

        del OLD_SUB_LEXICON, PERTINENT_WORDS

        # MUST USE uniques TO TAKE OUT ANY NEW WORDS ALREADY IN LEXICON (AND SORT)
        NEW_LEXICON = np.unique(NEW_LEXICON)

        with open(full_path, 'w') as f:
            for line in NEW_LEXICON:
                f.write(line+f'\n')
            f.close()

        del full_path
        del NEW_LEXICON

    del _WORDS, file_base, file_identifiers


    print(f'\n*** Lexicon update successful. ***\n')





