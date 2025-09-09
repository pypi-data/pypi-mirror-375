# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import re



def _match_finder(
    _line: list[str],
    _ngram: tuple[re.Pattern[str], ...],
) -> list[int]:
    """Slide along a sequence of strings looking for matches against an
    n-gram pattern.

    When one is found, record the first index position of the sequence
    that matches. Sequences cannot overlap.

    Parameters
    ----------
    _line : list[str]
        A single 1D sequence of strings.
    _ngram : tuple[re.Pattern[str], ...]
        A single n-gram sequence containing re.compile objects that
        specify an n-gram pattern. The 'ngram' parameter must have gone
        through by _special_param_conditioner. Cannot have less than 2
        entries.

    Returns
    -------
    _hits : list[int]
        The starting indices of sequences that match the n-gram pattern.

    """


    assert isinstance(_ngram, tuple)
    assert all(map(isinstance, _ngram, (re.Pattern for _ in _ngram)))


    # validation wont allow empty ngram
    # but there may be empty lines
    _n_len = len(_ngram)

    if _n_len > len(_line):
        return []


    _hits = []
    _idx = 0
    while _idx + len(_ngram) <= len(_line):

        _block = _line[_idx: _idx + _n_len]

        # _sp = sub_pattern
        _ngram_matches = [
            re.fullmatch(_sp, _word) for _sp, _word in zip(_ngram, _block)
        ]

        if all(_ngram_matches):
            _hits.append(_idx)
            _idx += _n_len
        else:
            _idx += 1


    return _hits





