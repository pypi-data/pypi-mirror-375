# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
from ._type_aliases import (
    XContainer,
    XWipContainer,
    SepType,
    SepWipType,
    SepFlagsType,
    LineBreakType,
    LineBreakWipType,
    LineBreakFlagsType
)

import numbers
import re

import numpy as np

from ._transform._sep_lb_finder import _sep_lb_finder
from ._transform._transform import _transform
from ._validation._validation import _validation
from .._TextJoiner.TextJoiner import TextJoiner
from .._TextSplitter.TextSplitter import TextSplitter

from ..__shared._transform._map_X_to_list import _map_X_to_list
from ..__shared._param_conditioner._param_conditioner import _param_conditioner

from ....base._copy_X import copy_X
from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)



class TextJustifier(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Justify text as closely as possible to the number of characters
    per line given by the user.

    This is not designed for making final drafts of highly formatted
    business letters. This is a tool designed to turn highly ragged
    text into block form that is more easily ingested and manipulated
    by humans and machines. Consider lines read in from text files or
    scraped from the internet. Many times there is large disparity in
    the number of characters per line, some lines may have a few
    characters, and other lines may have thousands of characters (or
    more.) This tool will square-up the text for you.

    The cleaner your data is, the more powerful this tool is, and
    the more predicable are the results. TextJustifier (TJ) in no
    way is designed to do any cleaning. See the other pybear text
    wrangling modules for that. While TJ will handle any text
    passed to it and blindly apply the instructions given to it,
    results are better when this is used toward the end of a text
    processing workflow. For  best results, pybear recommends that
    removal of junk characters (pybear :class:`TextReplacer`), empty
    strings (pybear :class:`TextRemover`), and leading and trailing
    spaces (pybear :class:`TextStripper`) be done before using TJ.

    There are 3 operative parameters for justifying text in this module,
    `n_chars`, `sep`, and `line_break`. `n_chars` is the target number
    of characters per line. The minimum allowed value is 1, and there is
    no maximum value. The `sep` parameter is the string sequence(s) or
    regex pattern(s) that tell TJ where it is allowed to wrap text. It
    does not mean that TJ WILL wrap that particular text, but that it
    can if it needs to when near the `n_chars` limit on a line. The wrap
    occurs AFTER the `sep` sequence. A common `sep` is a single space.
    The `line_break` parameter is the string sequence(s) or regex
    pattern(s) that tell TJ where it MUST wrap text. When TJ finds a
    `line_break` sequence, it will force a new line. The break occurs
    AFTER the `line_break` sequence. A typical `line_break` might be a
    period.

    When TJ is instantiated, there must be at least one `sep` for TJ
    to wrap on but there do not need to be any specified line breaks.
    This means that `sep` must be passed but `line_break` can be left
    to the default value of None. Both `sep` and `line_break` can accept
    patterns as literal strings or regular expressions. Also, both
    parameters can accept multiple patterns to wrap/break on via 1D
    sequences of patterns.

    To identify wrap points and line breaks using literal strings, pass
    a string or 1D sequence of strings to `sep` and `line_break`. You
    can mix containers to the different parameters, i.e., one could be a
    sequence and the other could be a single string. To identify wrap
    points and line breaks using regex patterns, pass a re.compile
    object with the regex pattern (and flags, if desired) or pass a 1D
    sequence of such objects. DO NOT PASS A REGEX PATTERN AS A LITERAL
    STRING. YOU WILL NOT GET THE CORRECT RESULT. ALWAYS PASS REGEX
    PATTERNS IN A re.compile OBJECT. DO NOT ESCAPE LITERAL STRINGS,
    TextJustifier WILL DO THAT FOR YOU. If you don't know what any of
    that means, then you don't need to worry about it, just use literal
    strings.

    Literal strings and re.compile objects cannot be mixed. You must
    go all-in on literals or all-in on regex. This means that you
    cannot pass 1D lists containing a mix of literals and re.compile
    objects to `sep` and `line_break`. Additionally, whatever wrap-point
    identification method is used in `sep` must be also be used for
    `line_break`. Meaning, if you used re.compile objects to indicate
    wrap points for `sep`, then you must also use re.compile objects to
    indicate break points for `line_break`.

    Literal string mode has validation and protections in place that
    prevent conflicts that could lead to undesired results. These
    safeguards make for a predictable tool. But these safeguards are
    not in place in regex mode. The reason is that the exact behavior
    of literal strings, as opposed to regex, can be predicted before
    ever seeing any text. Conflicts are impossible to predict when using
    regex unless you know the text it is applied to beforehand. No `sep`
    can be a substring of another `sep`. No `sep` can be identical to a
    `line_break` entry and no `sep` can be a substring of a `line_break`.
    No `line_break` can be a substring of another `line_break`. No
    `line_break` can be identical to a `sep` entry and no `line_break`
    can be a substring of a `sep`. But these rules do not apply when
    using regex. In regex mode, a conflict exists when both the `sep`
    pattern and the `line_break` pattern identify the same location in
    text as the first character of a match. In that case, TJ applies
    `sep`. It is up to the user to assess the pitfalls and the likelihood
    of error when using regex on their data. The user should inspect
    their results to ensure the desired outcome.

    TJ searches always default to case-sensitive, but can be made to
    be case-insensitive. You can globally set this behavior via the
    `case_sensitive` parameter. For those of you that know regex, you
    can also put flags in the re.compile objects passed to `sep` and
    `line_break`. Also, flags can be set globally for each of those
    parameters via `sep_flags` and `line_break_flags`, respectfully.
    Case-sensitivity is generally controlled by `case_sensitive` but
    IGNORECASE flags passed via re.compile objects or to the 'flags'
    parameters will ALWAYS overrule `case_sensitive`.

    Some lines in the text may not have any of the given wrap separators
    or line breaks at the end of the line. When justifying text and
    there is a shortfall of characters in a line, TJ will look to the
    next line to backfill strings. In the case where the line being
    backfilled onto does not have a separator at the end of the string,
    the character string given by `backfill_sep` will separate the
    otherwise separator-less string from the string being backfilled
    onto it.

    As simple as the tool is in concept, there are some nuances. Here is
    a non-exhaustive list of some of the quirks that may help the user
    understand some edge cases and explain why TJ returns the things
    that it does.
    1) TJ will not autonomously hyphenate words.
    2) If a line has no wraps or line-breaks in it, then TJ can only do
    2 things with it. If a line is given as longer than `n_chars` and
    there are no places to wrap, TJ will return the line as given,
    regardless of what `n_chars` is set to. But if the line is shorter
    than `n_chars`, it may have text from the next line(s) backfilled
    onto it.
    3) If `n_chars` is set very low, perhaps lower than the length of
    words (tokens) that may normally be encountered, then those
    words/lines will extend beyond the `n_chars` margin. Cool trick: if
    you want an itemized list of all the tokens in your text, set
    `n_chars` to 1.

    TJ accepts 1D and 2D data formats. Accepted objects include Python
    built-in lists, tuples, and sets, numpy arrays, pandas series and
    dataframes, and polars series and dataframes. When data is passed
    in a 1D container, results are always returned as a 1D Python
    list of strings. When data is passed in a 2D container, TJ uses
    pybear :class:`TextJoiner` and the `join_2D` parameter to convert it
    to a 1D list for processing. Then, once the processing is done, TJ
    uses pybear :class:`TextSplitter` and the `join_2D` parameter again
    to convert it back to 2D. The 2D results are always returned in a
    Python list of Python lists of strings. See TextJoiner and
    TextSplitter.

    TJ is a full-fledged scikit-style transformer. It has fully
    functional `get_params`, `set_params`, `transform`, and `fit_transform`
    methods. It also has `partial_fit`, `fit`, and `score` methods, which
    are no-ops. TJ technically does not need to be fit because it already
    knows everything it needs to do transformations from the parameters.
    These no-op methods are available to fulfill the scikit transformer
    API and make TJ suitable for incorporation into larger workflows,
    such as Pipelines and dask_ml wrappers.

    Because TJ doesn't need any information from :meth:`partial_fit`
    and :meth:`fit`, it is technically always in a 'fitted' state and
    ready to transform data. Checks for fittedness will always return
    True.

    TJ has one attribute, :attr:`n_rows_`, which is only available after
    data has been passed to :meth:`transform`. `n_rows_` is the number
    of rows of text seen in the original data. The outputted data may
    not have the same number of rows as the inputted data. This number
    is not cumulative and only reflects that last batch of data passed
    to `transform`.

    Parameters
    ----------
    n_chars : int, default = 79
        The target number of characters per line when justifying the
        given text. Minimum allowed value is 1; there is no maximum
        value. Under normal expected operation with reasonable margins,
        the outputted text will not exceed this number but can fall
        short. If margins are unusually small, the output can exceed
        the given margins (e.g. the margin is set lower than an
        individual word's length.)
    sep : SepType, default = ' '
        The literal string(s) or re.compile object(s) that indicate
        to `TextJustifier` where it is allowed to wrap a line. When
        passed as a 1D sequence, TJ will consider any of those patterns
        as a place where it can wrap a line. If a `sep` pattern is
        in the middle of a sequence that might otherwise be expected
        to be contiguous, TJ will wrap a new line AFTER the `sep`
        indiscriminately if proximity to the `n_chars` limit dictates
        to do so. Cannot be an empty string or a regex pattern that
        blatantly returns zero-span matches. Cannot be an empty sequence.
        When passed as re.compile object(s), it is only validated to be
        an instance of re.Pattern and that it is not likely to return
        zero-span matches. TJ does not assess the validity of the
        expression itself. Any exceptions would be raised by `re.search`.
        See the main docs for more discussion about limitations on what
        can be passed here.
    sep_flags : int | None, default = None
        The flags for the `sep` parameter. THIS WILL APPLY EVEN IF YOU
        PASS LITERAL STRINGS TO `sep`. IGNORECASE flags passed to this
        will overrule `case_sensitive` for `sep`. This parameter is only
        validated by TJ to be an instance of numbers.Integral or None.
        TJ does not assess the validity of the value. Any exceptions
        would be raised by `re.search`.
    line_break : LineBreakType, default = None
        Literal string(s) or re.compile object(s) that indicate to TJ
        where it MUST end a line. TJ will start a new line immediately
        AFTER the occurrence of the pattern regardless of the number
        of characters in the line. When passed as a 1D sequence of
        literals or re.compile objects, TJ will start a new line
        immediately after all occurrences of the patterns given. If
        None, do not force any line breaks. If the there are no
        patterns in the data that match the given strings, then there
        are no forced line breaks. If a `line_break` pattern is in the
        middle of a sequence that might otherwise be expected to be
        contiguous, TJ will force a new line after the `line_break`
        indiscriminately. Cannot be an empty string or a regex pattern
        that blatantly returns zero-span matches. Cannot be an empty
        1D sequence. When passed as re.compile object(s), it is only
        validated to be an instance of re.Pattern and that it is not
        likely to return zero-span matches. TJ does not assess the
        validity of the expression itself. Any exceptions would be
        raised by `re.search`. See the main docs for more discussion
        about limitations on what can be passed here.
    line_break_flags : int | None, default = None
        The flags for the `line_break` parameter. THIS WILL APPLY EVEN
        IF YOU PASS LITERAL STRINGS TO `line_break`. IGNORECASE flags
        passed to this will overrule `case_sensitive` for `line_break`.
        This parameter is only validated by TJ to be an instance of
        numbers.Integral or None. TJ does not assess the validity of
        the value. Any exceptions would be raised by `re.search`.
    backfill_sep : str, default = ' '
        In the case where a line is shorter than `n_chars`, DOES NOT END
        WITH A WRAP SEPARATOR, and the following line is short enough to
        be merged with it, this character string will separate the two
        strings when merged. If you do not want a separator in this case,
        pass an empty string to this parameter.
    join_2D : str, default = ' '
        Ignored if the data is given as a 1D sequence. For 2D containers
        of strings, this is the character string sequence that is used
        to join the strings within rows to convert the data to 1D for
        processing. The single string value is used to join the strings
        within the rows for all rows in the data.

    Attributes
    ----------
    n_rows_

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]] | set[str]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[str] | list[list[str]]

    NCharsType:
        int

    CoreSepBreakTypes:
        str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]

    SepType:
        CoreSepBreakTypes

    LineBreakType:
        CoreSepBreakTypes | None

    CoreSepBreakWipType:
        re.Pattern[str] | tuple[re.Pattern[str], ...]

    SepWipType:
        CoreSepBreakWipType

    LineBreakWipType:
        CoreSepBreakWipType | None

    CaseSensitiveType:
        bool

    SepFlagsType:
        int | None

    LineBreakFlagsType:
        int | None

    BackfillSepType:
        str

    Join2DType:
        str

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextJustifier as TJ
    >>> trfm = TJ(n_chars=70, sep=' ', backfill_sep=' ')
    >>> X = [
    ...     'Old Mother Hubbard',
    ...     'Went to the cupboard',
    ...     'To get her poor dog a bone;',
    ...     'But when she got there,',
    ...     'The cupboard was bare,',
    ...     'And so the poor dog had none.',
    ...     'She went to the baker’s',
    ...     'To buy him some bread;',
    ...     'And when she came back,',
    ...     'The poor dog was dead.'
    ... ]
    >>> out = trfm.fit_transform(X)
    >>> out = list(map(str.strip, out))
    >>> for _ in out:
    ...     print(_)
    Old Mother Hubbard Went to the cupboard To get her poor dog a bone;
    But when she got there, The cupboard was bare, And so the poor dog
    had none. She went to the baker’s To buy him some bread; And when she
    came back, The poor dog was dead.
    >>>
    >>> # Demonstrate regex and do a different justify on the same data
    >>> trfm.set_params(n_chars=45, sep=[re.compile(' '), re.compile(',')])
    TextJustifier(n_chars=45, sep=[re.compile(' '), re.compile(',')])
    >>> out = trfm.fit_transform(X)
    >>> out = list(map(str.strip, out))
    >>> for _ in out:
    ...     print(_)
    Old Mother Hubbard Went to the cupboard To
    get her poor dog a bone; But when she got
    there,The cupboard was bare,And so the poor
    dog had none. She went to the baker’s To buy
    him some bread; And when she came back,The
    poor dog was dead.


    """

    def __init__(
        self,
        *,
        n_chars:int = 79,
        sep:SepType = ' ',
        sep_flags:SepFlagsType = None,
        line_break:LineBreakType = None,
        line_break_flags:LineBreakFlagsType = None,
        case_sensitive:bool = True,
        backfill_sep:str = ' ',
        join_2D:str = ' '
    ) -> None:
        """Initialize the TextJustifier instance."""

        self.n_chars = n_chars
        self.sep = sep
        self.sep_flags = sep_flags
        self.line_break = line_break
        self.line_break_flags = line_break_flags
        self.case_sensitive = case_sensitive
        self.backfill_sep = backfill_sep
        self.join_2D = join_2D


    @property
    def n_rows_(self) -> int:
        """Get the `n_rows_` attribute.

        The number of rows in data passed to :meth:`transform`; may not
        be the same as the number of rows in the outputted data. This
        number is not cumulative and only reflects the last batch of
        data passed to `transform`.

        Returns
        -------
        n_rows_ : int
            The number of rows in the data passed to `transform`.

        """

        return self._n_rows


    def __pybear_is_fitted__(self) -> bool:
        return True


    def get_metadata_routing(self):
        """get_metadata_routing is not implemented in TextJustifier."""
        raise NotImplementedError(
            f"'get_metadata_routing' is not implemented in TextJustifier"
        )


    # def get_params
    # handled by GetParamsMixin


    # def set_params
    # handled by SetParamsMixin


    # def fit_transform
    # handled by FitTransformMixin


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op batch-wise fit operation.

        Parameters
        ----------
        X : XContainer
            The data to justify. Ignored.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The TextJustifier instance.

        """

        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """No-op one-shot fit operation.

        Parameters
        ----------
        X : XContainer
            The data to justify. Ignored.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The TextJustifier instance.

        """

        return self.partial_fit(X, y)


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """No-op score method.

        Needs to be here for dask_ml wrappers.

        Parameters
        ----------
        X : Any
            The data. Ignored.
        y : Any, default = None
            The target for the data. Ignored.

        Returns
        -------
        None


        """

        check_is_fitted(self)

        return


    @staticmethod
    def _cond_helper(
        _obj: LineBreakType,
        _case_sensitive: bool,
        _flags: int | None,
        _name: str
    ) -> None | re.Pattern[str] | tuple[re.Pattern[str], ...]:
        """Helper for making re.compiles and putting in flags for `sep`
        and `line_break`.

        Only used in one place in :meth:`transform`.
        """

        # even tho using LineBreak type hints, could be sep or line_break

        if isinstance(_obj, (type(None), str, re.Pattern)):
            __obj = _obj
        else:
            # must convert whatever sequence was into tuple for _p_c
            __obj = tuple(list(_obj))

        return _param_conditioner(
            __obj, _case_sensitive, _flags, False, 1, _name
        )


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Justify the text in a 1D sequence of strings or a (possibly
        ragged) 2D array-like of strings.

        Parameters
        ----------
        X : XContainer
            The data to justify.
        copy : bool, default = False
            Whether to directly operate on the passed `X` or on a
            deepcopy of `X`.

        Returns
        -------
        X_tr : XWipContainer
            The justified data returned as a 1D Python list of strings.

        """

        check_is_fitted(self)

        _validation(
            X, self.n_chars, self.sep, self.sep_flags, self.line_break,
            self.line_break_flags, self.case_sensitive, self.backfill_sep,
            self.join_2D
        )

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X


        X_tr: XWipContainer = _map_X_to_list(X_tr)

        # when the 2D X_tr == [[]], the trip thru TextJoiner and TextSplitter
        # is causing [['']] to be returned. When this is the case, just
        # return the original [[]]. 1D [] is returning as []
        if np.array_equal(X_tr, [[]]):
            return X_tr

        _was_2D = False
        # we know from validation it is legit 1D or 2D, do the easy check
        if all(map(isinstance, X_tr, (str for _ in X_tr))):
            # then is 1D:
            pass
        else:
            # then could only be 2D, need to convert to 1D
            _was_2D = True
            X_tr = TextJoiner(sep=self.join_2D).fit_transform(X_tr)

        # X_tr must be 1D at this point
        self._n_rows: int = len(X_tr)

        # condition sep and line_break parameters -- -- -- -- -- -- --
        _sep: SepWipType = \
            self._cond_helper(
                self.sep, self.case_sensitive, self.sep_flags, 'sep'
            )
        _line_break: LineBreakWipType = \
            self._cond_helper(
                self.line_break, self.case_sensitive, self.line_break_flags,
                'line_break'
            )
        # END condition sep and line_break parameters -- -- -- -- -- --

        X_tr: list[str] = _transform(
            X_tr, self.n_chars, _sep, _line_break, self.backfill_sep
        )

        if _was_2D:
            # when justifying (which is always in 1D), if the line ended
            # with a sep or line_break, then that stayed on the end of
            # the last word in the line. and if that sep or line_break
            # coincidentally .endswith(join_2D), then TextSplitter will
            # leave a relic '' at the end of that row. so for the case
            # where [sep | line_break].endswith(join_2D) and
            # line.endswith([sep | line_break), look at the last word in
            # each line and if it ends with that sep/line_break, indicate
            # as such so that after TextSplitter the '' and the end of
            # those rows can be deleted. dont touch any other rows that
            # might end with '', TJ didnt do it its the users fault.
            # backfill_sep should never be at the end of a line.
            _MASK = _sep_lb_finder(X_tr, self.join_2D, _sep, _line_break)

            X_tr = TextSplitter(sep=self.join_2D).fit_transform(X_tr)

            if any(_MASK):
                for _row_idx in range(len(X_tr)):
                    # and X_tr[_row_idx][-1] == '' is just insurance, thinking
                    # that it should always be the case that whatever was
                    # marked as True by _sep_lb_finder must end with ''.
                    if _MASK[_row_idx] is True and X_tr[_row_idx][-1] == '':
                        X_tr[_row_idx].pop(-1)

            del _MASK


        return X_tr







