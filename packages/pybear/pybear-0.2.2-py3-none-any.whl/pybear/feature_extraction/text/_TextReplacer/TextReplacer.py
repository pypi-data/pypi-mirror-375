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
    ReplaceType,
    WipReplaceType,
    CaseSensitiveType,
    FlagsType
)

from ._validation._validation import _validation
from ._transform._special_param_conditioner import _special_param_conditioner
from ._transform._regexp_1D_core import _regexp_1D_core

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)

from ..__shared._transform._map_X_to_list import _map_X_to_list

from ....base._copy_X import copy_X



class TextReplacer(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Search 1D vectors or (possibly ragged) 2D arrays of text data for
    character substrings and make one-to-one replacements.

    `TextReplacer` (TR) can search for patterns to replace by literal
    strings or regex patterns.

    So why not just use `str.replace` or `re.sub`? TR provides a few
    conveniences beyond the Python built-ins. First, you can quickly
    apply multiple replacement criteria over the entire text body in one
    step. Second, you won't need to put in multiple search patterns to
    manage case-sensitivity. TR has a `case-sensitive` parameter that
    allows you to globally toggle this behavior. Third, should you need
    granular control of replacements at the individual row level, TR
    allows customized search and replacement criteria for each row in
    your data. Finally, TR is a full-blown scikit-style transformer, and
    can be incorporated into larger workflows, like pipelines.

    For those who don't know how to write regular expressions or don't
    want to spend the time fine-tuning the patterns, TR's exact string
    matching provides quick access to search and replace functionality
    with multiple criteria. For those who do know regex, TR also accepts
    regular expressions via re.compile objects.

    TR accepts find/replace pairs in tuples to the `replace` parameter.
    In the first position of the tuple, specify the substring pattern to
    be searched for in your text. Provide a literal string or re.compile
    object containing your regex pattern intended to match substrings.
    DO NOT PASS A REGEX PATTERN AS A LITERAL STRING. YOU WILL NOT GET
    THE CORRECT RESULT. ALWAYS PASS REGEX PATTERNS IN A re.compile
    OBJECT. DO NOT ESCAPE LITERAL STRINGS, `TextReplacer` WILL DO THAT
    FOR YOU. If you don't know what any of that means, then you don't
    need to worry about it.

    In the second position of the tuple, specify what to substitute
    in when a match against the corresponding pattern is found. The
    replacement value for your search pattern can be specified as a
    literal string or a callable. The callable must accept the substring
    in your text that matched the pattern, do some operation on it, and
    return a single string. An example regex replacement criteria might
    be (re.compile('[a-m]'), your_callable()).

    You can pass multiple find/replace tuples to `replace` to quickly
    execute multiple search criteria on your data. Pass multiple
    find/replace tuples described above in one enveloping tuple. An
    example might be ((',', ''), ('.', ''), (';' '')). TR works from
    left to right through the tuple when searching and replacing. Knowing
    this, the replacements can be gamed so that later searches are
    dependent on earlier replacements.

    To make fine-grained replacements on the individual rows of your
    data, you can pass a Python list of the above-described tuples and
    tuples-of-tuples. The length of the list must match the length of
    the data, for both 1D and 2D datasets. To turn off search/replace for
    particular rows of the data, put None in those indices in the list.
    So the list you pass to `replace` can contain find/replace tuples,
    tuples of find/replace tuples, and None.

    TR searches always default to case-sensitive, but can be made to
    be case-insensitive. You can globally set this behavior via the
    `case_sensitive` parameter. For those of you that know regex, you
    can also put flags in the re.compile objects passed to `replace`, or
    flags can be set globally via `flags`. Case-sensitivity is generally
    controlled by `case_sensitive` but IGNORECASE flags passed via
    re.compile objects or `flags` will ALWAYS overrule `case_sensitive`.
    `case_sensitive` also accepts lists so that you can control this
    behavior down to the individual row. When passed as a list, the
    number of entries in the list must equal the number of rows in the
    data. The list can contain True, False, and/or None. When None, the
    default of True is applied.

    If you need to use flags, they can be passed directly to a re.compile
    object in the search criteria. For example, a search criteria might
    be (re.compile('a', re.I), ''). In this case, the re.I flag will make
    that specific search case agnostic. re flags can be passed globally
    to the `flags` parameter. Any flags passed globally will be joined
    with any flags passed to the individual compile objects by bit-wise
    OR. You can also exercise fine-grained control on certain rows of
    data for the `flags` parameter. When passed as a list, the number of
    entries in the list must equal the number of rows in the data. The
    list can contain re flags (integers) or None to not apply any (new)
    flags to that row. Even if None is passed to a particular index of
    the list, any flags passed to re.compile objects would still take
    effect.

    TR does not have a 'count' parameter as you would see with `re.sub`
    and `str.replace`. When replacement is not disabled for a certain
    row, TR always makes the specified substitution for everything that
    matches your pattern. In a way, TR has a more basic implementation
    of the 'count' functionality through its all-or-None behavior. You
    can pass a list to `replace` and set the value for a particular row
    index of the data to None, in which case zero replacements will be
    made for that row. Otherwise, all replacements will be made on that
    row of data.

    TR can be instantiated with the default parameters, but this will
    result in a no-op. To actually make replacements, you must pass at
    least 1 find/replace pair to `replace`.

    TR is a scikit-style transformer with `partial_fit`, `fit`, `score`,
    `transform`, `fit_transform`, `set_params`, and `get_params` methods.
    TR is technically always fit because it does not need to learn
    anything from data to do transformations; it already knows everything
    it needs to know from the parameters. Checks for fittedness will
    always return True. The :meth:`partial_fit`, :meth:`fit`,
    and :meth:`score` methods are no-ops that allow TR to be incorporated
    into larger workflows such as scikit pipelines or dask_ml wrappers.
    The `get_params`, `set_params`, `transform`, and `fit_transform`
    methods are fully functional.

    TR accepts 1D list-like vectors of strings or (possibly ragged) 2D
    array-likes of strings. Accepted 1D containers include Python lists,
    tuples, and sets, numpy vectors, pandas series, and polars series.
    Accepted 2D objects include Python embedded sequences of sequences,
    numpy arrays, pandas dataframes, and polars dataframes. When passed
    a 1D list-like, a Python list of the same size is returned. When
    passed a possibly ragged 2D array-like, an identically-shaped list
    of Python lists is returned.

    Parameters
    ----------
    replace : ReplaceType, default = None
        The literal string pattern(s) or regex pattern(s) to search for
        and their replacement value(s).
    case_sensitive : CaseSensitiveType, default = True
        Global setting for case-sensitivity. If True (the default) then
        all searches are case-sensitive. If False, TR will look for
        matches regardless of case. This setting is overriden when
        IGNORECASE flags are passed in re.compile objects or to `flags`.
    flags : FlagsType, default = None
        The flags values(s) for the substring searches. Internally, TR
        does all its searching for substrings with `re.sub`, therefore
        flags can be passed whether you are searching for literal strings
        or regex patterns. If you do not know regular expressions, then
        you do not need to worry about this parameter. If None, the
        default flags for `re.sub` are used globally. If a single flags
        object, that is applied globally. If passed as a list, the number
        of entries must match the number of rows in the data. Flags
        objects and Nones in the list follow the same rules stated above,
        but at the row level. If IGNORECASE is passed here as a global
        setting or in a list it overrides the `case_sensitive` 'True'
        setting.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]] | set[str]]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[str] | list[list[str]]

    FindType:
        str | re.Pattern[str]
    SubstituteType:
        str | Callable[[str], str]
    PairType:
        tuple[FindType, SubstituteType]
    ReplaceSubType:
        None | PairType | tuple[PairType, ...]
    ReplaceType:
        ReplaceSubType | list[ReplaceSubType]

    WipPairType:
        tuple[re.Pattern[str], SubstituteType]
    WipReplaceSubType:
        None | WipPairType | tuple[WipPairType, ...]
    WipReplaceType:
        WipReplaceSubType | list[WipReplaceSubType]

    CaseSensitiveType:
        bool | list[bool | None]

    FlagType:
        int | None
    FlagsType:
        FlagType | list[FlagType]

    See Also
    --------
    re.sub

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextReplacer as TR
    >>> import re
    >>>
    >>> trfm = TR(replace=((',', ''),(re.compile(r'\.'), '')))
    >>> X = ['To be, or not to be, that is the question.']
    >>> trfm.fit_transform(X)
    ['To be or not to be that is the question']
    >>> trfm.set_params(replace=('b', ''))
    TextReplacer(replace=('b', ''))
    >>> trfm.fit_transform(X)
    ['To e, or not to e, that is the question.']

    """


    def __init__(
        self,
        *,
        replace: ReplaceType | None = None,
        case_sensitive: CaseSensitiveType = True,
        flags: FlagsType | None = None
    ) -> None:
        """Initialize the TextReplacer instance."""

        self.replace = replace
        self.case_sensitive = case_sensitive
        self.flags = flags


    def __pybear_is_fitted__(self) -> bool:
        return True


    def get_metadata_routing(self):
        """`get_metadata_routing` is not implemented in TextReplacer."""
        raise NotImplementedError(
            f"'get_metadata_routing' is not implemented in `TextReplacer`"
        )


    # def get_params
    # handled by GetParamsMixin


    # def set_params
    # handled by SetParamsMixin


    # def fit_transform
    # handled by FitTransformMixin


    def partial_fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """No-op batch-wise fit of the `TextReplacer` instance.

        Parameters
        ----------
        X : XContainer
            1D or 2D text data. Ignored.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextReplacer` instance.

        """

        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """No-op one-shot fit of the TextReplacer instance.

        Parameters
        ----------
        X : XContainer
            1D or 2D text data. Ignored.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextReplacer` instance.

        """

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Search the data for matches against the search criteria and
        make the specified replacements.

        Parameters
        ----------
        X : XContainer
            1D or 2D text data whose strings will be searched and may
            have substrings replaced.
        copy : bool, default=False
            Whether to make the replacements directly on the given `X`
            or on a deepcopy of `X`.

        Returns
        -------
        X_tr : XWipContainer
            The data with replacements made.

        """

        check_is_fitted(self)

        _validation(
            X,
            self.replace,
            self.case_sensitive,
            self.flags
        )

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr: XWipContainer = _map_X_to_list(X_tr)

        _rr: WipReplaceType = _special_param_conditioner(
            self.replace,
            self.case_sensitive,
            self.flags,
            _n_rows = len(X_tr)
        )

        if all(map(isinstance, X_tr, (str for _ in X_tr))):

            X_tr = _regexp_1D_core(X_tr, _rr)

        else:

            for _row_idx in range(len(X_tr)):

                X_tr[_row_idx] = _regexp_1D_core(
                    X_tr[_row_idx],
                    _rr[_row_idx] if isinstance(_rr, list) else _rr
                )

        del _rr

        return X_tr


    def score(
        self,
        X: XContainer,
        y: Any = None
    ) -> None:
        """No-op score method.

        Needs to be here for dask_ml wrappers.

        Parameters
        ----------
        X : XContainer
            1D or 2D text data. Ignored.
        y : Any, default = None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        return





