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
    OverallStatisticsType
)

import numbers
import re

import pandas as pd
import polars as pl

from ._validation._validation import _validation
from ._validation._overall_statistics import _val_overall_statistics
from ._validation._uniques import _val_uniques
from ._validation._string_frequency import _val_string_frequency
from ._validation._startswith_frequency import _val_startswith_frequency
from ._validation._character_frequency import _val_character_frequency

from ._partial_fit._build_overall_statistics import _build_overall_statistics
from ._partial_fit._merge_overall_statistics import _merge_overall_statistics
from ._partial_fit._build_string_frequency import _build_string_frequency
from ._partial_fit._merge_string_frequency import _merge_string_frequency
from ._partial_fit._build_startswith_frequency import _build_startswith_frequency
from ._partial_fit._merge_startswith_frequency import _merge_startswith_frequency
from ._partial_fit._build_character_frequency import _build_character_frequency
from ._partial_fit._merge_character_frequency import _merge_character_frequency

from ._print._overall_statistics import _print_overall_statistics
from ._print._startswith_frequency import _print_startswith_frequency
from ._print._string_frequency import _print_string_frequency
from ._print._character_frequency import _print_character_frequency
from ._print._longest_strings import _print_longest_strings
from ._print._shortest_strings import _print_shortest_strings

from ._get._get_longest_strings import _get_longest_strings
from ._get._get_shortest_strings import _get_shortest_strings

from ._lookup._lookup_substring import _lookup_substring
from ._lookup._lookup_string import _lookup_string

from ....base._check_1D_str_sequence import check_1D_str_sequence

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    check_is_fitted
)



class TextStatistics(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin
):
    """Generate summary information about the strings and characters in
    text data.

    Statistics include:

    - size (number of strings fitted)

    - unique strings count

    - average length and standard deviation of all strings

    - max string length

    - min string length

    - string frequencies

    - 'starts with' frequency

    - single character frequency

    - longest strings

    - shortest strings

    `TextStatistics` (TS) has 2 functional scikit-style transformer
    methods, :meth:`fit` and :meth:`partial_fit`. The :meth:`transform`
    method is a no-op because TS does not mutate data, it only reports
    information about the strings and characters in it.

    `TextStatistics` can do one-shot training on a single batch of data
    via `fit`, or can be trained on multiple batches via `partial_fit`.
    The `fit` method resets the instance with each call, that is, all
    information held within the instance prior is deleted and the new
    fit information repopulates. The `partial_fit` method, however, does
    not reset and accumulates information across all batches seen. This
    makes TS suitable for streaming data and batch-wise training, such
    as with a dask_ml Incremental wrapper.

    TS does have other methods that allow access to certain functionality,
    such as conveniently printing summary information from attributes to
    screen. See the methods section of the docs.

    TS accepts 1D list-likes or (possibly ragged) 2D array-likes
    containing only strings. This includes Python lists, sets, and
    tuples, numpy vectors, pandas series, polars series, 2D Python
    built-ins, numpy arrays, pandas dataframes, and polars dataframes.

    TS is case-sensitive during fitting, always. This is a design choice
    so that users who want to differentiate between the same characters
    in different cases can do so. If you want your strings to be treated
    in a non-case-sensitive way, normalize the case of your strings prior
    to fitting on TS. (hint: use pybear :class:`TextNormalizer`).

    The TS class takes only one parameter, `store_uniques`. More on
    that below. The `store_uniques` parameter is intended to be set
    once at instantiation and not changed thereafter. This protects
    the integrity of the reported information. As such, TS has a
    no-op :meth:`set_params` method. Advanced users may access and set
    the `store_uniques` parameter directly on the instance, but the
    impacts of doing so in the midst of a series of partial fits or
    afterward is not tested. pybear does not recommend this technique;
    create a new instance with the desired setting and fit your data
    again. The TS :meth:`get_params` method is fully functional.

    When the `store_uniques` parameter is True, the TS instance retains
    a dictionary of all the unique strings it has seen during fitting
    and their frequencies. In this case, TS is able to yield all the
    information that it is designed to collect. This is ideal for
    situations with a 'small' number of unique strings, such as when
    fitting on cleaned tokens, where a recurrence of a unique will simply
    increment the count of that unique in the dictionary instead of
    creating a new entry.

    When `store_uniques` is False, however, the unique strings seen
    during fitting are not stored. In this case, the memory footprint
    of the TS instance will not grow linearly with the number of unique
    strings seen during fitting. This enables TS to fit on practially
    unlimited amounts of text data. This is ideal for situations where
    the individual strings being fit are phrases, sentences, or even
    entire books. This comes at cost, though, because some reporting
    capability is lost.

    Functionality available when `store_uniques` is False is size
    (the number of strings seen by the TS instance), average length,
    standard deviation of length, maximum length, minimum length, overall
    character frequency, and first character frequency. Functionality
    lost includes the unique strings themselves as would otherwise be
    available through :attr:`uniques_` and :attr:`string_frequency_`,
    and information about longest string and shortest string. Methods
    whose information reporting is impacted include :meth:`lookup_string`
    and :meth:`lookup_substring`, as well as the associated printing
    methods.

    Parameters
    ----------
    store_uniques : bool, default = True
        Whether to retain the unique strings seen by the `TextStatistics`
        instance in memory. If True, all attributes and print methods
        are fully informative. If False, the :attr:`string_frequency_`
        and :attr:`uniques_` attributes are always empty, and functionality
        that depends on these attributes have reduced capability.

    Attributes
    ----------
    size_
    uniques_
    overall_statistics_
    string_frequency_
    startswith_frequency_
    character_frequency_

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextStatistics as TS
    >>> STRINGS = ['I am Sam', 'Sam I am', 'That Sam-I-am!',
    ...    'That Sam-I-am!', 'I do not like that Sam-I-am!']
    >>> trfm = TS(store_uniques=True)
    >>> trfm.fit(STRINGS)
    TextStatistics()
    >>> trfm.size_
    5
    >>> trfm.overall_statistics_['max_length']
    28
    >>> trfm.overall_statistics_['average_length']
    14.4

    >>> STRINGS = ['a', 'a', 'b', 'c', 'c', 'c', 'd', 'd', 'e', 'f', 'f']
    >>> trfm = TextStatistics()
    >>> trfm.fit(STRINGS)
    TextStatistics()
    >>> trfm.size_
    11
    >>> trfm.string_frequency_
    {'a': 2, 'b': 1, 'c': 3, 'd': 2, 'e': 1, 'f': 2}
    >>> trfm.uniques_
    ['a', 'b', 'c', 'd', 'e', 'f']
    >>> trfm.overall_statistics_['max_length']
    1
    >>> trfm.character_frequency_
    {'a': 2, 'b': 1, 'c': 3, 'd': 2, 'e': 1, 'f': 2}

    """


    _lp: int = 5
    _rp: int = 15


    def __init__(
        self,
        *,
        store_uniques:bool = True
    ) -> None:
        """Initialize the TextStatistics instance."""

        self.store_uniques = store_uniques


    # @properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
    @property
    def size_(self) -> int:
        """Get the `size_` attribute.

        The number of strings fitted on the `TextStatistics` instance.

        Returns
        -------
        size : int
            The number of strings fitted on the `TextStatistics` instance.

        """

        check_is_fitted(self)

        return self.overall_statistics_['size']


    @property
    def uniques_(self) -> list[str]:
        """Get the `uniques_` attribute.

        A 1D list of the unique strings fitted on the `TextStatistics`
        instance. If `store_uniques` is False, this will always be empty.

        Returns
        -------
        uniques_ : list[str]
            A 1D list of the unique strings seen during fitting.

        """

        check_is_fitted(self)

        uniques = list(self.string_frequency_.keys())

        _val_uniques(uniques)

        return uniques


    @property
    def overall_statistics_(self) -> dict[str, numbers.Real]:
        """Get the `overall_statistics_` attribute.

        A dictionary that holds information about all the strings fitted
        on the `TextStatistics` instance. Available statistics are size
        (number of strings seen during fitting), uniques count, average
        string length, standard deviation of string length, maximum
        string length, and minimum string length. If `store_uniques` is
        False, the `uniques_count` field will always be zero.

        Returns
        -------
        overall_statistics_ : dict[str, numbers.Real]
            Summary information about all the strings seen during fit.

        """

        check_is_fitted(self)

        return self._overall_statistics


    @property
    def string_frequency_(self) -> dict[str, int]:
        """Get the `string_frequency_` attribute.

        A dictionary that holds the unique strings and the respective
        number of occurrences seen during fitting. If the `store_uniques`
        parameter is False, this will always be empty.

        Returns
        -------
        string_frequency_ : dict[str, int]
            The unique strings seen during fitting and their frequency.

        """

        check_is_fitted(self)

        return self._string_frequency


    @property
    def startswith_frequency_(self) -> dict[str, int]:
        """Get the `startswith_frequency_` attribute.

        A dictionary that holds the first characters and their
        frequencies in the first position for all the strings fitted on
        the `TextStatistics` instance.

        Returns
        -------
        startswith_frequency_ : dict[str, int]
            The first characters of every string seen during fit and
            their respective frequencies.

        """

        check_is_fitted(self)

        return self._startswith_frequency


    @property
    def character_frequency_(self) -> dict[str, int]:
        """Get the `character_frequency_` attribute.

        A dictionary that holds all the unique single characters
        and their frequencies for all the strings fitted on the
        `TextStatistics` instance.

        Returns
        -------
        character_frequency_ : dict[str, int]
            The counts of every character seen during fitting.

        """

        check_is_fitted(self)

        return self._character_frequency

    # END @properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def __pybear_is_fitted__(self) -> bool:
        return hasattr(self, '_string_frequency')


    def _reset(self) -> Self:
        """Reset the TextStatistics instance to the not-fitted state.

        Remove all objects that hold information from any fits that may
        have been performed on the instance.

        Returns
        -------
        self : object
            The `TextStatistics` instance.

        """

        if hasattr(self, '_string_frequency'):
            delattr(self, '_string_frequency')
        if hasattr(self, '_overall_statistics'):
            delattr(self, '_overall_statistics')
        if hasattr(self, '_startswith_frequency'):
            delattr(self, '_startswith_frequency')
        if hasattr(self, '_character_frequency'):
            delattr(self, '_character_frequency')

        return self


    # def get_params() - inherited from GetParamsMixin

    # def fit_transform() - inherited from FitTransformMixin

    def set_params(self, **params) -> Self:
        """No-op `set_params` method.

        Returns
        -------
        self : object
            The `TextStatistics` instance.

        """

        return self


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Batch-wise fitting of the `TextStatistics` instance.

        The instance is not reset and information about the strings in
        the batches of training data is accretive.

        Parameters
        ----------
        X : XContainer
            A 1D list-like or 2D array-like of strings to report
            statistics for. Can be empty. Strings do not need to be in
            the pybear :class:`Lexicon`.
        y : Any, default = None
            A target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TestStatistics` instance.

        """


        _validation(X, self.store_uniques)

        # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # 1D/2D redirector -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # we know X is legit 1D or 2D
        try:
            check_1D_str_sequence(X)
            # just flow thru to 1D handling, which is everything below this
            pass
        except:
            # must be 2D
            # get each row out 1 by 1 and pass recursively to partial_fit
            _n_rows = X.shape[0] if hasattr(X, 'shape') else len(X)
            for _row_idx in range(_n_rows):
                if isinstance(X, pd.DataFrame):
                    _line = X.values[_row_idx]
                elif isinstance(X, pl.DataFrame):
                    _line = X.row(_row_idx)
                else:
                    _line = X[_row_idx]

                self.partial_fit(_line)

            # need to skip out so 2D X doesnt get send down after finishing
            # the recursion
            return self
        # END 1D/2D redirector -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # SKIP OUT FOR EMPTY -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # if 1D X empty, just skip out, it has nothing to contribute
        # to any statistics, but sure will crash a lot of stuff for
        # zero reduction operation
        if len(X) == 0:
            # these assignments will make the instance fitted even if
            # it only saw empty data
            self._string_frequency = getattr(self, '_string_frequency', {})
            self._startswith_frequency = getattr(self, '_startswith_frequency', {})
            self._character_frequency = getattr(self, '_character_frequency', {})
            self._overall_statistics = getattr(self, '_overall_statistics', {})

            return self
        # END SKIP OUT FOR EMPTY -- -- -- -- -- -- -- -- -- -- -- -- --

        # string_frequency_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # this must be first
        _current_string_frequency: dict[str, int] = \
            _build_string_frequency(
                X,
                case_sensitive=True
            )

        if self.store_uniques:
            self._string_frequency: dict[str, int] = \
                _merge_string_frequency(
                    _current_string_frequency,
                    getattr(self, '_string_frequency', {})
                )
        else:
            self._string_frequency = {}

        _val_string_frequency(self._string_frequency)
        # END string_frequency_ -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # startswith_frequency -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _current_startswith_frequency: dict[str, int] = \
            _build_startswith_frequency(
                _current_string_frequency
            )

        self._startswith_frequency: dict[str, int] = \
            _merge_startswith_frequency(
                _current_startswith_frequency,
                getattr(self, '_startswith_frequency', {})
            )

        del _current_startswith_frequency

        _val_startswith_frequency(self._startswith_frequency)
        # END startswith_frequency -- -- -- -- -- -- -- -- -- -- -- --

        # character_frequency -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _current_character_frequency: dict[str, int] = \
            _build_character_frequency(
                _current_string_frequency
            )

        self._character_frequency: dict[str, int] = \
            _merge_character_frequency(
                _current_character_frequency,
                getattr(self, '_character_frequency', {})
            )

        del _current_string_frequency
        del _current_character_frequency

        _val_character_frequency(self._character_frequency)
        # END character_frequency -- -- -- -- -- -- -- -- -- -- -- -- --

        # overall_statistics_ -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _current_overall_statistics: OverallStatisticsType = \
            _build_overall_statistics(
                X,
                case_sensitive=False
            )

        if not self.store_uniques:
            _current_overall_statistics['uniques_count'] = 0

        self._overall_statistics: OverallStatisticsType = \
            _merge_overall_statistics(
                _current_overall_statistics,
                getattr(self, '_overall_statistics', {}),
                _len_uniques=len(self.uniques_)
            )

        _val_overall_statistics(self._overall_statistics)
        # END overall_statistics_ -- -- -- -- -- -- -- -- -- -- -- -- --

        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Single batch training of the `TextStatistics` instance.
        The instance is reset and the only information retained is
        that associated with this single batch of data.

        Parameters
        ----------
        X : XContainer
            A 1D list-like or 2D array-like of strings to report
            statistics for. Can be empty. Strings do not need to be in
            the pybear :class:`Lexicon`.
        y : Any, default = None
            A target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextStatistics` instance.

        """

        self._reset()

        return self.partial_fit(X)


    def transform(self, X: XContainer) -> XContainer:
        """A no-op transform method for data processing scenarios that
        may require the transform method.

        `X` is returned as given.

        Parameters
        ----------
        X : XContainer
            The data. Ignored.

        Returns
        -------
        X : XContainer
            The original, unchanged, data.

        """

        check_is_fitted(self)

        return X


    # OTHER METHODS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    def print_overall_statistics(self) -> None:
        """Print :attr:`overall_statistics_` to screen.

        The `uniques_count` field will always be zero if `store_uniques`
        is False.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_overall_statistics(self._overall_statistics, self._lp, self._rp)


    def print_startswith_frequency(self) -> None:
        """Print the :attr:`startswith_frequency_` attribute to screen.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_startswith_frequency(
            self._startswith_frequency, self._lp, self._rp
        )


    def print_character_frequency(self) -> None:
        """Print the :attr:`character_frequency_` attribute to screen.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_character_frequency(self._character_frequency, self._lp, self._rp)


    def print_string_frequency(
        self,
        n:int = 10
    ) -> None:
        """Print the :attr:`string_frequency_` attribute to screen.

        Only available if `store_uniques` is True. If False, uniques
        are not available for display to screen.

        Parameters
        ----------
        n : int, default = 10
            The number of the most frequent strings to print to screen.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_string_frequency(self._string_frequency, self._lp, self._rp, n)


    # longest_strings -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def get_longest_strings(
        self,
        n: int = 10
    ) -> dict[str, int]:
        """The longest strings seen by the `TextStatistics` instance
        during fitting.

        Only available if `store_uniques` is True. If False, the uniques
        seen during fitting are not available and an empty dictionary is
        always returned.

        Parameters
        ----------
        n : int, default = 10
            The number of the top longest strings to return.

        Returns
        -------
        dict[str, int]:
            The top 'n' longest strings seen by the `TextStatistics`
            instance during fitting. This will always be empty if
            `store_uniques` is False.

        """

        check_is_fitted(self)

        __ = _get_longest_strings(self._string_frequency, n=n)

        # _val_string_frequency will work for this
        _val_string_frequency(__)

        return __


    def print_longest_strings(
        self,
        n: int = 10
    ) -> None:
        """Print the longest strings in :attr:`string_frequency_` to
        screen.

        Only available if `store_uniques` is True. If False, uniques are
        not available for display to screen.

        Parameters
        ----------
        n : int, default = 10
            The number of top longest strings to print to screen.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_longest_strings(self._string_frequency, self._lp, self._rp, n)
    # END longest_strings -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # shortest_strings -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def get_shortest_strings(
        self,
        n: int = 10
    ) -> dict[str, int]:
        """The shortest strings seen by the `TextStatistics` instance
        during fitting.

        Only available if `store_uniques` is True. If False, the uniques
        seen during fitting are not available and an empty dictionary is
        always returned.

        Parameters
        ----------
        n : int, default = 10
            The number of the top shortest strings to return.

        Returns
        -------
        dict[str, int]:
            The top 'n' shortest strings seen by the `TextStatistics`
            instance during fitting. This will always be empty if
            `store_uniques` is False.

        """

        check_is_fitted(self)

        __ = _get_shortest_strings(self._string_frequency, n=n)

        # _val_string_frequency will work for this
        _val_string_frequency(__)

        return __


    def print_shortest_strings(
        self,
        n: int = 10
    ) -> None:
        """Print the shortest strings in :attr:`string_frequency_` to
        screen.

        Only available if `store_uniques` is True. If False, uniques are
        not available for display to screen.

        Parameters
        ----------
        n : int, default = 10
            The number of shortest strings to print to screen.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        _print_shortest_strings(self._string_frequency, self._lp, self._rp, n)
    # END shortest_strings -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def lookup_substring(
        self,
        pattern:str | re.Pattern[str],
        case_sensitive:bool = True
    ) -> list[str]:
        """Use string literals or regular expressions to look for
        substring matches in the fitted words.

        `pattern` can be a literal string or a regular expression in a
        re.compile object.

        If re.compile object is passed, `case_sensitive` is ignored and
        the fitted words are searched with the compile object as given.
        If string is passed and `case_sensitive` is True, search for an
        exact substring match of the passed string; if `case_sensitive`
        is False, search without regard to case.

        If a substring match is not found, return an empty list. If
        matches are found, return a 1D list of the matches in their
        original form from the fitted data.

        This is only available if `store_uniques` is True. If False, the
        unique strings that have been fitted on the TS instance are not
        retained therefore cannot be searched, and an empty list is
        always returned.

        Parameters
        ----------
        pattern : str | re.Pattern[str]
            Character sequence or regular expression in a re.compile
            object to be looked up against the strings fitted on the
            `TextStatistics` instance.
        case_sensitive : bool, default = True
            Ignored if a re.compile object is passed to `pattern`. If
            True, search for the exact pattern in the fitted data. If
            False, ignore the case of words in :attr:`uniques` while
            performing the search.

        Returns
        -------
        list[str]:
            List of all strings in the fitted data that contain the given
            character substring. Returns an empty list if there are no
            matches.

        """

        check_is_fitted(self)

        return _lookup_substring(pattern, self.uniques_, case_sensitive)


    def lookup_string(
        self,
        pattern:str | re.Pattern[str],
        case_sensitive:bool = True
    ) -> list[str]:
        """Use string literals or regular expressions to look for whole
        string matches (not substrings) in the fitted words.

        `pattern` can be a literal string or a regular expression in a
        re.compile object.

        If re.compile object is passed, `case_sensitive` is ignored and
        the fitted words are searched with the compile object as given.
        If string literal is passed and `case_sensitive` is True, search
        for an exact match of the whole passed string; if `case_sensitive`
        is False, search without regard to case.

        If an exact match is not found, return an empty list. If matches
        are found, return a 1D list of the matches in their original
        form from the fitted data.

        This is only available if `store_uniques` is True. If False, the
        unique strings that have been fitted on the TS instance are not
        retained therefore cannot be searched, and an empty list is
        always returned.

        Parameters
        ----------
        pattern : str | re.Pattern[str]
            Character sequence or regular expression in a re.compile
            object to be looked up against the strings fitted on the
            `TextStatistics` instance.
        case_sensitive : bool, default = True
            Ignored if a re.compile object is passed to `pattern`. If
            True, search for the exact pattern in the fitted data. If
            False, ignore the case of the words in :attr:`uniques_`
            while performing the search.

        Returns
        -------
        list[str]:
            If there are any matches, return the matching string(s) from
            the originally fitted data in a 1D list; if there are no
            matches, return an empty list.

        """


        check_is_fitted(self)

        return _lookup_string(pattern, self.uniques_, case_sensitive)


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """No-op score method.

        Dummy method to spoof dask Incremental and ParallelPostFit
        wrappers. Verified must be here for dask wrappers.

        Parameters
        ----------
        X : Any
            The data. Ignored.
        y : Any, default = None
            The target for the data. Ignored.

        """

        check_is_fitted(self)

        return









