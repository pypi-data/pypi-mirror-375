# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Sequence
)

import re
import os
import glob

import numpy as np

from .._TextStatistics.TextStatistics import TextStatistics

from ._methods._add_words import _add_words
from ._methods._check_order import _check_order
from ._methods._delete_words import _delete_words
from ._methods._find_duplicates import _find_duplicates



class Lexicon(TextStatistics):
    """The pybear lexicon of words in the English language.

    Not exhaustive, though attempts have been made. This serves as a
    list of words in the English language for text-cleaning purposes.
    `Lexicon` also has an attribute for pybear-defined stop words.

    The published pybear `Lexicon` only allows the 26 letters of the
    English alphabet and all must be capitalized. Other characters,
    such as numbers, hyphens, apostrophes, etc., are not allowed. For
    example, entries one may see in the pybear `Lexicon` include "APPLE",
    "APRICOT", "APRIL". Entries that one will not see in the published
    version are "AREN'T", "ISN'T" and "WON'T" (the entries would be
    "ARENT", "ISNT", and "WONT".) `Lexicon` has validation in place to
    protect the integrity of the published pybear `Lexicon` toward these
    rules. However, this validation can be turned off and local copies
    can be updated with any strings that the user likes.

    pybear stores its lexicon and stop words in text files that are
    read from the local disk when a `Lexicon` class is instantiated,
    populating the attributes of the instance. The lexicon files are
    named by the 26 letters of the English alphabet, therefore there
    are 26 `Lexicon` files. Words are assigned to a file by their first
    letter.

    The :meth:`add_words` method allows users to add words to their
    local copies of the `Lexicon`, that is, write new words to the
    `Lexicon` text files. The validation protocols that are in place
    secure the integrity of the published version of the pybear
    `Lexicon`, and the user must consider these when attempting to change
    their local  copy. When making local additions to the `Lexicon` via
    `add_words`,  this validation can be turned off via `file_validation`,
    `character_validation`, and `majuscule_validation` keyword arguments.
    These allow your `Lexicon` to take non-alpha characters, upper or
    lower case, and allows `Lexicon` to create new text files for itself.

    Attributes
    ----------
    size_
    lexicon_
    stop_words_
    overall_statistics_
    string_frequency_
    startswith_frequency_
    character_frequency_
    uniques_

    Examples
    --------
    >>> from pybear.feature_extraction.text import Lexicon
    >>> Lex = Lexicon()
    >>> round(Lex.size_, -4)
    70000
    >>> Lex.lexicon_[:5]
    ['A', 'AA', 'AAA', 'AARDVARK', 'AARDVARKS']
    >>> Lex.stop_words_[:5]
    ['A', 'ABOUT', 'ACROSS', 'AFTER', 'AGAIN']
    >>> round(Lex.overall_statistics_['average_length'], 0)
    8.0
    >>> Lex.lookup_string('MONKEY')
    'MONKEY'
    >>> Lex.lookup_string('SUPERCALIFRAGILISTICEXPIALIDOCIOUS')
    >>>
    >>> Lex.lookup_substring('TCHSTR')
    ['LATCHSTRING', 'LATCHSTRINGS']

    """


    def __init__(self) -> None:
        """Initialize the `Lexicon` instance."""

        super().__init__(store_uniques=True)

        # build lexicon -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        self._lexicon_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '_lexicon'
        )

        for file in sorted(glob.glob(os.path.join(self._lexicon_dir, '*.txt'))):
            with open(os.path.join(self._lexicon_dir, file)) as f:
                words = np.fromiter(f, dtype='<U40')
                words = np.char.replace(words, '\n', '')
                super().partial_fit(words)
        # END build lexicon -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # build stop_words -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _stop_words_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '_stop_words'
        )

        self._stop_words = []
        for file in sorted(glob.glob(os.path.join(_stop_words_dir, '*.txt'))):
            with open(os.path.join(_stop_words_dir, file)) as f:
                words = np.fromiter(f, dtype='<U40')
                words = np.char.replace(words, '\n', '')
                self._stop_words += list(map(str, words.tolist()))
        self._stop_words = sorted(self._stop_words)
        # END build stop_words -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # END init ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @property
    def lexicon_(self) -> list[str]:
        """A list of all the words in the pybear `Lexicon`.

        Returns
        -------
        uniques : list[str]
            A list of all the words in the pybear `Lexicon`.

        """

        return self.uniques_


    @property
    def stop_words_(self) -> list[str]:
        """The list of pybear stop words.

        The words are the most frequent words in an arbitrary
        multi-million-word corpus scraped from the internet.

        Returns
        -------
        _stop_words : list[str]
            The list of pybear stop words.

        """

        return self._stop_words


    def _reset(self):
        """Blocked."""
        raise AttributeError(f"'_reset' is blocked")


    def get_params(self, deep:bool = True):
        """Blocked."""
        raise AttributeError(f"'get_params' is blocked")


    def set_params(self, deep:bool = True):
        """Blocked."""
        raise AttributeError(f"'set_params' is blocked")


    def partial_fit(self, X:Any, y:Any = None):
        """Blocked."""
        raise AttributeError(f"'partial_fit' is blocked")


    def fit(self, X:Any, y:Any = None):
        """Blocked."""
        raise AttributeError(f"'fit' is blocked")


    def transform(self, X:Any):
        """Blocked."""
        raise AttributeError(f"'transform' is blocked")


    def fit_transform(self, X:Any):
        """Blocked."""
        raise AttributeError(f"'fit_transform' is blocked")


    def score(self, X:Any, y:Any = None):
        """Blocked."""
        raise AttributeError(f"'score' is blocked")


    def lookup_substring(
        self,
        pattern: str | re.Pattern[str]
    ) -> list[str]:
        """Use string literals or regular expressions to look for substring
        matches in the `Lexicon`.

        `pattern` can be a literal string or a regular expression in a
        re.compile object. Return a list of all words in the `Lexicon`
        that contain the given substring pattern. Returns an empty list
        if there are no matches.

        pybear `Lexicon` forces this search to be case-sensitive. If you
        pass a re.compile object with an IGNORECASE flag, this method
        strips that flag and leaves the other flags intact.

        Parameters
        ----------
        pattern : str | re.Pattern[str]
            Character sequence or regular expression in a re.compile
            object to be looked up against the pybear `Lexicon`.

        Returns
        -------
        matches : list[str]
            List of all words in the pybear `Lexicon` that contain the
            given character substring. Returns an empty list if there
            are no matches.

        """


        # take out any IGNORECASE flag from a re.compile
        if isinstance(pattern, re.Pattern):
            new_flags = pattern.flags & ~re.I
            # Recreate the pattern with the updated flags
            pattern = re.compile(pattern.pattern, new_flags)

        return super().lookup_substring(pattern, case_sensitive=True)


    def lookup_string(
        self,
        pattern: str | re.Pattern[str]
    ) -> list[str]:
        """Use string literals or regular expressions to look for full
        word matches in the `Lexicon`.

        `pattern` can be a literal string or a regular expression in a
        re.compile object. Return a list of all words in the `Lexicon`
        that completely match the given pattern. Returns an empty list
        if there are no matches.

        pybear `Lexicon` forces this search to be case-sensitive. If you
        pass a re.compile object with an IGNORECASE flag, this method
        strips that flag and leaves the other flags intact.

        Parameters
        ----------
        pattern : str | re.Pattern[str]
            Character sequence or regular expression in a re.compile
            object to be looked up against the pybear `Lexicon`.

        Returns
        -------
        matches : list[str]
            List of all full words in the pybear `Lexicon` that match
            the pattern. Returns an empty list if there are no matches.

        """

        # take out any IGNORECASE flag from a re.compile
        if isinstance(pattern, re.Pattern):
            new_flags = pattern.flags & ~re.I
            # Recreate the pattern with the updated flags
            pattern = re.compile(pattern.pattern, new_flags)

        return super().lookup_string(pattern, case_sensitive=True)


    def find_duplicates(self) -> dict[str, int]:
        """Find any duplicates in the `Lexicon`.

        If any, display to screen and return as Python dictionary with
        frequencies.

        Returns
        -------
        dict[str, int]:
            Any duplicates in the pybear `Lexicon` and their frequencies.

        """

        return _find_duplicates(self.string_frequency_)


    def check_order(self) -> list[str]:
        """Determine if the lexicon files are out of alphabetical order.

        Compare the words as stored against a sorted vector of the words.
        Displays any out-of-order words to screen and return a Python list
        of the words.

        Returns
        -------
        list[str]:
            Vector of any out-of-sequence words in the `Lexicon`.

        """

        return _check_order(self.lexicon_)


    def add_words(
        self,
        WORDS:str | Sequence[str],
        character_validation:bool = True,
        majuscule_validation:bool = True,
        file_validation:bool = True
    ) -> None:
        """Silently update the pybear `Lexicon` text files with the given
        words.

        Words that are already in the `Lexicon` are silently ignored.
        This is very much a case-sensitive operation.

        The 'validation' parameters allow you to disable the pybear
        `Lexicon` rules. The pybear `Lexicon` does not allow any
        characters that are not one of the 26 letters of the English
        alphabet. Numbers, spaces, and punctuation, for example, are not
        allowed in the formal pybear Lexicon. Also, the pybear Lexicon
        requires that all entries in the lexicon be MAJUSCULE, i.e.,
        upper-case. The published pybear `Lexicon` will always follow
        these rules. When the validation is used, it ensures the integrity
        of the `Lexicon`. However, the user can override this validation
        for local copies of `Lexicon` by setting `character_validation`,
        `majuscule_validation`, and / or `file_validation` to False. If
        you want your `Lexicon` to have strings that contain numbers,
        spaces, punctuation, and have different cases, then set the
        validation to False and add your strings to the `Lexicon` via
        this method.

        pybear stores words in the `Lexicon` text files based on the
        first character of the string. So a word like 'APPLE' is stored
        in a file named 'lexicon_A' (this is the default pybear way.) A
        word like 'apple' would be stored in a file named 'lexicon_a'.
        Keep in mind that the pybear `Lexicon` is built with all
        capitalized words and file names and these are the only ones
        that exist out of the box. If you were to turn off the majuscule
        validation and file validation' and pass the word 'apple' to
        this method, it will NOT append 'APPLE' to the 'lexicon_A' file,
        a new `Lexicon` file called 'lexicon_a' will be created and the
        word 'apple' will be put into it.

        The `Lexicon` instance reloads the `Lexicon` from disk and
        refills the attributes when update is complete.

        Parameters
        ----------
        WORDS : str | Sequence[str]
            The word or words to be added to the pybear `Lexicon`. Cannot
            be an empty string or an empty sequence. Words that are
            already in the `Lexicon` are silently ignored.
        character_validation : bool, default = True
            Whether to apply pybear `Lexicon` character validation to
            the word or sequence of words. pybear `Lexicon` allows only
            the 26 letters in the English language, no others. No spaces,
            no hyphens, no apostrophes. If True, any non-alpha characters
            will raise an exception during validation. If False, any
            string character is accepted.
        majuscule_validation : bool, default = True
            Whether to apply pybear `Lexicon` majuscule validation to the
            word or sequence of words. The pybear `Lexicon` requires all
            characters be majuscule, i.e., EVERYTHING MUST BE UPPER-CASE.
            If True, any non-majuscule characters will raise an exception
            during validation. If False, any case is accepted.
        file_validation : bool, default = True
            Whether to apply pybear `Lexicon` file name validation to the
            word or sequence of words. The formal pybear `Lexicon` only
            allows words to start with the 26 upper-case letters of the
            English alphabet (which then dictates the file name in which
            it will be stored). If True, any disallowed characters in the
            first position will raise an exception during validation. If
            False, any character is accepted, which may then necessitate
            that a file be created.

        Returns
        -------
        None

        """


        _add_words(
            WORDS,
            self._lexicon_dir,
            character_validation=character_validation,
            majuscule_validation=majuscule_validation,
            file_validation=file_validation
        )

        # _add_words writes new words to files. need to re-read files
        # into the instance and rebuild the lexicon and attributes.
        self.__init__()


    def delete_words(
        self,
        WORDS: str | Sequence[str]
    ):
        """Remove the given word(s) from the pybear `Lexicon` text files.
        Case sensitive! Any words that are not in the pybear `Lexicon`
        are silently ignored.

        Parameters
        ----------
        WORDS : str | Sequence[str]
            The word or words to remove from the pybear `Lexicon`. Cannot
            be an empty string or an empty sequence.

        Returns
        -------
        None

        """


        _delete_words(
            WORDS,
            self._lexicon_dir
        )

        # _delete_words removes words from the files. need to re-read
        # files into the instance and rebuild the attributes.
        self.__init__()








