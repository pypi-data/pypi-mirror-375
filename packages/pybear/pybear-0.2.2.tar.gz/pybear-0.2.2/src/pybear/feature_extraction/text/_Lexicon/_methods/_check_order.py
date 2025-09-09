# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np



def _check_order(
    lexicon_: list[str]
) -> list[str]:
    """Determine if the lexicon files are out of alphabetical order.

    Compare the words as stored against a sorted vector of the words.
    Displays any out-of-order words to screen and return a Python list
    of the words.

    Parameters
    ----------
    lexicon_ : list[str]
        The Python list containing the pybear lexicon.

    Returns
    -------
    OUT_OF_ORDER : list[str]
        Vector of any out of sequence words in the lexicon.

    """


    assert isinstance(lexicon_, list)
    assert all(map(isinstance, lexicon_, (str for _ in lexicon_)))


    # np.unique sorts asc alpha
    __ = np.unique(lexicon_)

    if np.array_equiv(lexicon_, __):

        print(f'\n*** LEXICON IS IN ALPHABETICAL ORDER ***\n')

        return []

    elif len(lexicon_) != len(__):

        print(f'\n*** LEXICON HAS DUPLICATE ENTRIES. USE find_duplicates(), ***\n')

        return []

    else:

        print(f'\n*** LEXICON IS OUT OF ORDER ***\n')

        OUT_OF_ORDER = []

        for idx in range(len(__)):
            # len(__) must <= len(lexicon_)
            if lexicon_[idx] != __[idx]:
                OUT_OF_ORDER.append(lexicon_[idx])

        print(f'OUT OF ORDER:')
        print(OUT_OF_ORDER)


        return OUT_OF_ORDER







