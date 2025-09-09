# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np



def _find_duplicates(
    string_frequency_: dict[str, int]
) -> dict[str, int]:
    """Find any duplicates in the Lexicon.

    If any, display to screen and return as Python dictionary with
    frequencies.

    Parameters
    ----------
    string_frequency_ : dict[str, int] - The unique words
        in the lexicon and their frequencies. There should be only one
        entry for each word in the lexicon, i.e., all frequencies should
        be 1.

    Returns
    -------
    DUPLICATES : dict[str, int]
        Dictionary of any duplicates in the lexicon and their frequencies.

    """

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(string_frequency_, dict)
    assert all(map(
        isinstance,
        string_frequency_.keys(),
        (str for _ in string_frequency_)
    ))
    assert all(map(
        isinstance,
        string_frequency_.values(),
        (int for _ in string_frequency_)
    ))
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if sum(string_frequency_.values()) == len(string_frequency_):
        print(f'\n*** THERE ARE NO DUPLICATES IN THE LEXICON ***\n')
        return {}
    else:

        UNIQUES = np.fromiter(string_frequency_.keys(), dtype='<U30')
        COUNTS = np.fromiter(string_frequency_.values(), dtype=np.uint32)

        MASK = (COUNTS > 1)
        DUPLICATES = dict((zip(
            map(str, UNIQUES[MASK]),
            map(int, COUNTS[MASK])
        )))

        del UNIQUES, COUNTS, MASK

        print()
        # print(f'*' * 79)
        print(f'\n DUPLICATE'.ljust(30) + f'COUNT')
        print(f'-' * 40)
        [print(f'{k}'.ljust(30) + f'{v}') for k, v in DUPLICATES.items()]
        print()
        # print(f'*' * 79)


        return DUPLICATES





