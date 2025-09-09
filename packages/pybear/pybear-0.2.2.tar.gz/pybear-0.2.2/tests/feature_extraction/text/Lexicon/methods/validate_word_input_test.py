# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._Lexicon._methods._validate_word_input \
    import _validate_word_input




class TestValidateWordInput:


    # character_validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_cv',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_character_validation(self, junk_cv):

        with pytest.raises(TypeError):

            _validate_word_input(
                'something',
                character_validation=junk_cv,
                majuscule_validation=False
            )


    @pytest.mark.parametrize('_cv', (True, False))
    def test_accepts_bool_character_validation(self, _cv):

        _validate_word_input(
            'something', character_validation=_cv, majuscule_validation=False
        )

    # END character_validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # majuscule_validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_mv',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_majuscule_validation(self, junk_mv):

        with pytest.raises(TypeError):

            _validate_word_input('SOMETHING', majuscule_validation=junk_mv)


    @pytest.mark.parametrize('_mv', (True, False))
    def test_accepts_bool_majuscule_validation(self, _mv):

        _validate_word_input('SOMETHING', majuscule_validation=_mv)

    # END majuscule_validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('junk_words',
        (-2.7, -1, 0, 1, 2.7, True, None, [0,1], (1,), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_WORDS(self, junk_words):

        with pytest.raises(TypeError):

            _validate_word_input(
                junk_words, character_validation=False, majuscule_validation=False
            )


    @pytest.mark.parametrize('_words', ('priceless', 'valuable', 'precious'))
    def test_accepts_WORDS_as_str(self, _words):

        _validate_word_input(
            _words, character_validation=False, majuscule_validation=False
        )


    def test_rejects_empty_WORDS_as_str(self):

        with pytest.raises(TypeError):
            _validate_word_input(
                '', character_validation=False, majuscule_validation=False
            )


    @pytest.mark.parametrize('_format', (list, tuple, set, np.ndarray))
    def test_accepts_WORDS_as_sequence_of_str(self, _format):

        _words = ['priceless', 'valuable', 'precious']

        if _format is np.ndarray:
            _words = np.array(_words)
            assert isinstance(_words, np.ndarray)
        else:
            _words = _format(_words)
            assert isinstance(_words, _format)


        _validate_word_input(
            _words, character_validation=False, majuscule_validation=False
        )


    def test_rejects_empty_WORDS_as_sequence_of_str(self):

        with pytest.raises(TypeError):
            _validate_word_input(
                [], character_validation=False, majuscule_validation=False
            )


    @pytest.mark.parametrize('_words',
        ('what', 'WHAT', 'WHAT!?', 'what!?', ['I', 'am', 'Sam!'], ['SAM-I-AM'])
    )
    @pytest.mark.parametrize('_cv', (True, False))
    @pytest.mark.parametrize('_mv', (True, False))
    def test_accuracy(self, _words, _cv, _mv):

        if _cv is False and _mv is False:
            # should pass any strings

            out = _validate_word_input(
                _words,
                character_validation=_cv,
                majuscule_validation=_mv
            )

            assert out is None

        elif _cv is True and _mv is False:

            if _words in ['WHAT!?', 'what!?', ['I', 'am', 'Sam!'], ['SAM-I-AM']]:
                with pytest.raises(ValueError):
                    _validate_word_input(
                        _words,
                        character_validation=_cv,
                        majuscule_validation=_mv
                    )
            else:
                _validate_word_input(
                    _words,
                    character_validation=_cv,
                    majuscule_validation=_mv
                )

        elif _cv is False and _mv is True:

            if _words in ['what', 'what!?', ['I', 'am', 'Sam!']]:
                with pytest.raises(ValueError):
                    _validate_word_input(
                        _words,
                        character_validation=_cv,
                        majuscule_validation=_mv
                    )
            else:
                _validate_word_input(
                    _words,
                    character_validation=_cv,
                    majuscule_validation=_mv
                )


        elif _cv is True and _mv is True:

            if _words == 'WHAT':

                _validate_word_input(
                    _words,
                    character_validation=_cv,
                    majuscule_validation=_mv
                )
            else:

                with pytest.raises(ValueError):
                    _validate_word_input(
                        _words,
                        character_validation=_cv,
                        majuscule_validation=_mv
                    )

        else:
            raise Exception










