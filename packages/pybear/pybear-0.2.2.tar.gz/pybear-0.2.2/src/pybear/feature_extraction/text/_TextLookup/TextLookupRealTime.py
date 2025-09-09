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

from ....base._validate_user_input import validate_user_str

from ....base._copy_X import copy_X

from ._TextLookupMixin import _TextLookupMixin

from ....base._check_is_fitted import check_is_fitted



class TextLookupRealTime(_TextLookupMixin):
    """Handle words in a 2D array-like body of text that are not in the
    pybear `Lexicon`.

    Options include replacing, removing, splitting, or skipping the word,
    or staging it to add to the pybear :class:`Lexicon`.

    TextLookupRealTime (TLRT) has a dual-functionality :meth:`transform`
    method. TLRT can operate autonomously on your data for a completely
    hands-free experience, or can be driven in a fully interactive
    transform process. The interactive mode is a menu-driven process
    that prompts the user for a decision about a word that is not in the
    `Lexicon` and makes the edits to the data in real time (hence the
    name.)

    The main benefit of having a real-time interactive mode is when you
    have data that has a lot of words that are not in the `Lexicon`.
    Manually cleaning text is a labor-intensive process that can require
    a lot of time and effort and there is always the risk of losing your
    work. TLRT will ask you in-situ after every 20 manual edits if you
    want to save your work to the hard drive. So if your session is
    disrupted at some point midstream, you won't lose all of your work.

    That aspect is the key difference between TLRT and :class:`TextLookup`
    (TL), that TLRT works on your data in real time, meaning that
    the data is modified in-situ immediately when you indicate an
    action. TL is a more conventional scikit-style transformer in
    that the learning that takes place for both autonomous and manual
    modes happens in partial_fit / fit, information is stored in 'holder'
    attributes, and then that information is applied blindly to any
    data that is passed to transform. TL does not mutate your data
    during fitting, so the changes to your data do not happen in
    'real time'. Because of this temporal dynamic, TL is not able to
    save changes to your data in-situ. If you log a lot of changes to
    your data during partial_fit / fit and then the program terminates
    for whatever reason, you lose all your work. TLRT affords you
    the opportunity to save your work in-situ, making your changes
    permanent. Another benefit of operating directly on the data
    in-situ, unlike TL, is that you can perform a different operation
    on each occurrence of a particular word.

    To run TLRT in autonomous mode, set either `auto_delete` or
    `auto_add_to_lexicon` to True; both cannot simultaneously be True.
    `auto_add_to_lexicon` can only be True if the `update_lexicon`
    parameter is True.

    When `auto_add_to_lexicon` is True, if TLRT encounters a word that
    is not in the `Lexicon` it will automatically stage the word in
    the :attr:`LEXICON_ADDENDUM_` and go to the next word until all the
    words in the text are exhausted. When `auto_delete` is True, if TLRT
    encounters a word that is not in the `Lexicon`, it will automatically
    delete the word from the text body and go to the next word, until
    all the words in the text are exhausted. In these cases, TLRT can
    never proceed into manual mode. To allow TLRT enter manual mode,
    both `auto_delete` and `auto_add_to_lexicon` must be False.

    In manual mode, when TLRT encounters a word that is not in the
    `Lexicon`, the user will be prompted with an interactive menu for an
    action. Choices include: 'skip once', 'skip always', 'delete once',
    'delete always', 'replace once', 'replace always', 'split once',
    'split always', and if `update_lexicon` is True, an 'add to lexicon'
    option. Notice that the operations can be split into 2 groups, the
    'once' group and the 'always' group. The 'once' group is a one time
    operation on that word. TLRT will not remember what to do the next
    time it sees this exact word. If you choose something from the
    'always' group, the word and its action go into a 'holder' object so
    that TLRT remembers what to do next time it sees the word. In this
    way, a tedious interactive session can become more automated as the
    session proceeds.

    The holder objects are all accessible attributes in the TLRT public
    API. See the Attributes section for more details. These holder
    objects can also be passed at instantiation to give TLRT a head-start
    on words that aren't in the `Lexicon` and helps make a manual session
    more automated. Let's say, for example, that you know that your
    text is full of some proper names that aren't in the `Lexicon`, and
    you don't want to add them permanently, and you don't want to have
    to always tell TLRT what to do with these words when they come up.
    You decide that you want to leave them in the text body and have
    TLRT ignore them. At instantiation pass a list of these strings to
    the `SKIP_ALWAYS` parameter. So you might pass ['ALICE', 'BOB',
    'CARL', 'DIANE',...] to `SKIP_ALWAYS`. TLRT will always skip these
    words without asking. The passed `SKIP_ALWAYS` becomes the starting
    seed of the :attr:`SKIP_ALWAYS_` attribute. Any other manual inputs
    during the session that say to always skip certain other words
    will be added to this list, so that at the end of the session the
    `SKIP_ALWAYS_` attribute will contain your originally passed words
    and the words added during the session.

    TLRT always looks for special instructions before looking to see if
    a word is in the `Lexicon`. Otherwise, if TLRT checked the word
    against the `Lexicon` first and the word is in it, TLRT would go to
    the next word automatically. Doing it in this way allows for users
    to give special instructions for words already in the `Lexicon`.
    Let's say there is a word in the `Lexicon` but you want to delete it
    from your text. You could pass it to `DELETE_ALWAYS` and TLRT will
    remove it regardless of what the `Lexicon` says.

    The `update_lexicon` parameter does not cause TLRT to directly update
    the `Lexicon`. If the user opts to stage a word for addition to the
    `Lexicon`, the word is added to the `LEXICON_ADDENDUM_` attribute.
    This is a deliberate design choice to stage the words rather than
    silently modify the `Lexicon`. This gives the user a layer of
    protection where they can review the words staged to go into the
    `Lexicon`, make any changes needed, then manually pass them to the
    `Lexicon` `add_words` method.

    TLRT requires (possibly ragged) 2D data formats. Accepted objects
    include python built-in lists and tuples, numpy arrays, pandas
    dataframes, and polars dataframes. Use pybear :class:`TextSplitter`
    to convert 1D text to 2D tokens. Results are always returned as a 2D
    python list of lists of strings.

    Your data should be in a highly processed state before using TLRT.
    This should be one of the last steps in a text wrangling workflow
    because the content of your text will be compared directly against
    the words in the `Lexicon`, and all the words in the pybear `Lexicon`
    have no non-alpha characters and are all majuscule. All junk
    characters should be removed and clear separators established. A
    pybear text wrangling workflow might look like:
    TextStripper > TextReplacer > TextSplitter > TextNormalizer >
    TextRemover > TextLookup > StopRemover > TextJoiner > TextJustifier

    Every operation in TLRT is case-sensitive. Remember that the formal
    pybear `Lexicon` is majuscule; use pybear :class:`TextNormalizer` to
    make all your text majuscule before using TLRT. Otherwise, TLRT will
    always flag every valid word that is not majuscule because it doesn't
    exactly match the `Lexicon`. If you alter your local copy of the
    pybear `Lexicon` with your own words of varying capitalization, TLRT
    honors your capitalization scheme.

    When you are in the manual text lookup process and are entering words
    at the prompts to replace unknown words in your text, whatever is
    entered is inserted into your text exactly as entered by you. You
    must enter the text exactly as you want it in the cleaned output. If
    normalizing the text is important to you, you must enter the text in
    the case that you want in the output, TLRT will not do it for you.

    TLRT is a full-fledged scikit-style transformer. It has fully
    functional `get_params`, `set_params`, `transform`, and `fit_transform`
    methods. It also has `partial_fit`, `fit`, and `score` methods, which
    are no-ops. TLRT technically does not need to be fit for 2 reasons.
    First, in autonomous mode, TLRT already knows everything it needs to
    do transformations from the parameters and the `Lexicon`. Secondly,
    in manual mode the user interacts with the data during transform,
    not partial_fit / fit. These no-op methods are available to fulfill
    the scikit transformer API and make TLRT suitable for incorporation
    into larger workflows, such as Pipelines and dask_ml wrappers.

    Because TLRT doesn't need any information from partial_fit / fit ,
    it is technically always in a 'fitted' state and ready to transform
    data. Checks for fittedness will always return True.

    TLRT exposes 2 attributes after a call to `transform`. First,
    the :attr:`n_rows_` attribute is the number of rows of text seen in
    the original data but is not necessarily the number of rows in the
    outputted data. TLRT also has a :attr:`row_support_` attribute that
    is a boolean vector of shape (n_rows, ) that indicates which rows of
    the original data were kept during the transform process (True) and
    which were deleted (False). The only way that an entry could become
    False is if `remove_empty_rows` is True and a row becomes empty when
    handling unknown words. `row_support_` only reflects the last dataset
    passed to transform.

    Parameters
    ----------
    update_lexicon : bool, default = False
        Whether to queue words that are not in the pybear `Lexicon` for
        later addition to the `Lexicon`. This applies to both autonomous
        and interactive modes. If False, TLRT will never put a word
        in :attr:`LEXICON_ADDENDUM_` and will never prompt you with the
        option.
    skip_numbers : bool, default = True
        When True, TLRT will try to do Python float(word) on the word
        and, if it can be cast to a float, TLRT will skip it and go to
        the next word. If False, TLRT will handle it like any other word.
        There are no numbers in the formal pybear `Lexicon` so TLRT will
        always flag them and handle them autonomously or prompt the user
        for an action. Since they are handled like any other word, it
        would be possible to stage them for addition to your local copy
        of the `Lexicon`.
    auto_split : bool, default = True
        TLRT will first look if the word is in any of the holder
        objects for special instructions, then look to see if the word
        is in the `Lexicon`. If not, the next step otherwise would be
        auto-add to `Lexicon`, auto-delete, or go into manual mode. This
        functionality is a last-ditch effort to see if a word is an
        erroneous compounding of 2 words that are in the `Lexicon`. if
        `auto_split` is True, TLRT will iteratively split any word of
        4 or more characters from after the second character to before
        the second to last character and see if both halves are in the
        `Lexicon`. When/if the first match is found, TLRT will remove
        the original word, split it, and insert in the original place
        the 2 halves that were found to be in the `Lexicon`. If False,
        TLRT will skip this process and go straight to auto-add,
        auto-delete, or manual mode.
    auto_add_to_lexicon : bool, default = False
        `update_lexicon` must be True to use this. Cannot be True
        if `auto_delete` is True. When this parameter is True, TLRT
        operates in 'auto-mode', where the user will not be prompted
        for decisions. When TLRT encounters a word that is not in
        the `Lexicon`, the word will silently be staged in the
        `LEXICON_ADDENDUM_` attribute to be added to the `Lexicon` later.
    auto_delete : bool, default = False
        If `update_lexicon` or `auto_add_to_lexicon` are True then this
        cannot be True . When this parameter is True, TLRT operates in
        'auto-mode', where the user will not be prompted for decisions.
        When TLRT encounters a word that is not in the Lexicon, the word
        will be silently deleted from the text body.
    DELETE_ALWAYS : Sequence[str] | None, default = None
        A list of words that will always be deleted by TLRT, even if
        they are in the `Lexicon`. In both manual and auto modes, TLRT
        will silently delete the word(s), no questions asked. What is
        passed here becomes the seed for the :attr:`DELETE_ALWAYS_`
        attribute, which may have more words added to it during run-time
        in manual mode. Auto-mode will never add more words to this list.
    REPLACE_ALWAYS : dict[str, str] | None, default = None
        A dictionary with words expected to be in the text body as keys
        and their respective single-word replacements as values. TLRT
        will replace these words even if they are in the `Lexicon`. For
        both auto and manual mode, TLRT will not prompt the user for
        any more information, it will silently replace the word. What is
        passed here becomes the seed for the :attr:`REPLACE_ALWAYS_`
        attribute, which may have more word/replacement pairs added to
        it during run-time in manual mode. Auto-mode will never add more
        entries to this dictionary.
    SKIP_ALWAYS : Sequence[str] | None, default = None
        A list of words that will always be ignored by TLRT, even if they
        are not in the `Lexicon`. For both auto and manual mode, TLRT
        will not prompt the user for any more information, it will
        silently skip the word. What is passed here becomes the seed
        for the :attr:`SKIP_ALWAYS_` attribute, which may have more words
        added to it during run-time in manual mode. Auto-mode will never
        add more words to this list.
    SPLIT_ALWAYS : dict[str, Sequence[str]] | None, default = None
        A dictionary with words expected to be in the text body as keys
        and their respective multi-word lists of replacements as values.
        TLRT will remove the original word and insert these words into
        the text body starting in its position even if the original
        word is in the `Lexicon`. For both auto and manual mode, TLRT
        will not prompt the user for any more information, it will
        silently split the word. What is passed here becomes the seed
        for the :attr:`SPLIT_ALWAYS_` attribute, which may have more
        word/replacement pairs added to it during run-time in manual
        mode. Auto-mode will never add entries to this dictionary.
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
    >>> from pybear.feature_extraction.text import TextLookupRealTime as TLRT
    >>> trfm = TLRT(skip_numbers=True, auto_delete=True, auto_split=False)
    >>> X = [
    ...    ['FOUR', 'SKORE', '@ND', 'SEVEN', 'YEARS', 'ABO'],
    ...    ['OUR', 'FATHERS', 'BROUGHT', 'FOTH', 'UPON', 'THIZ', 'CONTINENT'],
    ...    ['A', 'NEW', 'NETION', 'CONCEIVED', 'IN', 'LOBERTY'],
    ...    ['AND', 'DEDICORDED', '2', 'THE', 'PRAPISATION'],
    ...    ['THAT', 'ALL', 'MEESES', 'ARE', 'CREATED', 'EQUEL']
    ... ]
    >>> out = trfm.transform(X)
    >>> for i in out:
    ...     print(i)
    ['FOUR', 'SEVEN', 'YEARS']
    ['OUR', 'FATHERS', 'BROUGHT', 'UPON', 'CONTINENT']
    ['A', 'NEW', 'CONCEIVED', 'IN']
    ['AND', '2', 'THE']
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
        """Initialize the `TextLookupRealTime` instance."""

        # must have a & w in it for _split_or_replace_handler (mixin)
        self._LEX_LOOK_DICT = {
            'a': 'Add to Lexicon',
            'e': 'Replace once',
            'f': 'Replace always',
            'd': 'Delete once',
            'l': 'Delete always',
            's': 'Split once',
            'u': 'Split always',
            'k': 'Skip once',
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
        return True


    # property -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @property
    def n_rows_(self) -> int:
        """Get the `n_rows_` attribute.

        The number of rows in the last data passed to :meth:`transform`.
        Not necessarily the number of rows in the outputted data.

        Returns
        -------
        n_rows_ : int
            The number of rows in the last data passed to `transform`.

        """

        return self._n_rows

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
        """No-op batch-wise fit method.

        Parameters
        ----------
        X : XContainer
            The (possibly ragged) 2D container of text to have its
            contents cross-referenced against the pybear `Lexicon`.
            Ignored.
        y : Any, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextLookupRealTime` instance.

        """

        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op one-shot fit method.

        Parameters
        ----------
        X : XContainer
            The (possibly ragged) 2D container of text to have its
            contents cross-referenced against the pybear `Lexicon`.
            Ignored.
        y : Any | None, default=None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextLookupRealTime` instance.

        """

        self.reset()

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ):
        """Scan tokens in `X` and either autonomously handle tokens not
        in the pybear `Lexicon` or prompt for handling.

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
            The data with user-entered, auto-replaced, or deleted tokens
            in place of tokens not in the pybear `Lexicon`.

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

        self._n_rows = len(X_tr)

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

        # MANAGE THE CONTENTS OF LEXICON ADDENDUM -- -- -- -- -- -- --
        _abort = False

        if self.update_lexicon and not self.auto_add_to_lexicon \
                and len(self._LEXICON_ADDENDUM) != 0:

            print(f'\n*** LEXICON ADDENDUM IS NOT EMPTY ***\n')
            print(f'LEXICON ADDENDUM has {len(self._LEXICON_ADDENDUM)} entries')
            print(f'First 10 in LEXICON ADDENDUM:')
            self._display_lexicon_update(n=10)
            print()

            _opt = validate_user_str(
                f'Empty it(e), Proceed anyway(p), Abort TextLookupRealTime(a) > ',
                'AEP'
            )
            if _opt == 'A':
                _abort = True
            elif _opt == 'E':
                self._LEXICON_ADDENDUM = []
            elif _opt == 'P':
                pass
            else:
                raise Exception
            del _opt
        # END MANAGE THE CONTENTS OF LEXICON ADDENDUM -- -- -- -- -- --

        if self.verbose:
            print(f'\nRunning Lexicon cross-reference...')

        _quit = False
        _n_edits = 0
        _word_counter = 0
        self._row_support: npt.NDArray[bool] = np.ones((len(X_tr), )).astype(bool)
        for _row_idx in range(len(X_tr)-1, -1, -1) if not _abort else []:

            if self.verbose:
                print(f'\nStarting row {_row_idx+1} of {len(X_tr)} working backwards')
                print(f'\nCurrent state of ')
                self._display_lexicon_update()

            # GO THRU BACKWARDS BECAUSE A SPLIT OR DELETE WILL CHANGE X
            for _word_idx in range(len(X_tr[_row_idx])-1, -1, -1):

                # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
                # Manage in-situ save option if in manual edit mode.
                # the only way that _n_edits can increment is if u get
                # into manual mode, which means both auto_add_to_lexicon
                # and auto_delete are False. All of this code must stay
                # in this scope because it needs the FileDumpMixin.
                if _n_edits != 0 and _n_edits % 20 == 0:
                    _prompt = f'\nSave in-situ changes to file(s) or Continue(c) > '
                    if validate_user_str(_prompt, 'SC') == 'S':
                        _opt = validate_user_str(
                            f'\nSave to csv(c), Save to txt(t), Abort(a)? > ',
                            'CTA'
                        )
                        if _opt == 'C':
                            self.dump_to_csv(X_tr)
                        elif _opt == 'T':
                            self.dump_to_txt(X_tr)
                        elif _opt == 'A':
                            pass
                        else:
                            raise Exception
                        del _opt
                    del _prompt
                    _n_edits += 1
                # END manage in-situ save -- -- -- -- -- -- -- -- -- --

                _word_counter += 1
                if self.verbose and _word_counter % 1000 == 0:
                    print(f'\nWord {_word_counter:,} of {sum(map(len, X_tr)):,}...')

                _word = X_tr[_row_idx][_word_idx]

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
                    X_tr[_row_idx].pop(_word_idx)
                    continue

                if _word in self._REPLACE_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS REPLACE *{_word}* WITH '
                            f'*{self._REPLACE_ALWAYS[_word]}* ***\n'
                        )
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx], _word_idx, [self._REPLACE_ALWAYS[_word]]
                    )
                    continue

                if _word in self._SPLIT_ALWAYS:
                    # this may have had words in it from the user at init
                    if self.verbose:
                        print(
                            f'\n*** ALWAYS SPLIT *{_word}* WITH '
                            f'*{"*, *".join(self._SPLIT_ALWAYS[_word])}* ***\n'
                        )
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx], _word_idx, self._SPLIT_ALWAYS[_word]
                    )
                    continue

                # short circuit for numbers
                if self.skip_numbers:
                    try:
                        float(_word)
                        # if get to here its a number, go to next word
                        if self.verbose:
                            print(f'\n*** ALWAYS SKIP NUMBERS *{_word}* ***\n')
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
                        _word_idx, X_tr[_row_idx], self._KNOWN_WORDS, self.verbose
                    )
                    if len(_NEW_WORDS) > 0:
                        X_tr[_row_idx] = self._split_or_replace_handler(
                            X_tr[_row_idx],
                            _word_idx,
                            _NEW_WORDS
                        )
                        del _NEW_WORDS
                        # since auto_word_splitter requires that
                        # both halves already be in KNOWN_WORDS, running
                        # _NEW_WORDS thru _split_or_replace_handler is
                        # just to get the new line made, nothing should
                        # happen to LEXICON_ADDENDUM because the words
                        # are already in KNOWN_WORDS.
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
                    X_tr[_row_idx].pop(_word_idx)
                    continue
                # END short-circuit for auto-delete -- -- -- -- -- -- --


                # v v v MANUAL MODE v v v v v v v v v v v v v v v v v v
                # word is not in KNOWN_WORDS or any repetitive operation
                # holders

                # a manual edit is guaranteed to happen after this point
                _n_edits += 1

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
                        _word_idx, X_tr[_row_idx], self._KNOWN_WORDS, self.verbose
                    )
                    # if the user did not opt to take any of splits (or
                    # if there werent any), then _NEW_WORDS is empty, and
                    # the user is forced into the manual menu.
                    if len(_NEW_WORDS) > 0:
                        X_tr[_row_idx] = self._split_or_replace_handler(
                            X_tr[_row_idx],
                            _word_idx,
                            _NEW_WORDS
                        )
                        del _NEW_WORDS
                        # since quasi_auto_word_splitter requires that
                        # both halves already be in KNOWN_WORDS, running
                        # _NEW_WORDS thru _split_or_replace_handler is
                        # just to get the new line made, nothing should
                        # happen to LEXICON_ADDENDUM because the words
                        # are already in KNOWN_WORDS.
                        continue

                    del _NEW_WORDS
                # END quasi-automate split recommendation -- -- -- -- --

                print(f"\n{view_text_snippet(X_tr[_row_idx], _word_idx, _span=7)}")
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
                    # and X is unchanged
                elif _opt in 'dl':   # 'd': 'Delete once', 'l': 'Delete always'
                    if _opt == 'd':
                        if self.verbose:
                            print(f'\n*** ONE-TIME DELETE OF *{_word}* ***\n')
                    elif _opt == 'l':
                        self._DELETE_ALWAYS.append(_word)
                        if self.verbose:
                            print(f'\n*** ALWAYS DELETE *{_word}* ***\n')
                    X_tr[_row_idx].pop(_word_idx)
                elif _opt in 'ef':   # 'e': 'Replace once', 'f': 'Replace always',
                    _new_word = _word_editor(
                        _word,
                        _prompt=f'Enter new word to replace *{_word}*'
                    )
                    if _opt == 'e':
                        if self.verbose:
                            print(
                                f'\n*** ONE-TIME REPLACE *{_word}* WITH '
                                f'*{_new_word}* ***\n'
                            )
                    elif _opt == 'f':
                        self._REPLACE_ALWAYS[_word] = _new_word
                        if self.verbose:
                            print(
                                f'\n*** ALWAYS REPLACE *{_word}* WITH '
                                f'*{_new_word}* ***\n'
                            )
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx], _word_idx, [_new_word]
                    )
                    del _new_word
                elif _opt in 'kw':   # 'k': 'Skip once', 'w': 'Skip always'
                    if _opt == 'k':
                        if self.verbose:
                            print(f'\n*** ONE-TIME SKIP *{_word}* ***\n')
                    elif _opt == 'w':
                        self._SKIP_ALWAYS.append(_word)
                        if self.verbose:
                            print(f'\n*** ALWAYS SKIP *{_word}* ***\n')
                    # a no-op
                    pass
                elif _opt in 'su':   # 's': 'Split once', 'u': 'Split always'
                    _NEW_WORDS = _manual_word_splitter(
                        _word_idx, X_tr[_row_idx], self._KNOWN_WORDS, self.verbose
                    )   # cannot be empty
                    if _opt == 's':
                        if self.verbose:
                            print(
                                f'\n*** ONE-TIME SPLIT *{_word}* WITH '
                                f'*{"*, *".join(self._SPLIT_ALWAYS[_word])}* ***\n'
                            )
                    elif _opt == 'u':
                        self._SPLIT_ALWAYS[_word] = _NEW_WORDS
                        if self.verbose:
                            print(
                                f'\n*** ALWAYS SPLIT *{_word}* WITH '
                                f'*{"*, *".join(self._SPLIT_ALWAYS[_word])}* ***\n'
                            )
                    X_tr[_row_idx] = self._split_or_replace_handler(
                        X_tr[_row_idx],
                        _word_idx,
                        _NEW_WORDS
                    )
                    del _NEW_WORDS
                elif _opt == 'q':   # 'q': 'Quit'
                    _quit = True
                    break
                else:
                    raise Exception
                # END manual menu actions -- -- -- -- -- -- -- -- -- --

            if self.remove_empty_rows and len(X_tr[_row_idx]) == 0:
                X_tr.pop(_row_idx)
                self._row_support[_row_idx] = False

            if _quit:
                break

        del _n_edits, _word_counter

        print(f'\n*** LEX LOOKUP COMPLETE ***\n')

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # only ask to save at the end if the instance was set up for manual
        if not self.auto_add_to_lexicon and not self.auto_delete:
            print(f'\n*** LAST CHANCE TO SAVE ***\n')
            _prompt = f'\nSave completed text to file(s) or Skip(c) > '
            if validate_user_str(_prompt, 'SC') == 'S':
                _opt = validate_user_str(
                    f'\nSave to csv(c), Save to txt(t), Abort(a)? > ',
                    'CTA'
                )
                if _opt == 'C':
                    self.dump_to_csv(X_tr)
                elif _opt == 'T':
                    self.dump_to_txt(X_tr)
                elif _opt == 'A':
                    pass
                else:
                    raise Exception
                del _opt
            del _prompt
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if self.update_lexicon and not _abort:
            # show this to the user so they can copy-paste into Lexicon
            if len(self._LEXICON_ADDENDUM) != 0:
                print(f'\n*** COPY AND PASTE THESE WORDS INTO LEXICON ***\n')
                self._display_lexicon_update()

        del _abort


        return X_tr





