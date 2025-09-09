# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import os

import pytest
import numpy as np

from pybear.feature_extraction.text._Lexicon._methods._add_words import _add_words





class TestAddWords:


    # fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @staticmethod
    @pytest.fixture(scope='module')
    def local_dir():
        return os.path.dirname(os.path.abspath(__file__))


    @staticmethod
    @pytest.fixture(scope='function')
    def dummy_txt_file(local_dir):

        DUMMY_WORDS = ['ALLIGATOR', 'AMPLIFIER', 'ANCHOVY', 'AORTA', 'APPLY']

        with open(rf"{os.path.join(local_dir, 'lexicon_A.txt')}", 'w') as f:
            for word in DUMMY_WORDS:
                f.write(f'{word}\n')

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_WORDS',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_WORDS(self, junk_WORDS):

        with pytest.raises(TypeError):

            _add_words(
                junk_WORDS,
                lexicon_folder_path='sam i am',
                character_validation=False,
                majuscule_validation=False
            )


    @pytest.mark.parametrize('junk_path',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_lexicon_folder_path(self, junk_path):

        with pytest.raises(TypeError):

            _add_words(
                'ULTRACREPIDARIAN',
                lexicon_folder_path=junk_path,
                character_validation=False,
                majuscule_validation=False
            )


    @pytest.mark.parametrize('junk_cv',
        (-2.7, -1, 0, 1, 2.7, None, [0, 1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_character_validation(self, junk_cv):

        with pytest.raises(TypeError):

            _add_words(
                'CREPUSCULAR',
                lexicon_folder_path='/somewhere/out/there',
                character_validation=junk_cv,
                majuscule_validation=False
            )

    @pytest.mark.parametrize('junk_mv',
        (-2.7, -1, 0, 1, 2.7, None, [0, 1], (1,), {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_majuscule_validation(self, junk_mv):
        with pytest.raises(TypeError):
            _add_words(
                'PETRICHOR',
                lexicon_folder_path='/somewhere/out/there',
                character_validation=False,
                majuscule_validation=junk_mv
            )

    @pytest.mark.parametrize('junk_fv',
        (-2.7, -1, 0, 1, 2.7, None, [0, 1], (1,), {1, 2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_file_validation(self, junk_fv):
        with pytest.raises(TypeError):
            _add_words(
                'PETRICHOR',
                lexicon_folder_path='/somewhere/out/there',
                character_validation=False,
                majuscule_validation=False,
                file_validation=junk_fv
            )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('character_validation', (True, False))
    @pytest.mark.parametrize('majuscule_validation', (True, False))
    @pytest.mark.parametrize('file_validation', (True, False))
    def test_single_string_works(
        self, local_dir, dummy_txt_file, character_validation,
        majuscule_validation, file_validation
    ):

        # all validations should pass because using all caps and no junk chars

        # add the new word to the dummy file via _add_words
        _add_words(
            'AMSTERDAM',
            local_dir,
            character_validation=character_validation,
            majuscule_validation=majuscule_validation,
            file_validation=file_validation
        )

        # after the add is done (hopefully), read the file and compare
        # against expected
        with open(rf"{os.path.join(local_dir, 'lexicon_A.txt')}", 'r') as f:
            NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')


        NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
        NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

        EXP = [
            'ALLIGATOR', 'AMPLIFIER', 'AMSTERDAM', 'ANCHOVY', 'AORTA', 'APPLY'
        ]

        assert np.array_equal(NEW_SUB_LEXICON, EXP)

        os.remove(rf"{os.path.join(local_dir, 'lexicon_A.txt')}")


    @pytest.mark.parametrize('character_validation', (True, False))
    @pytest.mark.parametrize('majuscule_validation', (True, False))
    @pytest.mark.parametrize('file_validation', (True, False))
    def test_sequence_of_strings_works(
        self, local_dir, dummy_txt_file, character_validation,
        majuscule_validation, file_validation
    ):

        # all validations should pass because using all caps and no junk chars

        # add the new words to the dummy file via _add_words
        _add_words(
            ['ACKNOWLEDGE', 'AMSTERDAM', 'ANTIMONY', 'AQUEOUS'],
            local_dir,
            character_validation=character_validation,
            majuscule_validation=majuscule_validation,
            file_validation=file_validation
        )

        # after the add is done (hopefully), read the file and compare
        # against expected
        with open(rf"{os.path.join(local_dir, 'lexicon_A.txt')}", 'r') as f:
            NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')


        NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
        NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

        EXP = [
            'ACKNOWLEDGE', 'ALLIGATOR', 'AMPLIFIER', 'AMSTERDAM',
            'ANCHOVY', 'ANTIMONY', 'AORTA', 'APPLY', 'AQUEOUS'
        ]
        assert np.array_equal(NEW_SUB_LEXICON, EXP)

        os.remove(rf"{os.path.join(local_dir, 'lexicon_A.txt')}")


    @pytest.mark.parametrize('character_validation', (True, False))
    @pytest.mark.parametrize('majuscule_validation', (True, False))
    @pytest.mark.parametrize('file_validation', (True, ))
    def test_when_a_file_would_be_created_but_blocked(
        self, local_dir, character_validation, majuscule_validation,
        file_validation
    ):

        if character_validation:
            # character blocks first in _validate_word_input
            _error = ValueError
        elif majuscule_validation:
            # majuscule blocks second in _validate_word_input
            _error = ValueError
        else:
            # if not blocked by _validate_word_input,
            # but blocked by _identify_sublexicon file_validation ValueError
            _error = ValueError

        with pytest.raises(_error):
            _add_words(
                '@gmail.com',
                local_dir,
                character_validation=character_validation,
                majuscule_validation=majuscule_validation,
                file_validation=file_validation
            )

        del _error


    @pytest.mark.parametrize('character_validation', (True, False))
    @pytest.mark.parametrize('majuscule_validation', (True, False))
    @pytest.mark.parametrize('file_validation', (False, ))
    def test_when_a_file_would_be_created_not_blocked(
        self, local_dir, character_validation, majuscule_validation,
        file_validation
    ):

        if character_validation or majuscule_validation:
            # character blocks first in _validate_word_input
            # majuscule blocks second in _validate_word_input
            with pytest.raises(ValueError):
                _add_words(
                    ['@gmail.com', '@msn.com', '@hotmail.com'],
                    local_dir,
                    character_validation=character_validation,
                    majuscule_validation=majuscule_validation,
                    file_validation=file_validation
                )

        else:
            # a file should be created with the 3 strings in it

            _add_words(
                ['@gmail.com', '@msn.com', '@hotmail.com'],
                local_dir,
                character_validation=character_validation,
                majuscule_validation=majuscule_validation,
                file_validation=file_validation
            )

            # after the add is done (hopefully), read the file and compare
            # against expected
            with open(rf"{os.path.join(local_dir, 'lexicon_@.txt')}", 'r') as f:
                NEW_SUB_LEXICON = np.fromiter(f, dtype='<U30')

            NEW_SUB_LEXICON = np.char.replace(NEW_SUB_LEXICON, f'\n', f'')
            NEW_SUB_LEXICON = list(map(str, NEW_SUB_LEXICON))

            EXP = sorted(['@gmail.com', '@msn.com', '@hotmail.com'])
            assert np.array_equal(NEW_SUB_LEXICON, EXP)

            os.remove(rf"{os.path.join(local_dir, 'lexicon_@.txt')}")





