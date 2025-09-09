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

from .._Lexicon.Lexicon import Lexicon

from ....base import (
    DictMenuPrint,
    FileDumpMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)



class _TextLookupMixin(
    FileDumpMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """A mixin for `TextLookup` and `TextLookupRealTime` that provides
    everything except docs, :meth:`partial_fit`, and :meth:`transform`.

    """


    _lexicon_instance = None


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
        """Initialize the TextLookup(RealTime) instance."""

        self.update_lexicon: bool = update_lexicon
        self.skip_numbers: bool = skip_numbers
        self.auto_split: bool = auto_split
        self.auto_add_to_lexicon: bool = auto_add_to_lexicon
        self.auto_delete: bool = auto_delete
        self.SKIP_ALWAYS: Sequence[str] = SKIP_ALWAYS
        self.SPLIT_ALWAYS: dict[str, Sequence[str]] = SPLIT_ALWAYS
        self.DELETE_ALWAYS: Sequence[str] = DELETE_ALWAYS
        self.REPLACE_ALWAYS: dict[str, str] = REPLACE_ALWAYS
        self.remove_empty_rows = remove_empty_rows
        self.verbose = verbose

        # needs to get self._LEX_LOOK_DICT from the child
        if not self.update_lexicon and 'a' in self._LEX_LOOK_DICT:
            del self._LEX_LOOK_DICT['a']

        self._LexLookupMenu = DictMenuPrint(
            self._LEX_LOOK_DICT,
            disp_width=75,
            fixed_col_width=25
        )
    # END init ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @classmethod
    def get_lexicon(cls):
        """Create a singleton Lexicon instance as class attribute."""

        if cls._lexicon_instance is None:
            cls._lexicon_instance = Lexicon()

        return cls._lexicon_instance.lexicon_


    # property -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @property
    def row_support_(self) -> npt.NDArray[bool]:
        """Get the `row_support_` attribute.

        A 1D boolean vector of shape (`n_rows_`, ) that indicates which
        rows were kept in the data during transform. Only available if a
        transform has been performed, and only reflects the last dataset
        passed to :meth:`transform`.

        Returns
        -------
        row_support_ : numpy.ndarray[bool] of shape (`n_rows_`, )
            A boolean vector that indicates which rows were kept in the
            data during transform.

        """

        return self._row_support

    @property
    def DELETE_ALWAYS_(self) -> list[str]:
        """Return the `DELETE_ALWAYS_` attribute.

        A list of words that will always be deleted from the text body
        by TL(RT), even if they are in the `Lexicon`. This list is
        comprised of any words passed to `DELETE_ALWAYS` at instantiation
        and any words added in-situ.

        Returns
        -------
        DELETE_ALWAYS_ : list[str]
            A list of words that will always be deleted from the text
            body by TL(RT), even if they are in the `Lexicon`.

        """
        return self._DELETE_ALWAYS

    @property
    def KNOWN_WORDS_(self) -> list[str]:
        """A WIP object used by TL(RT) to determine "what is in the
        `Lexicon`."

        At instantiation, this is just a copy of the `lexicon_` attribute
        of the pybear :class:`Lexicon` class. If `update_lexicon` is
        True, any words to be added to the `Lexicon` are inserted
        at the front of this list (in addition to also being put
        in :attr:`LEXICON_ADDENDUM_`.) If `auto_add_to_lexicon` is True,
        then words are inserted at the front of this list silently during
        the auto-lookup process. If `auto_add_to_lexicon` is False, words
        are inserted into this list if the user selects 'add to lexicon'.

        Returns
        -------
        KNOWN_WORDS_ : list[str]
            A WIP object used by TL(RT) to determine "what is in the
            `Lexicon`."

        """

        return self._KNOWN_WORDS

    @property
    def LEXICON_ADDENDUM_(self) -> list[str]:
        """Words queued for entry into the pybear `Lexicon`.

        Can only have words in it if `update_lexicon` is True. If in
        auto mode (`auto_add_to_lexicon` is True), anything encountered
        in the text that is not in the :class:`Lexicon` is added to this
        list. In manual mode, if the user selects to 'add to lexicon'
        then the word is put in this list. TL(RT) does not automatically
        add new words to the actual `Lexicon` directly. TL(RT) stages new
        words in `LEXICON_ADDENDUM_` and at the end of a session prints
        them to the screen and makes them available in this attribute.

        Returns
        -------
        LEXICON_ADDENDUM_ : list[str]
            Words queued for entry into the pybear `Lexicon`.

        """

        return self._LEXICON_ADDENDUM

    @property
    def REPLACE_ALWAYS_(self) -> dict[str, str]:
        """A dictionary with words expected to be in the text body as
        keys and their respective single-word replacements as values.

        TL(RT) will replace these words even if they are in the `Lexicon`.
        This holds anything passed to `REPLACE_ALWAYS` at instantiation
        and anything added to it during run-time in manual mode. In
        manual mode, when the user selects 'replace always', the next
        time TL(RT) sees the word it will not prompt the user for any
        more information, it will silently replace the word. When in
        auto mode, TL(RT) will not add any entries to this dictionary.

        Returns
        -------
        REPLACE_ALWAYS_ : dict[str, str]
            A dictionary with words expected to be in the text body as
            keys and their respective single-word replacements as values.

        """

        return self._REPLACE_ALWAYS

    @property
    def SKIP_ALWAYS_(self) -> list[str]:
        """A list of words that are always ignored by TL(RT), even if
        they are not in the `Lexicon`.

        This list holds any words passed to the `SKIP_ALWAYS` parameter
        at instantiation and any words added to it when the user selects
        'skip always' in manual mode. In manual mode, the next time
        TL(RT) sees a word that is in this list it will not prompt the
        user again, it will silently skip the word.

        TL will only make additions to this list in auto mode if
        `skip_numbers` is True and a number is found in the training
        data. TLRT does not make additions to this list in auto mode.

        Returns
        -------
        SKIP_ALWAYS_ : list[str]
            A list of words that are always ignored by TL(RT), even if
            they are not in the `Lexicon`.

        """
        return self._SKIP_ALWAYS

    @property
    def SPLIT_ALWAYS_(self) -> dict[str, Sequence[str]]:
        """A dictionary with words expected to be in the text body as
        keys and their respective multi-word lists of replacements as
        values.

        Similar to :attr:`REPLACE_ALWAYS_`. TL(RT) will sub these words
        in even if the original word is in the `Lexicon`. This dictionary
        holds anything passed to `SPLIT_ALWAYS` at instantiation and any
        splits made when 'split always' is selected in manual mode. In
        manual mode, the next time TL(RT) sees the same word in the text
        body it will not prompt the user again, just silently make the
        split.

        The only way TL will add anything to this dictionary in auto
        mode is if `auto_split` is True and TL finds a valid split of an
        unknown word during `partial_fit` / `fit`. TLRT does not add
        anything to this dictionary in auto mode.

        Returns
        -------
        SPLIT_ALWAYS_ : dict[str, Sequence[str]]
            A dictionary with words expected to be in the text body as
            keys and their respective multi-word lists of replacements
            as values.

        """
        return self._SPLIT_ALWAYS

    # END property -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def reset(self) -> Self:
        """Reset the TextLookup instance.

        This will remove all attributes that are exposed during transform.

        Returns
        -------
        self : object
            Thr reset `TextLookup` instance.

        """

        _attrs = [
            '_n_rows', '_row_support', '_DELETE_ALWAYS', '_REPLACE_ALWAYS',
            '_SKIP_ALWAYS', '_SPLIT_ALWAYS', '_LEXICON_ADDENDUM', '_KNOWN_WORDS',
            '_OOV', '_n_rows', '_row_support', '_DELETE_ALWAYS', '_REPLACE_ALWAYS',
            '_SKIP_ALWAYS', '_SPLIT_ALWAYS', '_LEXICON_ADDENDUM', '_KNOWN_WORDS',
            '_OOV'
        ]

        for _attr in _attrs:
            if hasattr(self, _attr):
                delattr(self, _attr)

        del _attrs

        return self


    def get_metadata_routing(self):
        """`get_metadata_routing` is not implemented in TextLookup."""
        raise NotImplementedError(
            f"'get_metadata_routing' is not implemented in TextLookup"
        )


    # def get_params
    # handled by GetParamsMixin


    # def set_params
    # handled by SetParamsMixin


    # def fit_transform
    # handled by FitTransformMixin


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


    def _display_lexicon_update(
        self,
        n:int | None = None
    ) -> None:
        """Print :attr:`LEXICON_ADDENDUM_` object for copy and paste
        into `Lexicon`.

        Parameters
        ----------
        n : int | None, default = None
            The number of entries in :attr:`LEXICON_ADDENDUM_` to print.

        Returns
        -------
        None

        """

        print(f'LEXICON ADDENDUM:')
        if len(self._LEXICON_ADDENDUM) == 0:
            print(f'*** EMPTY ***')
        else:
            self._LEXICON_ADDENDUM.sort()
            print(f'[')
            for _ in self._LEXICON_ADDENDUM[:(n or len(self._LEXICON_ADDENDUM))]:
                print(f'    "{_}"{"" if _ == self._LEXICON_ADDENDUM[-1] else ","}')
            print(f']')
            print()


    def _split_or_replace_handler(
        self,
        _line: list[str],
        _word_idx: int,
        _NEW_WORDS: list[str]
    ) -> list[str]:
        """Handle removing a user-identified word from a line, substituting
        in new word(s), and updating the attr:`LEXICON_ADDENDUM_`, if
        applicable.

        This is called after split, split always, replace, and replace
        always.

        Parameters
        ----------
        _line : list[str]
            The full line of the data that holds the current word.
        _word_idx : int
            The index of the current word in `_line`.
        _NEW_WORDS : list[str]
            The word(s) to be inserted into `_line` in place of the
            original word.

        Returns
        -------
        _line : list[str]
            The full line in `X` that held the current word with that
            word removed and the new word(s) inserted in the that word's
            place.

        """

        _word = _line[_word_idx]

        _line.pop(_word_idx)

        # GO THRU _NEW_WORDS BACKWARDS
        for _slot_idx in range(len(_NEW_WORDS) - 1, -1, -1):

            _new_word = _NEW_WORDS[_slot_idx]

            _line.insert(_word_idx, _new_word)

            if self.update_lexicon:
                # when prompted to put a word into the lexicon, user can
                # say 'skip always', the word goes into that list, and the
                # user is not prompted again
                # conveniently for plain TextLookup, when in (partial_)fit and
                # the user picks one of the 2 options 'a' or 'w', it causes
                # the word to go in one of the lists which forces bypass
                # here in transform and avoids the menu.
                if _new_word in self._KNOWN_WORDS \
                        or _new_word in self._SKIP_ALWAYS:
                    continue

                # if new word is not KNOWN or not skipped...
                if self.auto_add_to_lexicon:
                    self._LEXICON_ADDENDUM.append(_NEW_WORDS[_slot_idx])
                    self._KNOWN_WORDS.insert(0, _NEW_WORDS[_slot_idx])
                    continue

                print(f"\n*** *{_NEW_WORDS[_slot_idx]}* IS NOT IN LEXICON ***\n")
                _ = self._LexLookupMenu.choose('Select option', allowed='aw')
                if _ == 'a':
                    self._LEXICON_ADDENDUM.append(_NEW_WORDS[_slot_idx])
                    self._KNOWN_WORDS.insert(0, _NEW_WORDS[_slot_idx])
                elif _ == 'w':
                    self._SKIP_ALWAYS.append(_word)
                else:
                    raise Exception

        del _NEW_WORDS

        return _line





