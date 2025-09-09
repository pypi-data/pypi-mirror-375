# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ....__shared._utilities._view_text_snippet import view_text_snippet
from ......base._validate_user_input import validate_user_str



def _quasi_auto_word_splitter(
    _word_idx: int,
    _line: list[str],
    _KNOWN_WORDS: list[str],
    _verbose: bool
) -> list[str]:
    """Look if the current 'word' that is not in the Lexicon is actually
    an erroneous compounding of two valid words that are in the Lexicon.

    Working from left to right in the word, starting after the second
    letter and stopping before the second-to-last letter, look for the
    first valid split comprised of 2 halves, each with 2 or more
    characters. Prompt the user if they want to keep the proposed split.
    If not, continue looking for and proposing valid splits until the
    user accepts a split or all valid splits are exhausted. If a split
    is found and accepted, return the 2 words; otherwise return an empty
    list.

    Parameters
    ----------
    _word_idx : int
        The index of the current word in its line.
    _line : list[str]
        The full line that the current word is in.
    _KNOWN_WORDS : list[str]
        All the words in the Lexicon and any words that have been put
        into `LEXICON_ADDENDUM` in the current session.
    _verbose : bool
        Whether to display helpful information.

    Returns
    -------
    _NEW_WORDS : list[str]
        If a valid split is found and the user accepts the split, the
        word is split and the two new words are returned. If no split
        is found, an empty list is returned.

    """


    _word = _line[_word_idx]

    _NEW_WORDS = []
    for split_idx in range(2, len(_word) - 1):
        if _word[:split_idx] in _KNOWN_WORDS and _word[split_idx:] in _KNOWN_WORDS:
            print(view_text_snippet(_line, _word_idx, _span=9))
            print(f"\n*{_word}* IS NOT IN LEXICON\n")
            print(f'\n*** RECOMMEND *{_word[:split_idx]}* AND '
                  f'*{_word[split_idx:]}* ***\n')
            # if user does not like the suggested split, continue making
            # & recommending splits. if no more splits, return the empty _NEW_LINE.
            if validate_user_str(f'Accept? (y/n) > ', 'YN') == 'Y':

                _NEW_WORDS.append(_word[:split_idx])
                _NEW_WORDS.append(_word[split_idx:])

                if _verbose:
                    print(
                        f'\n*** SUBSTITUTING *{_word}* WITH *{_word[:split_idx]}* '
                          f'AND *{_word[split_idx:]}*\n'
                    )

                break


    return _NEW_WORDS




