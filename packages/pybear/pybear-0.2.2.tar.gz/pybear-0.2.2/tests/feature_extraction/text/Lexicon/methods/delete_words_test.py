# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import os

import pytest
import numpy as np

from pybear.feature_extraction.text._Lexicon._methods._delete_words import \
    _delete_words



class TestDeleteWords:

    # def _delete_words(
    #     WORDS: str | Sequence[str],
    #     lexicon_folder_path: str
    # ) -> None:


    # fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @staticmethod
    @pytest.fixture(scope='module')
    def local_dir():
        return os.path.dirname(os.path.abspath(__file__))


    @staticmethod
    @pytest.fixture(scope='function')
    def dummy_txt_file(local_dir):

        DUMMY_WORDS = ['BALEEN', 'BEHOOVE', 'BISMUTH', 'BONKERS', 'BUMPKIN']

        with open(rf"{os.path.join(local_dir, 'lexicon_B.txt')}", 'w') as f:
            for word in DUMMY_WORDS:
                f.write(f'{word}\n')

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_WORDS',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_WORDS(self, junk_WORDS):

        with pytest.raises(TypeError):

            _delete_words(
                junk_WORDS,
                lexicon_folder_path='sam i am'
            )


    @pytest.mark.parametrize('junk_path',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_lexicon_folder_path(self, junk_path):

        with pytest.raises(TypeError):

            _delete_words(
                'ULTRACREPIDARIAN',
                lexicon_folder_path=junk_path
            )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_single_string_works(self, local_dir, dummy_txt_file):

        # remove the word from the dummy file via _delete_words
        _delete_words(
            'BALEEN',
            local_dir
        )

        # after the remove is done (hopefully), read the file and compare
        # against expected
        with open(rf"{os.path.join(local_dir, 'lexicon_B.txt')}", 'r') as f:
            NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')

        NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
        NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

        EXP = ['BEHOOVE', 'BISMUTH', 'BONKERS', 'BUMPKIN']

        assert np.array_equal(NEW_SUB_LEXICON, EXP)

        os.remove(rf"{os.path.join(local_dir, 'lexicon_B.txt')}")


    def test_sequence_of_strings_works(self, local_dir, dummy_txt_file):

        # add the new words to the dummy file via _add_words
        _delete_words(
            ['BALEEN', 'BISMUTH', 'BUMPKIN'],
            local_dir
        )

        # after the add is done (hopefully), read the file and compare
        # against expected
        with open(rf"{os.path.join(local_dir, 'lexicon_B.txt')}", 'r') as f:
            NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')

        NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
        NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

        EXP = ['BEHOOVE', 'BONKERS']
        assert np.array_equal(NEW_SUB_LEXICON, EXP)

        os.remove(rf"{os.path.join(local_dir, 'lexicon_B.txt')}")


    def test_not_in_lexicon(self, local_dir, dummy_txt_file):

        # this should silently skip
        _delete_words(
            'BAYONET',
            local_dir
        )

        # after the remove is done (hopefully), read the file and compare
        # against expected
        # nothing should be deleted
        with open(rf"{os.path.join(local_dir, 'lexicon_B.txt')}", 'r') as f:
            NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')

        NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
        NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

        EXP = ['BALEEN', 'BEHOOVE', 'BISMUTH', 'BONKERS', 'BUMPKIN']

        assert np.array_equal(NEW_SUB_LEXICON, EXP)

        os.remove(rf"{os.path.join(local_dir, 'lexicon_B.txt')}")


    def test_when_file_doesnt_exist(self, local_dir):

        # previously, this raised raised errors for no file
        # with pytest.raises((FileNotFoundError, ValueError)):
        #     FileNotFoundError by _delete_words when _identify_sublexicon not blocking
        #     ValueError by _identify_sublexicon when validation there is on

        # now should silently skip a file that doesnt exist (and therefore
        # cant contain the word you're trying to remove)
        _delete_words(
            '@GMAIL.COM',
            local_dir
        )










