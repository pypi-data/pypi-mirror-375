# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)

import re
import numbers



PatternType: TypeAlias = None | re.Pattern[str] | tuple[re.Pattern[str], ...]



def _val_compile_holder(
    _ch:PatternType | list[PatternType],
    _n_rows:int,
    _name:str = 'unnamed compile holder'
) -> None:
    """Validate the WIP parameter 'compile_holder'.

    Must be None, re.Pattern, a tuple of re.Patterns, or a list of Nones,
    re.Patterns, and/or tuples of re.Patterns. This object is almost 100%
    'data-agnostic', meaning it doesn't know anything about the data,
    like dimensionality or what is in it, except the number of rows in it.

    Parameters
    ----------
    _ch : PatternType | list[PatternType]
        The regex pattern(s) to search for in text data.
    _n_rows : int
        The number of rows in the data passed to transform.
    _name : str, default = 'unnamed compile holder'
        The name of the corresponding pattern-holder param in the home
        module, like 'split', 'replace', 'ngrams', etc.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    PatternType:
        None | re.Pattern[str] | tuple[re.Pattern[str], ...]

    """


    assert isinstance(_n_rows, numbers.Integral)
    assert not isinstance(_n_rows, bool)
    assert _n_rows >= 0

    assert isinstance(_name, str)

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    try:
        if isinstance(_ch, (type(None), re.Pattern)):
            raise UnicodeError
        elif isinstance(_ch, tuple):
            if not all(map(isinstance, _ch, (re.Pattern for _ in _ch))):
                raise Exception
            raise UnicodeError
        elif isinstance(_ch, list):
            for thing in _ch:
                if isinstance(thing, (type(None), re.Pattern)):
                    pass
                elif isinstance(thing, tuple):
                    if not all(map(isinstance, thing, (re.Pattern for _ in thing))):
                        raise Exception
                else:
                    raise Exception

            if len(_ch) != _n_rows:
                raise TimeoutError

            raise UnicodeError
        else:
            raise Exception
    except UnicodeError:
        pass
    except TimeoutError:
        raise ValueError(
            f"Algorithm failure. if '{_name}' is a list, the length of "
            f"the compile-holder for it must be equal to the number "
            f"of rows in the data passed to transform. \ngot {len(_ch)}, "
            f"expected {_n_rows}"
        )
    except Exception as e:
        raise TypeError(
            f"Algorithm failure. the compile-holder for '{_name}' must "
            f"be None, re.Pattern, tuple[re.Pattern, ...], or a list of "
            f"Nones, re.Patterns, and/or tuple[re.Pattern, ...]."
            f"\ngot {type(_ch)}."
        )






