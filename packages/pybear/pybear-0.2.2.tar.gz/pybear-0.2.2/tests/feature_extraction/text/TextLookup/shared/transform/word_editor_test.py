# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from unittest.mock import patch

import io

from pybear.feature_extraction.text._TextLookup._shared._transform._word_editor \
    import _word_editor



class TestWordEditor:


    @pytest.mark.parametrize('_word', ('MILK', 'BAGEL', 'CHEESE'))
    def test_accuracy(self, _word):

        user_inputs = "CHERRY\nY\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = _word_editor(_word, f'Enter something to eat instead of *{_word}* ')

        assert out == 'CHERRY'






