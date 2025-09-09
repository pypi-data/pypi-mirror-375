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



def _delete_words(
    WORDS: str | Sequence[str],
    lexicon_folder_path: str
) -> None:
    """Remove the given word(s) from the pybear lexicon text files.
    Case sensitive! Any words that are not in the pybear lexicon are
    silently ignored.

    Parameters
    ----------
    WORDS : str | Sequence[str]
        The word or words to remove from the pybear lexicon. Cannot be
        an empty string or an empty sequence.
    lexicon_folder_path : str
        The path to the directory that holds the lexicon text files.

    Returns
    -------
    None

    """


    if not isinstance(lexicon_folder_path, str):
        raise TypeError(f"'lexicon_folder_path' must be a string")

    _validate_word_input(
        WORDS,
        character_validation=False,
        majuscule_validation=False
    )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    file_base = f'lexicon_'

    # dont block bad first characters here, just let them through and if
    # the file doesnt exist for it, then skip it.
    file_identifiers: list[str] = \
        _identify_sublexicon(
            WORDS,
            file_validation=False
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
            with open(full_path, 'r') as f:
                raw_text = np.fromiter(f, dtype='<U40')
        except:
            # if the file does not exist in the lexicon, skip all words
            # that would be associated with that file.
            continue

        OLD_SUB_LEXICON = np.char.replace(raw_text, f'\n', f'')
        del raw_text

        PERTINENT_WORDS = [w for w in _WORDS if w[0] == file_letter]

        MASK = np.ones(len(OLD_SUB_LEXICON), dtype=np.int8)
        for _word in PERTINENT_WORDS:

            SUB_MASK = (_word == OLD_SUB_LEXICON)

            MASK -= SUB_MASK.astype(np.int8)

        del PERTINENT_WORDS, SUB_MASK

        NEW_LEXICON = list(map(str, OLD_SUB_LEXICON[(MASK == 1)]))

        del MASK, OLD_SUB_LEXICON

        with open(full_path, 'w') as f:
            for line in NEW_LEXICON:
                f.write(line+f'\n')
            f.close()

        del full_path
        del NEW_LEXICON


    del _WORDS, file_base, file_identifiers


    print(f'\n*** Lexicon update successful. ***\n')






