# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import itertools
import re

import numpy as np



def variable_finder(
    text:str | None = None,
    filepath:str | None = None
) -> list[str]:
    """Search a string OR a text file for substrings that appear to be
    variable declarations.

    Parameters
    ----------
    text : str | None
        The text to search for variable names.
    filepath : str | None
        The file path to open and search for variable names.

    Returns
    -------
    out : list[str]
        List of variable names found in the passed string or file.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if not isinstance(text, (str, type(None))):
        raise TypeError(f"'text' must be a string")
    if not isinstance(filepath, (str, type(None))):
        raise TypeError(f"'filepath' must be a string")

    if not ((text is None) + (filepath is None)) == 1:
        raise ValueError(f"must pass ONE of 'text' or 'filepath'")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if filepath:
        _raw_text = np.fromiter(
            open(filepath, mode='r', encoding="utf8"), dtype=object
        ).tolist()
        _raw_text = list(map(lambda x: x+f"\n", _raw_text))
        _raw_text = " ".join(_raw_text)
    elif text:
        _raw_text = text

    _finder = '[A-Za-z0-9_\.,: ]+'    # finds variable names
    _finder += '[ ]{0,1}[:]{0,1}[ ]{0,1}[A-Za-z\., \|\[\]]+[ ]{0,1}' # type hints'
    _finder += '[=][ ]{0,1}[A-Za-z0-9\'\"_\.\\\]+'  # find the value

    out = re.findall(re.compile(_finder), _raw_text)
    out += re.findall(re.compile('def [A-Za-z0-9_]+'), _raw_text)
    out += re.findall(re.compile('class [A-Za-z0-9_]+'), _raw_text)

    _finder = '[A-Za-z0-9_\.,: ]+'       # finds variable names
    _finder += '[ ]{0,1}[:]{0,1}[ ]{0,1}[A-Za-z\., \|\[\]]{0,}' # type hints
    for _idx, _match in enumerate(out):
        out[_idx] = re.search(re.compile(_finder), _match).group().strip()
        if '=' in out[_idx]:
            out[_idx] = out[_idx][:out[_idx].find('=')]
        if ',' in _match:
            out[_idx] = list(map(str.strip, out[_idx].split(',')))
        else:
            out[_idx] = [out[_idx]]

    out: list[str] = list(set(itertools.chain(*out)))

    out = [i for i in out if len(i) > 0]

    _functions = [i for i in out if 'def' in i]
    _classes = [i for i in out if 'class' in i]
    out = set(out) - set(_functions) - set(_classes)
    out = list(sorted(out)) + list(sorted(_functions))  + list(sorted(_classes))
    del _functions, _classes

    for _idx, _match in enumerate(out):
        if ':' in out[_idx]:
            out[_idx] = out[_idx][:out[_idx].find(':')]

    return out










