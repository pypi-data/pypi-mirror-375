# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Sequence
)
from typing_extensions import Self
import numpy.typing as npt

from copy import deepcopy

import numpy as np
import pandas as pd
import polars as pl

from ._shared._validation._validation import _validation

from ._shared._transform._auto_word_splitter import _auto_word_splitter
from ._shared._transform._manual_word_splitter import _manual_word_splitter
from ._shared._transform._quasi_auto_word_splitter import _quasi_auto_word_splitter
from ._shared._transform._word_editor import _word_editor

from ._shared._type_aliases import (
    XContainer,
    WipXContainer
)

from ..__shared._transform._map_X_to_list import _map_X_to_list
from ..__shared._utilities._view_text_snippet import view_text_snippet
from ....base._copy_X import copy_X

from ._TextLookupMixin import _TextLookupMixin

from ....base._check_is_fitted import check_is_fitted



class TextLookup(_TextLookupMixin):
    """Handle words in a 2D array-like body of text that are not in the
    pybear `Lexicon`.

    Options include replacing, removing, splitting, or skipping the word,
    or staging it to add to the pybear :class:`Lexicon`.

    TextLookup (TL) has a dual-functionality :meth:`partial_fit` method.
    TL can operate autonomously on your data for a completely hands-free
    experience, or can be driven in a fully interactive process. The
    interactive mode is a menu-driven process that prompts the user for
    a decision about a word that is not in the `Lexicon` and lazily
    stores edits to the data to be applied later during transform.

    TL has a sister module called :class:`TextLookupRealTime` which is
    not a typical scikit-style transformer. TL is more conventional in
    that the learning that takes place for both autonomous and manual
    modes happens in :meth:`partial_fit` and :meth:`fit`, information is
    stored in 'holder' attributes, and then that information is applied
    blindly to any data that is passed to :meth:`transform`. TL does
    not mutate your data during fitting, so the changes to your data do
    not happen in 'real time'. Because of this temporal dynamic, TL is
    not able to save changes to your data in-situ. If you log a lot of
    changes to your data in `partial_fit` or `fit` and then the program
    terminates for whatever reason, you lose all your work. If you want
    to make edits to the data in real time and be able to save your
    changes in-situ then use TextLookupRealTime.

    To run TL in autonomous mode, set either `auto_delete` or
    `auto_add_to_lexicon` to True; both cannot simultaneously be True.
    `auto_add_to_lexicon` can only be True if the `update_lexicon`
    parameter is True.

    When `auto_add_to_lexicon` is True, if TL encounters a word that is
    not in the `Lexicon` it will automatically stage the word in
    the :attr:`LEXICON_ADDENDUM_` and go to the next word until all the
    words in the text are exhausted. When `auto_delete` is True, if TL
    encounters a word that is not in the `Lexicon`, it will silently add
    the word to the :attr:`DELETE_ALWAYS_` attribute and go to the next
    word, until all the words in the text are exhausted. In these cases,
    TL can never proceed into manual mode. To allow TL to go into manual
    mode, `auto_delete` and `auto_add_to_lexicon` both must be False.

    In manual mode, when TL encounters a word that is not in the
    `Lexicon`, the user will be prompted with an interactive menu for an
    action. Choices that are always presented include: 'skip always',
    'delete always', 'replace always', and 'split always'. Conditionally,
    if `update_lexicon`. is True, an 'add to lexicon' option is also
    presented. If you choose something from the 'always' group, the word
    goes into a 'holder' object for the selected action so that TL knows
    how to handle it during transform. TL does not have the ability to
    handle the same word in different ways at different times. Whatever
    instruction is selected for one occurrence of a word must be applied
    to all occurrences of the word because the storage mechanisms for
    the operation/word combinations do not track the exact locations of
    individual words.

    When you are in the manual text lookup process and are entering words
    at the prompts to replace unknown words in your text, whatever is
    entered is inserted into your text exactly as entered by you. You
    must enter the text exactly as you want it in the cleaned output. If
    normalizing the text is important to you, you must enter the text in
    the case that you want in the output, TL will not do it for you.

    The holder objects are all accessible attributes in the TL public
    API. See the Attributes section for more details. These holder
    objects can also be passed at instantiation to give TL a head-start
    on words that aren't in the `Lexicon` and helps make a manual session
    more automated. Let's say, for example, that you know that your
    text is full of some proper names that aren't in the `Lexicon`, and
    you don't want to add them permanently, and you don't want to have
    to always tell TL what to do with these words when they come up.
    You decide that you want to leave them in the text body and have
    TL ignore them. At instantiation pass a list of these strings to
    the `SKIP_ALWAYS` parameter. So you might pass ['ZEKE', 'YVONNE',
    'XAVIER',...] to `SKIP_ALWAYS`. TL will always skip these words
    without asking. The passed `SKIP_ALWAYS` becomes the starting seed
    of the :attr:`SKIP_ALWAYS_` attribute. Any other manual inputs
    during the session that say to always skip certain other words
    will be added to this list, so that at the end of the session
    the `SKIP_ALWAYS_` attribute will contain your originally passed
    words and the words added during the session.

    TL always looks for special instructions before looking to see if
    a word is in the `Lexicon`. Otherwise, if TL checked the word against
    the `Lexicon` first and the word is it`, TL would go to the next
    word automatically. Doing it in this way allows for users to give
    special instructions for words already in the `Lexicon`. Let's say
    there is a word in the `Lexicon` but you want to delete it from your
    text. You could pass it to `DELETE_ALWAYS` and TL will remove it
    regardless of what the `Lexicon` says.

    The `update_lexicon` parameter does not cause TL to directly update
    the `Lexicon`. If the user opts to stage a word for addition to the
    `Lexicon`, the word is added to the `LEXICON_ADDENDUM_` attribute.
    This is a deliberate design choice to stage the words rather than
    silently modify the `Lexicon`. This gives the user a layer of
    protection where they can review the words staged to go into the
    `Lexicon`, make any changes needed, then manually pass them to the
    `Lexicon` `add_words` method.

    TL requires (possibly ragged) 2D data formats. Accepted objects
    include python built-in lists and tuples, numpy arrays, pandas
    dataframes, and polars dataframes. Use pybear :class:`TextSplitter`
    to convert 1D text to 2D tokens. Results are always returned as a 2D
    python list of lists of strings.

    Your data should be in a highly processed state before using TL.
    This should be one of the last steps in a text wrangling workflow
    because the content of your text will be compared directly against
    the words in the `Lexicon`, and all the words in the pybear `Lexicon`
    have no non-alpha characters and are all majuscule. All junk
    characters should be removed and clear separators established. A
    pybear text wrangling workflow might look like:
    TextStripper > TextReplacer > TextSplitter > TextNormalizer >
    TextRemover > TextLookup > StopRemover > TextJoiner > TextJustifier

    Every operation in TL is case-sensitive. Remember that the formal
    pybear `Lexicon` is majuscule; use pybear :class:`TextNormalizer` to
    make all your text majuscule before using TL. Otherwise, TL will
    always flag every valid word that is not majuscule because it doesn't
    exactly match the `Lexicon`. If you alter your local copy of the
    pybear `Lexicon` with your own words of varying capitalization, TL
    honors your capitalization scheme.

    If TL encounters a word during transform that was not seen during
    fitting and it is not in the `Lexicon`, the way that it is handled
    depends on the setting of the `auto_delete` parameter. If
    `auto_delete` is True, the word is deleted from the text body. If
    False, the word is skipped. In both cases, the word is added to
    an :attr:`OOV_` (out of vocabulary) dictionary. `OOV_` is only
    available after data has been passed to `transform`. The keys are
    the out-of-vocabulary words and the values are the frequency of each
    unseen word.

    TL is a full-fledged scikit-style transformer. It has fully
    functional `get_params`, `set_params`, `partial_fit`, `fit`,
    `transform`, and `fit_transform` methods. It also has a no-op
    `score` method that allows TL to be wrapped by dask_ml wrappers,
    on the off-chance that you actually have text data in dask format.

    TL has an :attr:`n_rows_` attribute which is only available after
    data has been passed to :meth:`partial_fit` or :meth:`fit`. It is
    the total number of rows of text seen in the original data and is
    not necessarily the number of rows in the outputted data. TL also
    has a :attr:`row_support_` attribute that is a boolean vector of
    shape (n_rows, ) that indicates which rows of the original data were
    kept during the transform process (True) and which were deleted
    (False). The only way that an entry could become False is if the
    `remove_empty_rows` parameter is True and a row becomes empty when
    handling unknown words. `row_support_` is only available after
    something has been passed to `transform`, and only reflects the last
    dataset passed to transform.

    Parameters
    ----------
    update_lexicon : bool, default = False
        Whether to queue words that are not in the pybear :class:`Lexicon`
        for later addition to the `Lexicon`. This applies to both
        autonomous and interactive modes. If False, TL will never put a
        word in :attr:`LEXICON_ADDENDUM_` and will never prompt you with
        the option.
    skip_numbers : bool, default = True
        When True, TL will try to do Python float(word) on the word and,
        if it can be cast to a float, TL will skip it and go to the next
        word. If False, TL will handle it like any other word. There are
        no numbers in the formal pybear `Lexicon` so TL will always flag
        them and handle them autonomously or prompt the user for an
        action. Since they are handled like any other word, it would be
        possible to stage them for addition to your local copy of the
        `Lexicon`.
    auto_split : bool, default = True
        TL will first look if the word is in any of the holder objects
        for special instructions, then look to see if the word is in
        the `Lexicon`. If not, the next step otherwise would be auto-add
        to `Lexicon`, auto-delete, or go into manual mode. This
        functionality is a last-ditch effort to see if a word is an
        erroneous compounding of 2 words that are in the `Lexicon`. If
        `auto_split` is True, TL will iteratively split any word of 4 or
        more characters from after the second character to before the
        second to last character and see if both halves are in the
        `Lexicon`. When/if the first match is found, TL will remove the
        original word, split it, and insert in the original place the 2
        halves that were found to be in the `Lexicon`. If `auto_split`
        is False, TL will skip this process and go straight to auto-add,
        auto-delete, or manual mode.
    auto_add_to_lexicon : bool, default = False
        `update_lexicon` must be True to use this parameter. Cannot
        be True if `auto_delete` is True. When this parameter is
        True, TL operates in 'auto-mode', where the user will not be
        prompted for decisions. When TL encounters a word that is
        not in the `Lexicon`, the word will silently be staged in
        the `LEXICON_ADDENDUM_` attribute to be added to the `Lexicon`
        later.
    auto_delete : bool, default = False
        If `update_lexicon` is True, then this cannot be set to True.
        When this parameter is True, TL operates in 'auto-mode', where
        the user will not be prompted for decisions. When TL encounters
        a word that is not in the `Lexicon`, the word will be silently
        deleted from the text body.
    DELETE_ALWAYS : Sequence[str] | None, default = None
        A list of words that will always be deleted by TL, even if they
        are in the `Lexicon`. In both manual and auto modes, TL will
        silently delete the word(s), no questions asked. What is passed
        here becomes the seed for the :attr:`DELETE_ALWAYS_` attribute,
        which may have more words added to it during run-time in manual
        mode. Auto-mode will never add more words to this list.
    REPLACE_ALWAYS : dict[str, str] | None, default = None
        A dictionary with words expected to be in the text body as keys
        and their respective single-word replacements as values. TL
        will replace these words even if they are in the `Lexicon`.
        For both auto and manual mode, TL will not prompt the user for
        any more information, it will silently replace the word. What
        is passed here becomes the seed for the :attr:`REPLACE_ALWAYS_`
        attribute, which may have more word/replacement pairs added to
        it during run-time in manual mode. Auto-mode will never add more
        entries to this dictionary.
    SKIP_ALWAYS : Sequence[str] | None, default = None
        A list of words that will always be ignored by TL, even if
        they are not in the `Lexicon`. For both auto and manual mode,
        TL will not prompt the user for any more information, it will
        silently skip the word. What is passed here becomes the seed for
        the :attr:`SKIP_ALWAYS_` attribute, which may have more words
        added to it during run-time in manual mode. Auto-mode will only
        a add entries to this list if `ignore_numbers` is True and TL
        finds a number during partial_fit / fit.
    SPLIT_ALWAYS : dict[str, Sequence[str]] | None, default = None
        A dictionary with words expected to be in the text body as keys
        and their respective multi-word lists of replacements as values.
        TL will remove the original word and insert these words into
        the text body starting in its position even if the original
        word is in the `Lexicon`. For both auto and manual mode, TL
        will not prompt the user for any more information, it will
        silently split the word. What is passed here becomes the seed
        for the :attr:`SPLIT_ALWAYS_` attribute, which may have more
        word/replacement pairs added to it during run-time in manual
        mode. Auto-mode will only add entries to this dictionary if
        `auto_split` is True and TL finds a valid split for an unknown
        word.
    remove_empty_rows : bool, default = False
        Whether to remove any rows that may have been made empty
        during the lookup process. If `remove_empty_rows` is True and
        rows are deleted, the user can find supplemental information
        in :attr:`row_support_`, which indicates through booleans which
        rows were kept (True) and which rows were removed (False).
    verbose : bool, default = False
        Whether to display helpful information during the transform
        process. This applies to both auto and manual modes.

    Attributes
    ----------
    n_rows_
    row_support_
    DELETE_ALWAYS_
    KNOWN_WORDS_
    LEXICON_ADDENDUM_
    REPLACE_ALWAYS_
    SKIP_ALWAYS_
    SPLIT_ALWAYS_
    OOV_

    Notes
    -----
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

    WipXContainer:
        list[list[str]]

    RowSupportType:
        numpy.ndarray[bool]

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextLookup as TL
    >>> trfm = TL(skip_numbers=False, auto_delete=True, auto_split=False)
    >>> X = [
    ...    ['FOUR', 'SKORE', '@ND', 'SEVEN', 'YEARS', 'ABO'],
    ...    ['OUR', 'FATHERS', 'BROUGHT', 'FOTH', 'UPON', 'THIZ', 'CONTINENT'],
    ...    ['A', 'NEW', 'NETION', 'CONCEIVED', 'IN', 'LOBERTY'],
    ...    ['AND', 'DEDICORDED', '2', 'THE', 'PRAPISATION'],
    ...    ['THAT', 'ALL', 'MEESES', 'ARE', 'CREATED', 'EQUEL']
    ... ]
    >>> out = trfm.fit_transform(X)
    >>> for i in out:
    ...     print(i)
    ['FOUR', 'SEVEN', 'YEARS']
    ['OUR', 'FATHERS', 'BROUGHT', 'UPON', 'CONTINENT']
    ['A', 'NEW', 'CONCEIVED', 'IN']
    ['AND', 'THE']
    ['THAT', 'ALL', 'ARE', 'CREATED']

    """


    def __init__(
        self,
        *,
        update_lexicon:bool = False,
        skip_numbers:bool = True,
        auto_split:bool = True,
        auto_add_to_lexicon:bool = False,
        auto_delete:bool = False,
        DELETE_ALWAYS:Sequence[str] | None = None,
        REPLACE_ALWAYS:dict[str, str] | None = None,
        SKIP_ALWAYS:Sequence[str] | None = None,
        SPLIT_ALWAYS:dict[str, Sequence[str]] | None = None,
        remove_empty_rows:bool = False,
        verbose:bool = False
    ) -> None:
        """Initialize the `TextLookup` instance."""

        # must have a & w in it for _split_or_replace_handler (mixin)
        self._LEX_LOOK_DICT = {
            'a': 'Add to Lexicon',
            'f': 'Replace always',
            'l': 'Delete always',
            'u': 'Split always',
            'w': 'Skip always',
            'q': 'Quit'
        }

        super().__init__(
            update_lexicon=update_lexicon,
            skip_numbers=skip_numbers,
            auto_split=auto_split,
            auto_add_to_lexicon=auto_add_to_lexicon,
            auto_delete=auto_delete,
            DELETE_ALWAYS=DELETE_ALWAYS,
            REPLACE_ALWAYS=REPLACE_ALWAYS,
            SKIP_ALWAYS=SKIP_ALWAYS,
            SPLIT_ALWAYS=SPLIT_ALWAYS,
            remove_empty_rows=remove_empty_rows,
            verbose=verbose
        )

    # END init ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    def __pybear_is_fitted__(self) -> bool:
        return hasattr(self, 'KNOWN_WORDS_')


    # property -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @property
    def n_rows_(self) -> int:
        """Get the `n_rows_` attribute.

        The cumulative number of rows of text passed to :meth:`partial_fit`.
        Not necessarily the number of rows in the outputted data.

        Returns
        -------
        n_rows_ : int
            The cumulative number of rows of text passed to `partial_fit`.

        """

        return self._n_rows


    @property
    def OOV_(self) -> dict[str, int]:
        """Get the `OOV_` attribute.

        Access "Out-of-vocabulary" words that were found during transform
        but were not seen during fitting. If data that was not seen
        during `partial_fit` / `fit` is passed to :meth:`transform`,
        there is the possibility that there are strings that were not
        previously seen. In this case, TL will not do any more learning
        and will not prompt for anything from the user. If `auto_delete`
        is True, TL will delete this new word; if False, the word is
        skipped. In both cases, TL will always add all unseen strings
        as keys in this dictionary. The values are the frequency of
        each respective string.

        Returns
        -------
        OOV_ : dict[str, int]
            Out-of-vocabulary words found during transform.

        """

        if not hasattr(self, '_OOV'):
            raise AttributeError(
                f"'OOV_' is not accessible until after transform"
            )
        else:
            return self._OOV

    # END property -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # def get_params
    # handled by TextLookupMixin/GetParamsMixin


    # def set_params
    # handled by TextLookupMixin/SetParamsMixin


    # def fit_transform
    # handled by TextLookupMixin/FitTransformMixin


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Batch-wise fit method.

        Scan tokens in `X` and either log how to autonomously handle
        tokens not in the pybear `Lexicon` or prompt for how to handle.

        Parameters
        ----------
        X : XContainer
            The (possibly ragged) 2D container of text to have its
            contents cross-referenced against the pybear `Lexicon`.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextLookup` instance.

        """

        # do not make a copy of X, do not mutate X. Instead of mutating X
        # into list[list[str]] like transform, extract one line at a time
        # from X as list[str], that way there are smaller copies.

        _validation(
            X,
            self.update_lexicon,
            self.skip_numbers,
            self.auto_split,
            self.auto_add_to_lexicon,
            self.auto_delete,
            self.DELETE_ALWAYS,
            self.REPLACE_ALWAYS,
            self.SKIP_ALWAYS,
            self.SPLIT_ALWAYS,
            self.remove_empty_rows,
            self.verbose
        )

        # get n_rows -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if hasattr(X, 'shape'):
            _n_rows = int(X.shape[0])
            _n_words = int(X.shape[0] * X.shape[1])
        else:
            _n_rows = len(X)
            _n_words = sum(map(len, X))

        self._n_rows = getattr(self, '_n_rows', 0) + _n_rows
        # END get n_rows -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # Manage attributes -- -- -- -- -- -- -- -- -- -- -- -- -- --
        self._DELETE_ALWAYS = \
            list(getattr(self, 'DELETE_ALWAYS_', deepcopy(self.DELETE_ALWAYS) or []))
        self._REPLACE_ALWAYS = \
            getattr(self, 'REPLACE_ALWAYS_', deepcopy(self.REPLACE_ALWAYS) or {})
        self._SKIP_ALWAYS = \
            list(getattr(self, 'SKIP_ALWAYS_', deepcopy(self.SKIP_ALWAYS) or []))
        self._SPLIT_ALWAYS = \
            getattr(self, 'SPLIT_ALWAYS_', deepcopy(self.SPLIT_ALWAYS) or {})

        self._LEXICON_ADDENDUM: list[str] = \
            getattr(self, 'LEXICON_ADDENDUM_', [])

        self._KNOWN_WORDS: list[str] = \
            getattr(self, 'KNOWN_WORDS_', list(self.get_lexicon()))
        # END Manage attributes -- -- -- -- -- -- -- -- -- -- -- -- --


        if self.verbose:
            print(f'\nRunning Lexicon cross-reference...')

        _quit = False
        _word_counter = 0
        for _row_idx in range(_n_rows-1, -1, -1):

            if self.verbose:
                print(f'\nStarting row {_row_idx+1} of {_n_rows} working backwards')
                print(f'\nCurrent state of ')
                self._display_lexicon_update()

            # NEED TO EXTRACT CURRENT LINE ONE BY ONE FROM THE DATA
            # we know from validation it is legit 2D
            if isinstance(X, pd.DataFrame):
                _line = list(map(str, X.values[_row_idx]))
            elif isinstance(X, pl.DataFrame):
                _line = list(map(str, X[_row_idx].to_numpy().ravel()))
            else:
                _line = list(map(str, X[_row_idx]))

            # GO THRU BACKWARDS TO STAY STANDARDIZED WITH TextLookupRealTime.
            for _word_idx in range(len(_line)-1, -1, -1):

                _word_counter += 1
                if self.verbose and _word_counter % 1000 == 0:
                    print(f'\nWord {_word_counter:,} of {_n_words:,}...')

                _word = _line[_word_idx]

                # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
                # short-circuit for things already known or learned in-situ
                if _word in self._SKIP_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(f'\n*** ALWAYS SKIP *{_word}* ***\n')
                    continue

                if _word in self._DELETE_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(f'\n*** ALWAYS DELETE *{_word}* ***\n')
                    continue

                if _word in self._REPLACE_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS REPLACE *{_word}* WITH '
                            f'*{self._REPLACE_ALWAYS[_word]}* ***\n'
                        )
                    continue

                if _word in self._SPLIT_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS SPLIT *{_word}* WITH '
                            f'*{"*, *".join(self._SPLIT_ALWAYS[_word])}* ***\n'
                        )
                    continue

                # short circuit for numbers
                if self.skip_numbers:
                    try:
                        float(_word)
                        # if get to here its a number, go to next word
                        if self.verbose:
                            print(f'\n*** ALWAYS SKIP NUMBERS *{_word}* ***\n')
                        self._SKIP_ALWAYS.append(_word)
                        continue
                    except:
                        pass
                # END short circuit for numbers

                # PUT THIS LAST.... OTHERWISE USER WOULD NEVER BE ABLE
                # TO DELETE, REPLACE, OR SPLIT WORDS ALREADY IN LEXICON
                if _word in self._KNOWN_WORDS:
                    if self.verbose:
                        print(f'\n*** *{_word}* IS ALREADY IN LEXICON ***\n')
                    continue
                # END short-circuit for already known or learned in-situ
                # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

                # short-circuit for auto-split -- -- -- -- -- -- -- --
                # last ditch before auto-add & auto-delete, try to save
                # the word
                # LOOK IF word IS 2 KNOWN WORDS MOOSHED TOGETHER
                # LOOK FOR FIRST VALID SPLIT IF len(word) >= 4
                if self.auto_split and len(_word) >= 4:
                    _NEW_WORDS = _auto_word_splitter(
                        _word_idx, _line, self._KNOWN_WORDS, _verbose=False
                    )
                    if len(_NEW_WORDS) > 0:
                        # need to put this in SPLIT_ALWAYS_ so that transform
                        # knows what to do with it (transform doesnt have the
                        # ability to run any of the word_splitter functions)
                        self._SPLIT_ALWAYS[_word] = _NEW_WORDS
                        del _NEW_WORDS
                        continue
                    # else: if _NEW_WORDS is empty, there wasnt a valid
                    # split, just pass, if auto_delete is True, that will
                    # delete this word and go to the next word. if
                    # auto_delete is False, it will also pass thru
                    # quasi_auto_splitter, then the user will have to
                    # deal with it manually.
                    del _NEW_WORDS
                # END short-circuit for auto-split -- -- -- -- -- -- --

                # short-circuit for auto-add -- -- -- -- -- -- -- -- --
                # ANYTHING that is in X that is not in Lexicon gets added
                # and stays in X.
                if self.auto_add_to_lexicon:
                    # auto_add_to_lexicon can only be True if
                    # update_lexicon=True
                    if self.verbose:
                        print(f'\n*** AUTO-ADD *{_word}* TO LEXICON ADDENDUM ***\n')
                    self._LEXICON_ADDENDUM.append(_word)
                    self._KNOWN_WORDS.insert(0, _word)
                    continue
                # END short-circuit for auto-add -- -- -- -- -- -- -- --

                # short-circuit for auto-delete -- -- -- -- -- -- -- --
                if self.auto_delete:
                    if self.verbose:
                        print(f'\n*** AUTO-DELETE *{_word}* ***\n')
                    self._DELETE_ALWAYS.append(_word)
                    continue
                # END short-circuit for auto-delete -- -- -- -- -- -- --


                # v v v MANUAL MODE v v v v v v v v v v v v v v v v v v
                # word is not in KNOWN_WORDS or any repetitive operation
                # holders

                # quasi-automate split recommendation -- -- -- -- -- --
                # if we had auto_split=True and we get to here, its
                # because there were no valid splits and just passed
                # thru, so the word will also pass thru here. if
                # auto_split was False and we get to here, we are about
                # to enter manual mode. the user is forced into this as
                # a convenience to partially automate the process of
                # finding splits as opposed to having to manually type
                # 2-way splits over and over.

                if len(_word) >= 4:
                    _NEW_WORDS = _quasi_auto_word_splitter(
                        _word_idx, _line, self._KNOWN_WORDS, _verbose=False
                    )
                    # if the user did not opt to take any of splits (or
                    # if there werent any), then _NEW_WORDS is empty, and
                    # the user is forced into the manual menu.
                    if len(_NEW_WORDS) > 0:
                        # need to put this in SPLIT_ALWAYS_ so that transform
                        # knows what to do with it (transform doesnt have the
                        # ability to run any of the word_splitter functions)
                        self._SPLIT_ALWAYS[_word] = _NEW_WORDS
                        del _NEW_WORDS
                        continue

                    del _NEW_WORDS
                # END quasi-automate split recommendation -- -- -- -- --

                print(f"\n{view_text_snippet(_line, _word_idx, _span=7)}")
                print(f"\n*{_word}* IS NOT IN LEXICON\n")
                _opt = self._LexLookupMenu.choose('Select option')

                # manual menu actions -- -- -- -- -- -- -- -- -- -- -- --
                if _opt == 'a':    # 'a': 'Add to Lexicon'
                    # this menu option is not available in LexLookupMenu
                    # if 'update_lexicon' is False
                    self._LEXICON_ADDENDUM.append(_word)
                    self._KNOWN_WORDS.insert(0, _word)
                    if self.verbose:
                        print(f'\n*** ADD *{_word}* TO LEXICON ADDENDUM ***\n')
                elif _opt == 'l':   # 'l': 'Delete always'
                    self._DELETE_ALWAYS.append(_word)
                    if self.verbose:
                        print(f'\n*** ALWAYS DELETE *{_word}* ***\n')
                elif _opt == 'f':   # 'f': 'Replace always',
                    _new_word = _word_editor(
                        _word,
                        _prompt=f'Enter new word to replace *{_word}*'
                    )
                    self._REPLACE_ALWAYS[_word] = _new_word
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS REPLACE *{_word}* WITH '
                            f'*{_new_word}* ***\n'
                        )
                    del _new_word
                elif _opt == 'w':   # 'w': 'Skip always'
                    self._SKIP_ALWAYS.append(_word)
                    if self.verbose:
                        print(f'\n*** ALWAYS SKIP *{_word}* ***\n')
                elif _opt == 'u':   # 'u': 'Split always'
                    # this split is different than auto and quasi... those
                    # split on both halves of the original word being in
                    # Lexicon, but here the user might pass something new,
                    # so this needs to run thru _split_or_replace_handler
                    # in case update_lexicon is True and the new words
                    # arent in the Lexicon
                    _NEW_WORDS = _manual_word_splitter(
                        _word_idx, _line, self._KNOWN_WORDS, self.verbose
                    )   # cannot be empty
                    self._SPLIT_ALWAYS[_word] = _NEW_WORDS
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS SPLIT *{_word}* WITH '
                            f'*{"*, *".join(_NEW_WORDS)}* ***\n'
                        )
                    # DONT MAKE AN ASSIGNMENT!
                    self._split_or_replace_handler(_line, _word_idx, _NEW_WORDS)
                    del _NEW_WORDS
                elif _opt == 'q':   # 'q': 'Quit'
                    _quit = True
                    break
                else:
                    raise Exception
                # END manual menu actions -- -- -- -- -- -- -- -- -- --

            if _quit:
                break

        del _word_counter

        if self.verbose:
            print(f'\n*** LEX LOOKUP COMPLETE ***\n')

        if self.update_lexicon:
            # show this to the user so they can copy-paste into Lexicon
            if len(self._LEXICON_ADDENDUM) != 0:
                print(f'\n*** COPY AND PASTE THESE WORDS INTO LEXICON ***\n')
                self._display_lexicon_update()


        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """One-shot fit method.

        `TextLookup` attributes are reset with each call.

        Parameters
        ----------
        X : XContainer
            The (possibly ragged) 2D container of text to have its
            contents cross-referenced against the pybear `Lexicon`.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextLookup` instance.

        """

        self.reset()

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ):
        """Apply the handling learned in partial_fit / fit to `X`.

        Parameters
        ----------
        X : XContainer
            The data in (possibly ragged) 2D array-like format.
        copy : bool, default=False
            Whether to make substitutions and deletions directly on the
            passed `X` or a deepcopy of `X`.

        Returns
        -------
        X_tr : list[list[str]]
            The data with instructions from fitting applied.

        """

        check_is_fitted(self)

        _validation(
            X,
            self.update_lexicon,
            self.skip_numbers,
            self.auto_split,
            self.auto_add_to_lexicon,
            self.auto_delete,
            self.DELETE_ALWAYS,
            self.REPLACE_ALWAYS,
            self.SKIP_ALWAYS,
            self.SPLIT_ALWAYS,
            self.remove_empty_rows,
            self.verbose
        )

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X


        # we know from validation X is legit 2D
        X_tr: WipXContainer = _map_X_to_list(X_tr)


        self._row_support: npt.NDArray[bool] = np.ones((len(X_tr), )).astype(bool)
        self._OOV: dict[str, int] = {}
        for _row_idx in range(len(X_tr)-1, -1, -1):

            # GO THRU BACKWARDS BECAUSE A SPLIT OR DELETE WILL CHANGE X
            for _word_idx in range(len(X_tr[_row_idx])-1, -1, -1):

                _word = X_tr[_row_idx][_word_idx]

                # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
                if _word in self._SKIP_ALWAYS:
                    # this may have had words in it from the user at init
                    continue

                elif _word in self._DELETE_ALWAYS:
                    # this may have had words in it from the user at init
                    X_tr[_row_idx].pop(_word_idx)
                    continue

                elif _word in self._REPLACE_ALWAYS:
                    # this may have had words in it from the user at init
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx], _word_idx, [self._REPLACE_ALWAYS[_word]]
                    )
                    continue

                elif _word in self._SPLIT_ALWAYS:
                    # this may have had words in it from the user at init
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx], _word_idx, self._SPLIT_ALWAYS[_word]
                    )
                    # since the word_splitter functions require that
                    # all new words already be in KNOWN_WORDS, or are
                    # added to KNOWN_WORDS or SKIP_ALWAYS in partial_fit,
                    # running _NEW_WORDS thru _split_or_replace_handler
                    # is just to get the new line made, nothing should
                    # happen to LEXICON_ADDENDUM because the words
                    # are already in KNOWN_WORDS or SKIP_ALWAYS.
                    continue

                # PUT THIS LAST.... OTHERWISE USER WOULD NEVER BE ABLE
                # TO DELETE, REPLACE, OR SPLIT WORDS ALREADY IN LEXICON
                if _word in self._KNOWN_WORDS:
                    continue
                # END short-circuit for already known or learned in-situ
                # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

                # if we get to here the word is something that wasnt seen
                # during partial_fit. always gets put in _OOV. if
                # auto_delete, then remove it. otherwise, skip it.
                if _word in self._OOV:
                    self._OOV[_word] += 1
                else:
                    self._OOV[_word] = 1

                if self.auto_delete:
                    X_tr[_row_idx].pop(_word_idx)
                    continue
                else:
                    continue
                # end handle unseen -- -- -- -- -- -- -- -- -- -- -- --


            if self.remove_empty_rows and len(X_tr[_row_idx]) == 0:
                X_tr.pop(_row_idx)
                self._row_support[_row_idx] = False


        return X_tr





