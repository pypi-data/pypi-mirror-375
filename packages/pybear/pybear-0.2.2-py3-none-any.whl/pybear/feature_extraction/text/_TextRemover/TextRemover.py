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
    RemoveType,
    WipRemoveType,
    CaseSensitiveType,
    FlagsType,
    RowSupportType
)

import re

import numpy as np

from ._regexp_1D_core import _regexp_1D_core
from ._validation import _validation

from ..__shared._transform._map_X_to_list import _map_X_to_list
from ..__shared._param_conditioner._param_conditioner import _param_conditioner

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)

from ....base._copy_X import copy_X



class TextRemover(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Remove full strings (not substrings) from text data.

    Identify full strings to remove by literal string equality or by
    regular expression `fullmatch`. Remove any and all matches completely
    from the data.

    One particularly useful application is to take out empty or gibberish
    strings in data read in from a file. Another is to remove strings
    that have become empty or have only non-alphanumeric characters after
    replacing values (see pybear :class:`TextReplacer`).

    `TextRemover` (TR) always looks for matches against entire strings,
    it does not do partial matches. You can tell TR what strings to
    remove with literal strings or regular expressions in re.compile
    objects passed to `remove`. Pass literal strings or re.compile
    objects that are intended to match entire words. DO NOT PASS A REGEX
    PATTERN AS A LITERAL STRING. YOU WILL NOT GET THE CORRECT RESULT.
    ALWAYS PASS REGEX PATTERNS IN A re.compile OBJECT. DO NOT ESCAPE
    LITERAL STRINGS, TextRemover WILL DO THAT FOR YOU. If you don't know
    what any of that means, then you don't need to worry about it.

    TR searches always default to case-sensitive, but can be made to
    be case-insensitive. You can globally set this behavior via the
    `case_sensitive` parameter. For those of you that know regex, you
    can also put flags in the re.compile objects passed to `remove`, or
    flags can be set globally via `flags`. Case-sensitivity is generally
    controlled by `case_sensitive` but IGNORECASE flags passed via
    re.compile objects or `flags` will always overrule `case_sensitive`.

    So why not just use regular literal string matching or `re.fullmatch`
    to find strings and remove them? Unlike those, TR accepts multiple
    patterns to search for and remove. TR can remove multiple strings in
    one call by passing a tuple of literal strings and/or re.compile
    objects to `remove`. But if you need fine-grained control on certain
    rows of data, `remove`, `case_sensitive`, and/or `flags` can be
    passed as lists indicating specific instructions for individual rows.
    When any of these are passed as a list, the number of entries in the
    list must equal the number of rows in the data. What is allowed to
    be put in the lists is dictated by the allowed global values for
    each respective parameter.

    `TextRemover` is a full-fledged scikit-style transformer. It has
    fully functional `get_params`, `set_params`, `transform`, and
    `fit_transform` methods. It also has no-op `partial_fit` and `fit`
    methods to allow for integration into larger workflows, like scikit
    pipelines. Technically TR does not need to be fit and is  always in
    a fitted state (any 'is_fitted' checks of an instance will always
    return True) because TR knows everything it needs to know to transform
    data from the parameters. It also has a no-op `score` method
    to allow dask_ml wrappers.

    Accepts 1D list-like and (possibly ragged) 2D array-likes of strings.
    Accepted 1D containers include Python lists, tuples, and sets, numpy
    vectors, pandas series, and polars series. Accepted 2D containers
    include embedded Python sequences, numpy arrays, pandas dataframes,
    and polars dataframes. When passed a 1D list-like, returns a Python
    list of strings. When passed a 2D array-like, returns a Python list
    of Python lists of strings. If you pass your data as a dataframe
    with feature names, the feature names are not preserved.

    By definition, a row is removed from 1D data when an entire string
    is removed. This behavior is unavoidable, in this case `TextRemover`
    must mutate along the example axis. However, the user can control
    this behavior for 2D containers. `remove_empty_rows` is a boolean
    that indicates to TR whether to remove any rows that may have become
    (or may have been given as) empty after removing unwanted strings.
    If True, TR will remove any empty rows from the data and those rows
    will be indicated in the :attr:`row_support_` mask by a False in
    their respective positions. It is possible that empty 1D lists are
    returned. If False, empty rows are not removed from the data.

    TextRemover instances that have undergone a transform operation
    expose 2 attributes. :attr:`n_rows_` is the number of rows in the
    data last passed to `transform`, which may be different from the
    number of rows returned. `row_support_` is a boolean numpy vector
    indicating which rows were kept (True) and which were removed
    (False) fram the data during the last transform. This mask can be
    applied to a target for the data (if any) so that the rows in the
    target match the rows in the data after transform. The length of
    `row_support_` must equal `n_rows_`. Neither of these attributes
    are cumulative, they only reflect the last dataset passed
    to :meth:`transform`.

    Parameters
    ----------
    remove : RemoveType, default = None
        The literal strings or regex patterns to remove from the data.
        When passed as a single literal string or re.compile object,
        that is applied to every string in the data, and every full
        string that matches exactly will be removed. When passed as a
        Python tuple of character strings and/or re.compile objects,
        each pattern is searched against all the strings in the data
        and any exact matches are removed. If passed as a list, the
        number of entries must match the number of rows in `X`, and each
        string, re.compile, or tuple is applied to the corresponding row
        in the data. If any entry in the list is None, the corresponding
        row in the data is ignored.
    case_sensitive : CaseSensitiveType, default = True
        Global setting for case-sensitivity. If True (the default)
        then all searches are case-sensitive. If False, TR will look
        for matches regardless of case. This setting is overriden
        when IGNORECASE flags are passed in re.compile objects or
        to `flags`.
    remove_empty_rows : bool, default = False
        Whether to remove rows that become empty when data is passed in
        a 2D container. This does not apply to 1D data. If True, TR
        will remove any empty rows from the data and that row will be
        indicated in the `row_support_` mask by a False in that position.
        If False, empty rows are not removed from the data.
    flags : FlagsType, default = None
        The flags value(s) for the full string searches. Internally,
        TR does all its searching for strings with `re.fullmatch`,
        therefore flags can be passed whether you are searching for
        literal strings or regex patterns. If you do not know regular
        expressions, then you do not need to worry about this parameter.
        If None, the default flags for `re.fullmatch` are used globally.
        If a single flags object, that is applied globally. If passed
        as a list, the number of entries must match the number of rows
        in the data. Flags objects and Nones in the list follow the
        same rules stated above, but at the row level. If IGNORECASE
        is passed here as a global setting or in a list it overrides
        the `case_sensitive` 'True' setting.

    Attributes
    ----------
    n_rows_
    row_support_

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]] | set[str]

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

    PatternType:
        None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]
    RemoveType:
        PatternType | list[PatternType]

    WipPatternType:
        None | re.Pattern[str] | tuple[re.Pattern[str], ...]
    WipRemoveType:
        WipPatternType | list[WipPatternType]

    CaseSensitiveType:
        bool | list[bool | None]

    RemoveEmptyRowsType:
        bool

    FlagType:
        None | int
    FlagsType:
        FlagType | list[FlagType]

    RowSupportType:
        numpy.ndarray[bool]

    See Also
    --------
    list.remove
    re.fullmatch

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextRemover as TR
    >>> trfm = TR(remove=(' ', ''))
    >>> X = [' ', 'One', 'Two', '', 'Three', ' ']
    >>> trfm.fit_transform(X)
    ['One', 'Two', 'Three']
    >>> trfm.set_params(**{'remove': re.compile('[bcdei]')})
    TextRemover(remove=re.compile('[bcdei]'))
    >>> X = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
    >>> trfm.fit_transform(X)
    [['a'], ['f'], ['g', 'h']]

    """


    def __init__(
        self,
        *,
        remove: RemoveType = None,
        case_sensitive: CaseSensitiveType = True,
        remove_empty_rows: bool = False,
        flags: FlagsType = None
    ) -> None:
        """Initialize the TextRemover instance."""

        self.remove = remove
        self.case_sensitive = case_sensitive
        self.remove_empty_rows = remove_empty_rows
        self.flags = flags


    def __pybear_is_fitted__(self) -> bool:
        return True


    @property
    def n_rows_(self) -> int:
        """Get the `n_rows_` attribute.

        The number of rows in the data passed to :meth:`transform`.
        This reflects the data that is passed, not the data that is
        returned, which may not necessarily have the same number of
        rows as the original data. Only available if a transform has
        been performed, and only reflects the results of the last
        transform done, it is not cumulative.

        Returns
        -------
        n_rows_ : int
            The number of rows in the data passed to transform.

        """

        return self._n_rows


    @property
    def row_support_(self) -> npt.NDArray[bool]:
        """Get the `row_support_` attribute.

        A boolean vector indicating which rows were kept (True) or
        removed (False) during the transform process. Only available
        if a transform has been performed, and only reflects the results
        of the last transform done, it is not cumulative.

        Returns
        -------
        row_support_ : numpy.ndarray[bool]
            A boolean vector indicating which rows were kept in the data
            during the transform process.

        """

        return self._row_support


    def get_metadata_routing(self):
        """metadata routing is not implemented in `TextRemover`."""
        raise NotImplementedError(
            f"metadata routing is not implemented in TextRemover"
        )


    # def get_params
    # from GetParamsMixin


    # def set_params
    # from SetParamsMixin


    # def fit_transform
    # from FitTransformMixin


    def partial_fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """Batch-wise no-op fit operation.

        Parameters
        ----------
        X : XContainer
            The data. Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextRemover` instance.

        """

        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """One-shot no-op fit operation.

        Parameters
        ----------
        X : XContainer
            The data. Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextRemover` instance.

        """

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Remove unwanted strings from the data.

        Parameters
        ----------
        X : XContainer
            The data.
        copy : bool, default=False
            Whether to remove unwanted strings directly from the original
            `X` or from a deepcopy of the original `X`.

        Returns
        -------
        X : XWipContainer
            The data with unwanted strings removed.

        """

        check_is_fitted(self)

        _validation(
            X,
            self.remove,
            self.case_sensitive,
            self.remove_empty_rows,
            self.flags
        )

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr: XWipContainer = _map_X_to_list(X_tr)

        self._n_rows = len(X_tr)

        _rr: WipRemoveType = _param_conditioner(
            self.remove,
            self.case_sensitive,
            self.flags,
            _order_matters=False,
            _n_rows=self._n_rows,
            _name='remove'
        )

        if all(map(isinstance, X_tr, (str for _ in X_tr))):

            X_tr, self._row_support = _regexp_1D_core(X_tr, _rr, _from_2D=False)

        else:
            # must be 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            for _row_idx in range(len(X_tr)):

                # notice the indexer, only need the X_tr component
                X_tr[_row_idx] = _regexp_1D_core(
                    X_tr[_row_idx],
                    _rr[_row_idx] if isinstance(_rr, list) else _rr,
                    _from_2D=True
                )[0]

            self._row_support = np.ones(self._n_rows, dtype=bool)
            if self.remove_empty_rows:
                for _row_idx in range(self._n_rows-1, -1, -1):
                    if len(X_tr[_row_idx]) == 0:
                        X_tr.pop(_row_idx)
                        self._row_support[_row_idx] = False
            # END recursion for 2D -- -- -- -- -- -- -- -- -- -- -- --

        del _rr

        return X_tr


    def score(
        self,
        X: XContainer,
        y: Any = None
    ) -> None:
        """No-op score method to allow wrap by dask_ml wrappers.

        Parameters
        ----------
        X : XContainer
            The data. Ignored.
        y : Any, default=None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        return





