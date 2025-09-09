# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    SepWipType,
    LineBreakWipType
)

import numbers
import re



def _stacker(
    _X: list[str],
    _n_chars: int,
    _sep: SepWipType,
    _line_break: LineBreakWipType,
    _backfill_sep: str
) -> list[str]:
    """Compile the text in `X` line by line to fill the `n_chars` per
    row requirement.

    After the original text is split into lines of indivisible chunks of
    text by :func:`_splitter` (each line ends with `sep` or `line_break`,
    or has neither), recompile the text line by line to fill the `n_chars`
    per row requirement. Observe the `line_break` rule that that pattern
    must end a line and subsequent text starts on a new line below.
    Observe the `backfill_sep` rule that when a line that does not end
    with a `sep` pattern has a line from a row below stacked to it, that
    the `backfill_sep` sequence is inserted in between.

    How could a line in the split text have no `sep` or `line_break`
    at the end? Because that was how the line was in the raw text,
    and :func:`_splitter` did a no-op on it because there were no seps
    or line breaks in it.

    `sep` and `line_break` must have already been processed
    by :func:`_param_conditioner`, i.e., all literal strings must be
    converted to re.compile and any flags passed as parameters or
    associated with `case_sensitive` must have been put in the compile(s).

    Parameters
    ----------
    _X : list[str]
        The data as processed by _splitter(). Must be a list of strings.
        Each string is an indivisible unit of text based on the given
        separators and line-breaks.
    _n_chars : int
        The number of characters per line to target when justifying the
        text.
    _sep : SepWipType
        The regex pattern(s) that indicate to TJ where it is allowed to
        wrap a line.
    _line_break : LineBreakWipType
        The regex pattern(s) that indicate to TJ where it must force a
        new line.
    _backfill_sep : str
        Some lines in the text may not have any of the given wrap
        separators or line breaks at the end of the line. When justifying
        text and there is a shortfall of characters in a line, TJ will
        look to the next line to backfill strings. In the case where the
        line being backfilled onto does not have a separator or line
        break at the end of the string, this character string will
        separate the otherwise separator-less string from the string
        being backfilled onto it.

    Returns
    -------
    _X : list[str]
        The data in its final justified state.

    Notes
    -----

    **Type Aliases**

    SepWipType:
        re.Pattern[str] | tuple[re.Pattern[str], ...]

    LineBreakWipType:
        None | CoreSepBreakWipType

    """

    assert isinstance(_X, list)
    assert isinstance(_n_chars, numbers.Integral)
    assert isinstance(_sep, (re.Pattern, tuple))
    assert isinstance(_line_break, (type(None), re.Pattern, tuple))
    assert isinstance(_backfill_sep, str)


    # _splitter has turned every line in _X into an indivisible chunk.
    # each string is immutable.

    # condition _sep and _line_break to only look at the end -- -- -- --
    # that means put $ at the end of all the patterns in the compiles.
    # and convert single compile to iterable.
    def _precondition_helper(
        _obj: LineBreakWipType
    ) -> None | tuple[re.Pattern[str], ...]:
        """Helper function to put $ at the end of all the patterns in
        the compiles and convert single compile to iterable.
        """

        if _obj is None:
            return None
        elif isinstance(_obj, re.Pattern):
            _new_obj = re.compile(_obj.pattern + '$', _obj.flags)
            # convert this to a tuple for easy iterating later
            _new_obj = (_new_obj, )
        elif isinstance(_obj, tuple):
            _new_obj = []
            for _compile in _obj:
                _new_obj.append(re.compile(_compile.pattern + '$', _compile.flags))
            _new_obj = tuple(_new_obj)
        else:
            raise Exception

        return _new_obj
    # END _precondition_helper -- -- -- -- -- --

    _new_sep = _precondition_helper(_sep)

    _new_line_break = _precondition_helper(_line_break)

    del _precondition_helper
    # END condition _sep and _line_break to only look at the end -- -- --


    line_idx = 0
    while True:

        # if _X is empty this will raise. make empty flow thru.
        try:
            _line = _X[line_idx]
        except IndexError:
            break
        except Exception as e:
            raise e

        # if the next line doesnt exist we cant do anymore
        try:
            _X[line_idx + 1]
        except IndexError:
            break
        except Exception as e:
            raise e


        # if a line is already at or over n_chars, go to the next line
        if len(_line) >= _n_chars:
            line_idx += 1
            continue

        # all lines below here are shorter than n_chars

        # if the line ends with a line_break, nothing can be backfilled
        # onto it
        if _new_line_break is not None:    # must be a tuple
            _hit = False
            for _lb in _new_line_break:
                _match = re.search(_lb, _line)
                if _match is not None and _match.span()[1] != _match.span()[0]:
                    line_idx += 1
                    _hit = True
                    break
            if _hit:
                continue
            del _hit, _match

        # backfill onto short lines, conditional on how the line ends
        # if it ends with a separator, do not use a backfill_sep
        _needs_backfill_sep = False
        _hit = False
        if re.search(re.compile(f'{re.escape(_backfill_sep)}$'), _line):
            # if there already is a backfill sep dont put another
            _hit = True
        else:
            for _s in _new_sep:
                _match = re.search(_s, _line)
                if _match is not None and _match.span()[1] != _match.span()[0]:
                    _hit = True
                    break
            del _match
        if not _hit:
            _needs_backfill_sep = True
        del _hit

        _addon_len = len(_X[line_idx + 1])
        # if the current line has no sep at the end, append backfill_sep
        _addon_len += len(_backfill_sep) if _needs_backfill_sep else 0

        if len(_line) + _addon_len <= _n_chars:
            if _needs_backfill_sep:
                _X[line_idx] += _backfill_sep
            _X[line_idx] += _X.pop(line_idx + 1)
            # do not increment the line index!
            # see if more lines can be pulled up to the current line from below
            continue
        else:
            # attaching addon puts it over _n_chars
            line_idx += 1
            continue


    return _X






