# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _auto_word_splitter(
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
    characters. If there is a match, return the words, otherwise return
    an empty list.

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
        If a valid split is found, the word is split and the two new
        words are returned. If no split is found, this list is empty.

    """


    _word = _line[_word_idx]

    # LOOK IF word IS 2 KNOWN WORDS MOOSHED TOGETHER

    _NEW_WORDS = []
    for split_idx in range(2, len(_word) - 1):
        if _word[:split_idx] in _KNOWN_WORDS \
                and _word[split_idx:] in _KNOWN_WORDS:

            _NEW_WORDS.append(_word[:split_idx])
            _NEW_WORDS.append(_word[split_idx:])

            if _verbose:
                print(
                    f'\n*** SUBSTITUTING *{_word}* WITH *{_word[:split_idx]}* '
                    f'AND *{_word[split_idx:]}*\n'
                )
            break


    return _NEW_WORDS




