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
    SepsType,
    CaseSensitiveType,
    MaxSplitsType,
    FlagsType
)

from ._validation import _validation
from ._regexp_core import _regexp_core

from ..__shared._param_conditioner._param_conditioner import _param_conditioner
from ..__shared._transform._map_X_to_list import _map_X_to_list

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
)

from ....base._copy_X import copy_X



class TextSplitter(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Split a dataset of strings on the given separator(s).

    So why not just use `str.split` or `re.split`? `TextSplitter` has
    some advantages over the built-ins.

    First, multiple splitting criteria can be passed to the `sep`
    parameter to split on multiple character sequences, which
    `str.split` and `re.split` cannot do natively. For example,
    consider the string "How, now. brown; cow?". This can be split
    on the comma, period, and semicolon by passing a tuple to the
    `sep` parameter, such as (',', '.', ';'). The output will be
    ["How", " now", " brown", " cow?"].

    Second, the splitting criteria are simultaneously mapped over a list
    of strings, performing many splits in a single operation. Both
    `str.split` and `re.split` only accept one string argument.

    Third, the split criteria and supporting parameters can be tweaked
    for individual strings in the data by passing them in lists. This
    allows fine-grained control over splitting every string in the data,
    if you need it.

    Finally, `TextSplitter` is a scikit-style transformer and can be
    integrated into larger workflows.

    `TextSplitter` (TS) performs splits by searching for the user-given
    separators in the text and splits strings on that character sequence
    when one is found. The matching separator sequence is NOT preserved
    in the text when the split is made. You can tell `TextSplitter` what
    separators to split with by passing None, literal strings, or regular
    expressions in re.compile objects to `sep`. None does not split. A
    single literal string or re.compile object will split the text on
    all occurrences of that pattern in the text body. When using regex,
    ALWAYS pass your regex patterns in a re.compile object. DO NOT PASS
    A REGEX PATTERN AS A LITERAL STRING. YOU WILL NOT GET THE CORRECT
    RESULT. ALWAYS PASS REGEX PATTERNS IN A re.compile OBJECT. DO NOT
    ESCAPE LITERAL STRINGS, TextSplitter WILL DO THAT FOR YOU. If you
    don't know what any of that means, then you don't need to worry
    about it.

    You can pass tuples of literal strings and/or re.compile objects
    to `sep` to split on multiple separator patterns at the same time.
    Also, Nones, literal strings, re.compile objects, and tuples of
    literal strings and/or re.compile objects can be passed in a list.
    The number of entries in the list must equal the number of strings
    in the data. Each entry in the list is applied to the corresponding
    row in the data.

    If no parameters are passed, i.e., all parameters are left to their
    default values at instantiation, then `TextSplitter` does a no-op
    split, but does change your data from 1D to 2D.

    Separator searches always default to case-sensitive, but can be made
    to be case-insensitive. You can globally set this behavior via
    the `case_sensitive` parameter. For those of you that know regex,
    you can also put flags in the re.compile objects passed to `sep`, or
    flags can be set globally via `flags`. Case-sensitivity is generally
    controlled by `case_sensitive` but IGNORECASE flags passed via
    re.compile objects or `flags` will ALWAYS overrule `case_sensitive`.
    `case_sensitive` also accepts lists so that you can control this
    behavior down to the individual string.

    `TextSplitter` mimics the 'maxsplit' behavior of `re.split`. See the
    docs for `re.split` for more information. Therefore, when passing
    values to `maxsplit`, obey the rules for 'maxsplit' in `re.split`.
    When passing multiple split criteria, i.e., you have passed a
    tuple of literal strings and/or re.compile objects to `sep`, the
    `maxsplit` parameter is applied cumulatively for all separators
    working from left to right across a string in the data. For example,
    consider the string "One, two, buckle my shoe. Three, four, shut the
    door.". We are going to split on commas and periods, and perform 4
    splits, working from left to right. We enter `sep` as (',', '.') and
    pass the number 4 to `maxsplit`. Then we pass the string in a list
    to the :meth:`transform` method of `TextSplitter`. The output will be
    ["One", " two", " buckle my shoe", " Three", " four, shut the door."]
    The `maxsplit` argument worked from left to right and performed 4
    splits on commas and periods cumulatively counting the application
    of the splits for all separators.

    `TextSplitter` is a full-fledged scikit-style transformer. It has
    functional `transform` and `fit_transform` methods, as well as
    `get_params` and `set_params` methods. It has no-op `partial_fit`,
    `fit`, and `score` methods, so that it integrates into larger
    workflows like scikit pipelines and dask_ml wrappers.

    TextSplitter accepts 1D list-like vectors of strings. Accepted
    containers include Python lists, tuples, and sets, numpy vectors,
    pandas series, and polars series. Output is always returned as a
    Python list of Python lists of strings.

    Parameters
    ----------
    sep : SepsType, default = None
        The separator(s) to split the strings in `X` on. None skips every
        string in `X`, performing no splits. When passed as a single
        literal character string, that is applied to every string in `X`.
        If a single regular expression in a re.compile object is passed,
        that split is performed on every entry in `X`. When passed as a
        tuple of literal character strings and/or re.compile objects,
        each separator in the tuple is applied to every string, subject
        to the allowance set by `maxsplit`. If passed as a list of
        separators, the number of entries must match the number of
        strings in `X`, and each literal, re.compile, or tuple of
        literals/re.compiles is applied to the corresponding string in
        `X`. If any entry in the list is None, no split is performed on
        the corresponding string in `X`.
    case_sensitive : CaseSensitiveType
        Global setting for case-sensitivity. If True (the default) then
        all searches are case-sensitive. If False, TS will look for
        matches regardless of case. This setting is overriden when
        IGNORECASE flags are passed in re.compile objects or to `flags`.
    maxsplit : MaxSplitsType, default = None
        The maximum number of splits to perform on a string. Only applies
        when something is passed to `sep`. If None, the default number
        of splits for `re.split` is used on every string in `X`. If
        passed as an integer, that number is applied to every string in
        `X`. If passed as a list, the number of entries must match the
        number of strings in `X`, and each is applied correspondingly to
        `X`.  If any entry in the list is None, no split is performed on
        the corresponding string in `X`.
    flags : FlagsType, default = None
        The flags value(s) for the separator searches. If you do
        not know what this means then ignore this and just use
        `case_sensitive`. If None, the default flags for `re.split`
        are used on every string in the data. If a single flags object,
        that is applied to every string in the data. If passed as a
        list, the number of entries must match the number of strings in
        `X`. Flags objects and Nones in the list follow the same rules
        stated above.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        list[str] | tuple[str] | set[str]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.Series

    PolarsTypes:
        polars.Series

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[list[str]]

    SepType:
        None | str |  re.Pattern[str]  | tuple[str | re.Pattern[str], ...]
    SepsType:
        SepType | list[SepType]

    CaseSensitiveType:
        bool | list[bool | None]

    MaxSplitType:
        int | None
    MaxSplitsType:
        MaxSplitType | list[MaxSplitType]

    FlagType:
        int | None
    FlagsType:
        FlagType | list[FlagType]

    See Also
    --------
    re.split

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextSplitter as TS
    >>> import re
    >>>
    >>> Trfm = TextSplitter(sep=' ', maxsplit=2)
    >>> X = [
    ...     'This is a test.',
    ...     'This is only a test.'
    ... ]
    >>> Trfm.fit(X)
    TextSplitter(maxsplit=2, sep=' ')
    >>> Trfm.transform(X)
    [['This', 'is', 'a test.'], ['This', 'is', 'only a test.']]

    >>> Trfm = TextSplitter(sep=re.compile('s'), maxsplit=2)
    >>> X = [
    ...     'This is a test.',
    ...     'This is only a test.'
    ... ]
    >>> Trfm.fit(X)
    TextSplitter(maxsplit=2, sep=re.compile('s'))
    >>> Trfm.transform(X)
    [['Thi', ' i', ' a test.'], ['Thi', ' i', ' only a test.']]

    """


    def __init__(
        self,
        *,
        sep: SepsType = None,
        case_sensitive: CaseSensitiveType = True,
        maxsplit: MaxSplitsType = None,
        flags: FlagsType = None
    ):
        """Initialize the TextSplitter instance."""

        self.sep = sep
        self.case_sensitive = case_sensitive
        self.maxsplit = maxsplit
        self.flags = flags


    # handled by mixins
    # def set_params
    # def get_params
    # def fit_transform


    def __pybear_is_fitted__(self) -> bool:
        return True


    def get_metadata_routing(self):
        """metadata routing is not implemented in `TextSplitter`."""
        raise NotImplementedError(
            f"metadata routing is not implemented in TextSplitter"
        )


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op batch-wise fitting of `TextSplitter`.

        Parameters
        ----------
        X : XContainer
            A 1D sequence of strings to be split. Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextSplitter` instance.

        """

        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op one-shot fitting of TextSplitter.

        Parameters
        ----------
        X : XContainer
            A 1D sequence of strings to be split. Ignored.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextSplitter` instance.

        """

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Split the strings in `X` on the separator(s).

        Parameters
        ----------
        X : XContainer
            A 1D sequence of strings to be split.
        copy : bool, default=False
            Whether to perform the splits directly on `X` or on a
            deepcopy of `X`.

        Returns
        -------
        X_tr : XWipContainer
            The split strings.

        """


        _validation(
            X,
            self.sep,
            self.case_sensitive,
            self.maxsplit,
            self.flags
        )


        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr: XWipContainer = _map_X_to_list(X_tr)

        _rr = _param_conditioner(
            self.sep,
            self.case_sensitive,
            self.flags,
            _order_matters=False,
            _n_rows=len(X_tr),
            _name='sep'
        )


        return _regexp_core(X_tr, _rr, self.maxsplit)


    def score(
        self,
        X:XContainer,
        y:Any | None = None
    ) -> None:
        """No-op scorer.

        Parameters
        ----------
        X : XContainer
            A 1D sequence of strings. Ignored.
        y : Any, default = None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        return







