# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
)
from .._type_aliases import ReplaceType

import re



def _val_replace(
    _replace: ReplaceType,
    _n_rows: int
) -> None:
    """Validate the 'replace' argument.

    Parameters
    ----------
    _replace : ReplaceType
        A find/replace pair, a tuple of find/replace pairs, or a list of
        those things. If a list, the number of entries in the list must
        equal the number of rows in the data.
    _n_rows : int
        The number of rows of text in the data.

    Returns
    -------
    None

    """


    # could be:
    # FindType: TypeAlias = str | re.Pattern[str]
    # SubstituteType: TypeAlias = str | Callable[[str], str]
    # PairType: TypeAlias = FindType | SubstituteType
    # ReplaceSubType: TypeAlias = None | PairType | tuple[PairType, ...]
    # ReplaceType: TypeAlias = ReplaceSubType | list[ReplaceSubType]


    # helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def _core_pair_validator(
        _tuple: tuple[
            str, re.Pattern[str],
            str, Callable[[str], str]
        ]
    ):
        # must 2 entries str | re.Pattern[str] and str | Callable

        """Validate the core find/replace pairs.

        Parameters
        ----------
        _tuple : tuple
            The patterns to search for and what to replace them with.

        Returns
        -------
        None

        """

        err_msg = (
            f"when passing find/substitute pairs to 'replace', you must pass "
            f"them in a tuple with 2 positions. \nThe first position must "
            f"always be a string or a re.compile object. \nThe second must "
            f"always be a string or a callable."
        )

        if not isinstance(_tuple, tuple):
            raise TypeError(err_msg)

        if len(_tuple) != 2:
            raise ValueError(err_msg)

        allowed = (
            (str, re.Pattern),
            (str, Callable)
        )

        for _idx, _arg in enumerate(_tuple):

            if not isinstance(_arg, allowed[_idx]):
                raise TypeError(err_msg)

    # END helper function -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    err_msg = (
        f"'replace' must be None, a find/replace tuple, a tuple of "
        f"find/replace tuples, or a python list containing any mix of "
        f"those 3 things. \nsee the docs for more details."
    )


    if _replace is None:
        return
    elif isinstance(_replace, tuple):
        if all(map(isinstance, _replace, (tuple for _ in _replace))):
            for _tuple in _replace:
                _core_pair_validator(_tuple)
        else:
            _core_pair_validator(_replace)
    elif isinstance(_replace, list):
        if len(_replace) != _n_rows:
            raise ValueError(
                f"if 'replace' is passed as a list its length must equal "
                f"the number of rows in the data."
            )
        for _row in _replace:
            if _row is None:
                continue
            elif isinstance(_row, tuple):
                if all(map(isinstance, _row, (tuple for _ in _row))):
                    for _tuple in _row:
                        _core_pair_validator(_tuple)
                else:
                    _core_pair_validator(_row)
            else:
                raise TypeError(err_msg)
    else:
        raise TypeError(err_msg)





