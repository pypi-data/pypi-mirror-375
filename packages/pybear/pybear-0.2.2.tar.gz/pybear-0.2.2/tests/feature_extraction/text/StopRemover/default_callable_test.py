# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._StopRemover.StopRemover import StopRemover

import pytest



class TestDefaultCallable:

    # def _default_callable(_str1: str, _str2: str) -> bool:

    def test_default_callable_escapes_words_from_text(self):

        assert StopRemover._default_callable(
            r'^\n\t\s$',
            r'^\n\t\s$'
        ) is True

        assert StopRemover._default_callable(
            r'^\n\t\s$',
            r'^\n\t\s%'
        ) is False


    @pytest.mark.parametrize('text_word', ('^/n/s/t$', 'THIS', 'IS', 'A', 'TEST'))
    @pytest.mark.parametrize('stop_word', ('TESTING', 'TEST', '123', '^/n/s/t$'))
    def test_default_callable_accuracy(self, text_word, stop_word):

        assert StopRemover._default_callable(
            text_word,
            stop_word
        ) is (text_word == stop_word)










