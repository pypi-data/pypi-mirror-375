# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias
)
from ._type_aliases import MaxSplitsType

import numbers
import re




PatternsType: TypeAlias = (
    None | re.Pattern[str] | tuple[re.Pattern[str], ...]
    | list[None | re.Pattern[str] | tuple[re.Pattern[str], ...]]
)



def _regexp_core(
    _X: Sequence[str],
    _rs: PatternsType,
    _maxsplit: MaxSplitsType
) -> list[list[str]]:
    """Split the strings in `X` based on the criteria in `sep`, `maxsplit`
    and `flags`. `sep` and `flags` have been rolled into re.compile
    objects by _param_conditioner() and are in `_rs`.

    Parameters
    ----------
    _X : XContainer
        The data, 1D vector of strings.
    _rs : PatternsType
        The pattern(s) by which to identify where strings will be split.


    Returns
    -------
    _X : list[list[str]]
        The split data.

    Notes
    -----

    **Type Aliases**

    PatternsType:
        None | re.Pattern[str] | tuple[re.Pattern[str], ...]
        | list[None | re.Pattern[str] | tuple[re.Pattern[str], ...]]

    MaxSplitType:
        int | None

    MaxSplitsType:
        MaxSplitType | list[MaxSplitType]

    """


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    assert isinstance(_X, list)
    assert all(map(isinstance, _X, (str for _ in _X)))

    _allowed = (type(None), re.Pattern, tuple, list)
    assert isinstance(_rs, _allowed)
    if isinstance(_rs, list):
        assert all(map(isinstance, _rs, (_allowed for _ in _rs)))
        assert not any(map(isinstance, _rs, (list for _ in _rs)))
    del _allowed

    _allowed = (type(None), numbers.Integral, list)
    assert isinstance(_maxsplit, _allowed)
    if isinstance(_maxsplit, list):
        assert all(map(isinstance, _maxsplit, (_allowed for _ in _maxsplit)))
        assert not any(map(isinstance, _maxsplit, (list for _ in _maxsplit)))
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # force this to return a 2D even on an empty
    # otherwise [] will blow past the for loop below and just return []
    if len(_X) == 0:
        return [[]]


    # listify 'maxsplit' if not already list
    if _maxsplit is None:
        _kwargs = [{} for _ in _X]
    elif isinstance(_maxsplit, numbers.Integral):
        _kwargs = [{'maxsplit': _maxsplit} for _ in _X]
    elif isinstance(_maxsplit, list):
        _kwargs = []
        for i, ms in enumerate(_maxsplit):
            if ms is None:
                _kwargs.append({})
            elif isinstance(ms, numbers.Integral):
                _kwargs.append({'maxsplit': ms})
            else:
                raise Exception
        pass
    else:
        raise Exception


    for _idx, _str in enumerate(_X):

        # for re.split, maxsplit=0 means split all,
        # <0 no split, > 0 == number of splits

        if _rs is None or _kwargs[_idx].get('maxsplit', 0) < 0:
            # even though it is not split, it still needs to go from str
            # to list[str]
            _X[_idx] = [_str]
            continue
        elif isinstance(_rs, re.Pattern):
            _X[_idx] = re.split(_rs, _str, **_kwargs[_idx])
        elif isinstance(_rs, tuple):
            # we need to count the splits, cant just apply each
            # re.compile in the tuple and apply maxsplit on each one.

            # maxsplit < 0 handled above
            # only maxsplit >= 0 can get in here

            n = 0
            last_end = 0
            holder = []
            while n < len(_str):

                _hit = False
                for _subpattern in _rs:
                    match = re.match(_subpattern, _str[n:])
                    if match is None:  # or match.span() == (0, 0):
                        continue
                    else:
                        _hit = True
                        end = n + match.span()[1]
                        holder.append(_str[last_end:n])
                        last_end = end
                        break

                if len(holder) == \
                        (_kwargs[_idx].get('maxsplit', 0) or float('inf')):
                    holder.append(_str[end:])
                    break
                elif _hit:
                    n = end
                elif not _hit:
                    n += 1

            if len(holder) <= (_kwargs[_idx].get('maxsplit', 0) or float('inf')):
                holder.append(_str[last_end:])

            _X[_idx] = holder

        elif isinstance(_rs, list):
            # use recursion
            _X[_idx] = _regexp_core(
                [_str],
                _rs[_idx],
                _kwargs[_idx].get('maxsplit', None)
            )[0]
        else:
            raise Exception


    return _X





