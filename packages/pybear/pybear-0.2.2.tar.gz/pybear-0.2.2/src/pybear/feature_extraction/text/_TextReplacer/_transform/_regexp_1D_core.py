# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import re

from .._type_aliases import WipReplaceType



def _regexp_1D_core(
    _X: list[str],
    _rr: WipReplaceType
) -> list[str]:
    """Search and replace substrings in a 1D list of strings using
    `re.sub`.

    Parameters
    ----------
     _X : list[str]
        The original 1D data or one row of 2D data.
    _rr :W ipReplaceType
        The pattern(s) by which to identify substrings to replace and
        their replacement(s).

    Returns
    -------
    _X : list[str]
        The 1D vector with substring replacements made.

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    assert isinstance(_X, list)
    assert all(map(isinstance, _X, (str for _ in _X)))

    # _rr is validated immediately after it is made

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # condition a single tuple so that all tuples are in a holder tuple
    if isinstance(_rr, tuple) and isinstance(_rr[0], re.Pattern):
        _rr = (_rr,)


    if _rr is None:
        return _X

    elif isinstance(_rr, tuple):

        for _idx, _word in enumerate(_X):

            for _tuple in _rr:
                # if the user passed a callable as the replacement, use
                # a helper wrapper to convert the re.Match object to str,
                # so that the user callable signature will always be
                # str -> str. if the replacement is not a callable, it
                # must be a literal, embed it in a lambda.

                if isinstance(_tuple[1], str):
                    _helper = lambda x: _tuple[1]
                elif callable(_tuple[1]):
                    _helper = lambda re_match: _tuple[1](re_match.group())
                else:
                    raise Exception

                _X[_idx] = re.sub(_tuple[0], _helper, _X[_idx])

    elif isinstance(_rr, list):

        # use recursion
        # send the one string back into this module in a list

        for _idx, _row in enumerate(_X):

            if isinstance(_rr[_idx], list):
                raise TypeError

            _X[_idx] = _regexp_1D_core([_X[_idx]], _rr[_idx])[0]

    else:
        raise Exception(f"invalid format for rr in _regexp_1D_core")


    return _X










