# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence,
    TypeAlias
)

import re



SepOrLineBreakType: TypeAlias = \
    None | str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]



def _val_sep_or_line_break(
    _sep_or_line_break:SepOrLineBreakType,
    _name:Literal['sep', 'line_break'],
    _mode:Literal['str', 'regex']
) -> None:
    """Validate `sep` or `line_break`.

    `sep` cannot be None, but `line_break` can be. That is the only
    difference for what can be passed to `sep` and `line_break`.

    For string mode:
    Must be a non-empty string or a non-empty Python sequence of
    non-empty strings.

    For regex mode:
    Must be a re.compile object that does not blatantly return zero-span
    matches or a non-empty Python sequence of such objects. re.Pattern
    objects are only validated to be an instance of re.Pattern and to
    not blatantly return zero-span matches. There is no attempt to assess
    the validity of the expression itself. Any exceptions would be raised
    by re.search.

    Parameters
    ----------
    _sep_or_line_break : SepOrLineBreakType

        Cannot pass an empty string or a regex pattern that blatantly
        returns a zero-span match. Cannot be an empty sequence.

        sep: SepType - the pattern(s) that indicate to TJ where it
        is allowed to wrap a line if `n_chars` dictates to do so. A new
        line would be wrapped immediately AFTER the given pattern.
        When passed as a sequence of patterns, TJ will consider any
        of those patterns as a place where it can wrap a line. If
        the there are no patterns in a line that match the given
        pattern(s), then there are no wraps. If a `sep` pattern match
        is in the middle of a text sequence that might otherwise be
        expected to be contiguous, TJ will wrap a new line after the
        match indiscriminately if proximity to the `n_chars` limit
        dictates to do so.

        line_break: LineBreakType - Tells TJ where it must start a new
        line. A new line will be started immediately AFTER the given
        pattern regardless of the number of characters in the line. When
        passed as a sequence of patterns, TJ will force a new line
        immediately AFTER any occurrences of the patterns given. If
        None, do not force any line breaks. If the there are no patterns
        in the data that match the given pattern(s), then there are no
        forced line breaks. If a `line_break` pattern is in the middle
        of a sequence that might otherwise be expected to be contiguous,
        TJ will force a new line AFTER the `line_break` indiscriminately.
    _name:
        Literal['sep', 'line_break'] - the name of the parameter being
        validated. Must be `sep` or `line_break`.
    _mode:
        Literal['str', 'regex'] - whether validating strings for 'str'
        mode or re.compile objects for 'regex' mode.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    SepType:
        str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]

    LineBreakType:
        None | str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]

    SepOrLineBreakType:
        None | str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]]

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if _name not in ['sep', 'line_break']:
        raise ValueError(f"'_name' must be 'sep' or 'line_break'")

    if _mode not in ['str', 'regex']:
        raise ValueError(f"'_mode' must be 'str' or 'regex'")
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    if _name == 'line_break' and _sep_or_line_break is None:
        return


    # HELPER FUNCTION -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def _can_return_empty_match(
        _pat: str | re.Pattern[str]
    ) -> bool:
        """Helper function to try to identify strings or regex patterns
        that will always return zero-span matches.

        Parameters
        ----------
        _pat : str | re.Pattern[str]
            A string or re.compile object passed to TJ at init.

        """

        nonlocal _mode

        if _mode == 'str':
            return (_pat == '')
        elif _mode == 'regex':
            test_strings = ('', 'x')

            for s in test_strings:
                match = _pat.search(s)
                if match and match.span()[0] == match.span()[1]:
                    return True
            return False
        else:
            raise Exception(f'algorithm failure.')

    # END HELPER FUNCTION -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    if _mode == 'str':
        err_msg = (f"'{_name}' must be a non-empty string or a non-empty "
                   f"python sequence of non-empty strings. ")
        if _mode == '_line_break':
            err_msg += f"\nWhen passed, it must be of the same type as 'sep'. "
        if isinstance(_sep_or_line_break, str):
            if _can_return_empty_match(_sep_or_line_break):
                raise ValueError(err_msg + f"\nGot empty string.")
            return
    elif _mode == 'regex':
        err_msg = (f"'{_name}' must be a re.compile object or python "
                   f"sequence of re.compile objects. ")
        if _mode == '_line_break':
            err_msg += f"\nWhen passed, it must be of the same type as 'sep'. "
        if isinstance(_sep_or_line_break, re.Pattern):
            if _can_return_empty_match(_sep_or_line_break):
                raise ValueError(f"\nGot zero-span pattern. \nNo regex "
                    f"patterns that blatantly return zero-span matches "
                    f"are allowed.")
            return
    else:
        raise Exception(f"algorithm failure.")


    # can only get here if not str/re.compile
    try:
        iter(_sep_or_line_break)
        if isinstance(_sep_or_line_break, (str, dict)):
            raise Exception
    except Exception as e:
        raise TypeError(err_msg + f"\nGot {_sep_or_line_break}.")

    if len(_sep_or_line_break) == 0:
        raise ValueError(err_msg + f"\nGot empty sequence.")
    for _item in _sep_or_line_break:
        if _mode == 'str':
            if not isinstance(_item, str):
                raise TypeError(err_msg + f"\nGot {_item}.")
            if _can_return_empty_match(_item):
                raise ValueError(err_msg + f"\nGot empty string.")
        elif _mode == 'regex':
            if not isinstance(_item, re.Pattern):
                raise TypeError(err_msg + f"\nGot {_item}.")
            if _can_return_empty_match(_item):
                raise ValueError(f"\nGot zero-span pattern. \nNo regex "
                    f"patterns that blatantly return zero-span matches "
                    f"are allowed.")





