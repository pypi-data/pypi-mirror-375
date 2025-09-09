# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._Lexicon._methods._identify_sublexicon \
    import _identify_sublexicon



class TestIdentifySublexicon:


    @pytest.mark.parametrize('junk_WORDS',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_WORDS(self, junk_WORDS):

        with pytest.raises(TypeError):
            _identify_sublexicon(junk_WORDS)


    @pytest.mark.parametrize('junk_fv',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0, 1], (1,), {1,2}, {'a': 1},
         lambda x: x)
    )
    def test_rejects_junk_file_validation(self, junk_fv):

        with pytest.raises(TypeError):
            _identify_sublexicon('EGGS', file_validation=junk_fv)


    @pytest.mark.parametrize('bad_first_char',
        ('-infinity', '!hola', '%up', '&how', '(no)', '$one', '@gmail')
    )
    @pytest.mark.parametrize('fv', (True, False))
    def test_conditionally_rejects_bad_first_char(self, bad_first_char, fv):

        if fv is True:
            with pytest.raises(ValueError):
                _identify_sublexicon(bad_first_char, file_validation=fv)
        else:
            _identify_sublexicon(bad_first_char, file_validation=fv)


    def test_accuracy(self):

        out = _identify_sublexicon(['I', 'am', 'Sam', 'Sam', 'I', 'am'])
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['I', 'S', 'a'])


        out = _identify_sublexicon(['I', 'do', 'not', 'like', 'green', 'eggs'])
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['I', 'd', 'e', 'g', 'l', 'n'])


        out = _identify_sublexicon(['AND', 'HAM', 'SAM', 'I', 'AM'])
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equal(out, ['A', 'H', 'I', 'S'])






