# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
import numpy.typing as npt
from ._type_aliases import (
    XContainer,
    XWipContainer,
    NGramsType,
    NGramsWipType,
    NGCallableType,
    SepType,
    WrapType,
    CaseSensitiveType,
    FlagsType
)

from ._validation._validation import _validation
from ._transform._transform import _transform
from ._transform._special_param_conditioner import _special_param_conditioner
from ..__shared._transform._map_X_to_list import _map_X_to_list

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)

from ....base._copy_X import copy_X



class NGramMerger(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Join specified adjacent words into an N-gram unit, to be handled
    as a single "word".

    Sometimes in text analytics it makes sense to work with a block of
    words as a single unit rather than as stand-alone words. Perhaps you
    have a project where you need to analyze the frequency of certain
    occupations or terms across hundreds of thousands of resumes. After
    starting your analysis, you realize that terms like 'process' and
    'engineer' or 'executive' and 'assistant' almost always seem to be
    with each other. So you decide that it might be meaningful to conduct
    your analysis as if those terms were a single unit.

    That's where `NGramMerger` comes in. `NGramMerger` (NGM) is a tool
    that finds specified series of adjacent words (n-grams) and joins
    them to create a single contiguous string.

    NGM accepts n-gram patterns in Python sequences passed to the `ngrams`
    parameter. In each position of the n-gram sequence(s), specify the
    whole-string pattern for each individual string to be searched for
    in your text. NGM always looks for full matches against tokens, it
    does not do partial matches. Valid examples of NGM n-grams are
    [('three', 'blind', 'mice')] and [('a', 'b'), ('1', '2', '3', '4')].

    The search for n-grams can be done using literal strings or regular
    expressions. For those of you who do not know regex, you can safely
    ignore any references to flags, re.compile, or re.Pattern, and just
    use literal strings. The examples above show literal strings. Provide
    literal strings and/or re.compile objects containing your regex
    patterns intended to match full strings. DO NOT PASS A REGEX PATTERN
    AS A LITERAL STRING. YOU WILL NOT GET THE CORRECT RESULT. ALWAYS
    PASS REGEX PATTERNS IN A re.compile OBJECT. DO NOT ESCAPE LITERAL
    STRINGS, NGM WILL DO THAT FOR YOU. If you don't know what any of
    that means, then you don't need to worry about it.

    N-gram searches always default to case-sensitive, but can be made
    to be case-insensitive. You can globally set this behavior via the
    `case_sensitive` parameter. For those of you that know regex, you
    can also put flags in the re.compile objects passed to `ngrams`, or
    flags can be set globally via `flags`. Case-sensitivity is generally
    controlled by `case_sensitive` but IGNORECASE flags passed via
    re.compile objects or `flags` will ALWAYS overrule `case_sensitive`.

    NGM works from top-to-bottom and left-to-right across the data,
    using a forward-greedy approach to merging n-grams. All pattern
    matches are mutually exclusive. Overlapping match patterns are not
    acknowledged. When NGM finds a pattern match, it will immediately
    jump to the next word AFTER the pattern, not the next word within
    the pattern. For example, if you passed an n-gram pattern of
    [('BACON', 'BACON')], and in the text body there is a line that
    contains ...'BACON', 'BACON', 'BACON', ... NGM will apply the n-gram
    as 'BACON_BACON', 'BACON'. This aspect of NGM's operation cannot be
    changed.

    NGM is able to wrap across the beginnings and ends of lines, if you
    desire. This can be toggled with `wrap`. If you do not want NGM to
    look for and join n-grams across the end of one line into the
    beginning of another, set this parameter to False (the default).
    When True, NGM will look for matches as if there is no break between
    the two lines. When allowed and an n-gram match is found across 2
    lines, the joined n-gram is put into the line where the match BEGAN.
    For example, if an n-gram match is found starting at the end of line
    724 and ends in the beginning of line 725, the joined n-gram will
    go at the end of line 724 and the respective words in line 725 will
    be removed.

    When using wrapped searches, the same forward-greedy method discussed
    above is applied. Consider, for example, a case where a pattern match
    exists at the end of one line and into the next line, but in the next
    line there is an overlapping match. NGM will apply the wrapped match
    first because it is first in the working order, and consume the words
    out of the overlap, destroying the second matching pattern.

    NGM only looks for wrapped n-grams across 2 lines, no more. Consider
    the case where you have text that is one word per line, and you are
    looking for a pattern like [('ONE', 'TWO', 'THREE')]. NGM will not
    find a match for this across 3 lines. The way to match this n-gram
    would be 1) put all your tokens on one line, or 2) make 2 passes.
    On the first pass look for the n-gram [('ONE', 'TWO')], then on the
    second pass look for the n-gram [('ONE_TWO', 'THREE')].

    NGM does not necessarily run your n-grams in the given order. To
    prevent conflicts, NGM runs the n-gram patterns in descending order
    of length, that is, the longest n-gram is run first and the shortest
    n-gram is run last. For n-grams that are the same length, NGM runs
    them in the order that they were entered in `ngrams`. If you would
    like to impose another n-gram run order hierarchy, you can manipulate
    the order in which NGM sees the n-grams by setting the n-grams
    piecemeal via :meth:`set_params`. Instantiate with your preferred
    n-grams, pass the data to :meth:`transform`, and keep the processed
    data in memory. Then use `set_params` to set the lesser-preferred
    n-grams and pass the processed data to `transform` again.

    NGM affords you some control over how the n-grams are merged in the
    text body. There are two parameters that control this, `sep` and
    `ngcallable`. `ngcallable` allows you to pass a function that takes
    a variable-length list of strings and returns a single string. `sep`
    will simply concatenate the words in the matching pattern with the
    separator that you choose. If you pass neither, i.e. the NGM default
    parameters are not overriden by the user at instantiation, NGM will
    default to concatenating the words in the matching pattern with a '_'
    separator. In short, NGM merges words that match n-gram patterns
    using the following hierarchy:
    given callable > given separator > default separator.

    If no parameters are passed, i.e., all parameters are left to
    their default values at instantiation, then NGM does a no-op on
    the n-gram search. If `ngrams` is left to the default value of None,
    but `remove_empty_rows` is set to True, NGM will still remove any
    empty rows in your data if your data was passed with empty rows in
    it.

    NGM should only be used on highly processed data. NGM should not be
    the first (or even near the first) step in a complex text wrangling
    workflow. This should be one of the last steps. An example of a
    text wrangling workflow could be: TextReplacer > TextSplitter >
    TextNormalizer > TextRemover > TextLookup > StopRemover > NGramMerger.

    NGM requires (possibly ragged) 2D data formats. The data should be
    processed at least to the point that you are able to split your data
    into tokens. (If you have 1D data and know what your separators are
    as either string literal or regex patterns, use :class:`TextSplitter`
    to convert your data to 2D before using NGM.) Accepted 2D objects
    include Python list/tuple of lists/tuples, numpy arrays, pandas
    dataframes, and polars dataframes. Results are always returned as a
    Python list of lists of strings.

    NGM is a full-fledged scikit-style transformer. It has functional
    `get_params`, `set_params`, `transform`, and `fit_transform` methods.
    It also has `partial_fit`, `fit`, and `score` methods, which are
    no-ops. NGM technically does not need to be fit because it already
    knows everything it needs to do transformations from the parameters.
    These no-op methods are available to fulfill the scikit transformer
    API and make NGM suitable for incorporation into larger workflows,
    such as pipelines and dask_ml wrappers.

    Because NGM doesn't need any information from :meth:`partial_fit`
    and :meth:`fit`, it is technically always in a 'fitted' state and
    ready to transform data. Checks for fittedness will always return
    True.

    NGM has 2 attributes which are only available after data has been
    passed to `transform`. :attr:`n_rows_` is the number of rows of
    text seen in the original data, which may not be equal to the number
    of rows in the outputted data. :attr:`row_support_` is a 1D boolean
    vector that indicates which rows were kept (True) and which
    rows were removed (False) from the data during transform. The only
    way for an entry to become False (i.e. a row was removed) is if
    `remove_empty_rows` is True and there were empty rows in the data
    originally passed, or `wrap` is also True and all the strings on one
    row are merged into an n-gram at the end of the line above it.
    `n_rows_` must equal the number of entries in `row_support_`.

    Parameters
    ----------
    ngrams : NGramsType, default = None
        A sequence of sequences, where each inner sequence holds a series
        of string literals and/or re.compile objects that specify an
        n-gram. Cannot be empty, and cannot have any n-gram patterns
        with less than 2 entries.
    ngcallable : NGCallableType, default = None
        A callable applied to word sequences that match an n-gram to
        produce a single contiguous string sequence.
    sep : str | None, default = None
        The separator that joins words that match an n-gram. This is
        overriden when a callable is passed to `ngcallable`.
    wrap : bool default = False
        Whether to look for pattern matches across the end of one line
        and into the beginning of the next line.
    case_sensitive : bool, default = True
        Global case-sensitivity setting. If True (the default) then all
        searches are case-sensitive. If False, NGM will look for matches
        regardless of case. This setting is overriden when IGNORECASE
        flags are passed in re.compile objects or to `flags`.
    remove_empty_rows : bool, default = False
        Whether to delete any empty rows that may occur during the n-gram
        merging process. A row could only become empty if `wrap` is True
        or the data was passed with an empty row already in it.
    flags : int | None, default = None
        The global flags value(s) applied to the n-gram search. Must be
        None or an integer. The values of the integers are not validated
        for legitimacy, any exceptions would be raised by `re.fullmatch`.
        An IGNORECASE flag passed here will override `case_sensitive`.

    Attributes
    ----------
    n_rows_
    row_support_

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[Sequence[str]]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.DataFrame

    PolarsTypes:
        polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[list[str]]

    NGramsType:
        Sequence[Sequence[str | re.Pattern[str]]] | None

    NGramsWipType:
        list[tuple[re.Pattern[str], ...]] | None

    NGCallableType:
        Callable[[list[str]], str] | None

    SepType:
        str | None

    WrapType:
        bool

    CaseSensitiveType:
        bool

    RemoveEmptyRowsType:
        bool

    FlagsType:
        int | None

    Examples
    --------
    >>> from pybear.feature_extraction.text import NGramMerger as NGM
    >>> trfm = NGM(ngrams=(('NEW', 'YORK', 'CITY'), ('NEW', 'YORK')))
    >>> X = [
    ...   ['UNITED', 'NATIONS', 'HEADQUARTERS'],
    ...   ['405', 'EAST', '42ND', 'STREET'],
    ...   ['NEW', 'YORK', 'CITY', 'NEW', 'YORK', '10017', 'USA']
    ... ]
    >>> out = trfm.fit_transform(X)
    >>> for line in out:
    ...   print(line)
    ['UNITED', 'NATIONS', 'HEADQUARTERS']
    ['405', 'EAST', '42ND', 'STREET']
    ['NEW_YORK_CITY', 'NEW_YORK', '10017', 'USA']
    >>> # Change the separator to '@'
    >>> trfm.set_params(sep='@')
    NGramMerger(ngrams=(('NEW', 'YORK', 'CITY'), ('NEW', 'YORK')), sep='@')
    >>> out = trfm.fit_transform(X)
    >>> for line in out:
    ...   print(line)
    ['UNITED', 'NATIONS', 'HEADQUARTERS']
    ['405', 'EAST', '42ND', 'STREET']
    ['NEW@YORK@CITY', 'NEW@YORK', '10017', 'USA']

    """


    def __init__(
        self,
        *,
        ngrams:NGramsType = None,
        ngcallable:NGCallableType = None,
        sep:SepType = None,
        wrap:WrapType = False,
        case_sensitive:CaseSensitiveType = True,
        remove_empty_rows:bool = False,
        flags:FlagsType = None
    ) -> None:
        """Initialize the NGramMerger instance."""

        self.ngrams = ngrams
        self.ngcallable = ngcallable
        self.sep = sep
        self.wrap = wrap
        self.case_sensitive = case_sensitive
        self.remove_empty_rows = remove_empty_rows
        self.flags = flags


    @property
    def n_rows_(self) -> int:
        """Get the `n_rows_` attribute.

        The number of rows in the data passed to :meth:`transform`.
        This reflects the data that is passed, not the data that is
        returned, which may not necessarily have the same number of
        rows as the original data. The number of rows returned could
        be less than the number passed if `remove_empty_rows` is True
        and there was an empty row already in the data when it was
        passed, or `wrap` is also True and all the strings on one line
        were merged into an n-gram on the previous line. `n_rows_` only
        reflects the last batch of data passed; it is not cumulative.
        This attribute is only exposed after data is passed to
        `transform`.

        Returns
        -------
        n_rows_ : int
            The number of rows in the data passed to `transform`.

        """

        return self._n_rows


    @property
    def row_support_(self) -> npt.NDArray[bool]:
        """Get the `row_support_` attribute.

        A boolean 1D numpy vector of shape (`n_rows_`, ) indicating
        which rows of the data were kept (True) or removed (False)
        during transform.

        Only available if a transform has been performed, and only
        reflects the results of the last transform done.

        The only way an entry in this vector could become False (i.e.
        a row was removed) is if `remove_empty_rows` is True and an
        empty row was already in the data when passed, or `wrap` is also
        True and all strings on one line were merged into an n-gram on
        the line above it.

        Returns
        -------
        row_support_ : numpy.ndarray[bool] of shape (n_original_rows, )
            A boolean vector indicating which rows were kept in the data
            during the transform process.

        """

        return self._row_support


    def __pybear_is_fitted__(self) -> bool:
        return True


    # def get_params
    # handled by GetParamsMixin


    # def set_params
    # handled by SetParamsMixin


    # def fit_transform
    # handled by FitTransformMixin


    def reset(self) -> Self:
        """No-op reset method.

        Returns
        -------
        self : object
            The reset `NGramMerger` instance.

        """

        return self


    def get_metadata_routing(self):
        """get_metadata_routing is not implemented in NGramMerger."""
        raise NotImplementedError(
            f"'get_metadata_routing' is not implemented in NGramMerger."
        )


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op batch-wise fit operation.

        Parameters
        ----------
        X : XContainer
            The data. Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `NGramMerger` instance.

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
            The data. Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `NGramMerger` instance.

        """

        self.reset()

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Merge n-grams in a (possibly ragged) 2D array-like of strings.

        Parameters
        ----------
        X : XContainer
            The data.
        copy : bool, default=False
            Whether to directly operate on the passed `X` or on a
            deepcopy of `X`.

        Returns
        -------
        X_tr : list[list[str]]
            The data with all matching n-gram patterns replaced with
            contiguous strings.

        """

        check_is_fitted(self)

        _validation(
            X,
            self.ngrams,
            self.ngcallable,
            self.sep,
            self.wrap,
            self.case_sensitive,
            self.remove_empty_rows,
            self.flags
        )

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr: XWipContainer = _map_X_to_list(X_tr)

        self._n_rows: int = len(X_tr)

        _ngrams_wip: NGramsWipType = _special_param_conditioner(
            self.ngrams,
            self.case_sensitive,
            self.flags
        )

        # WHAT SUBMODULES ARE CALLED AND WHERE
        # _transform
        #     _match_finder
        #     _wrap_manager
        #         _manage_wrap_idxs
        #         _match_finder
        #         _get_wrap_match_idxs
        #         _replacer (only one that uses sep)
        #     _replacer (only one that uses sep)

        X_tr, self._row_support = _transform(
            X_tr, _ngrams_wip, self.ngcallable, self.sep, self.wrap,
            self.remove_empty_rows
        )

        return X_tr


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





