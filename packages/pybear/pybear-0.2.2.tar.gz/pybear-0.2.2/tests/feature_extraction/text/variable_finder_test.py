# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import os

from pybear.feature_extraction.text.variable_finder import variable_finder



class TestVariableFinder:



    @pytest.mark.parametrize('junk_text',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    def test_text_rejects_junk(self, junk_text):

        with pytest.raises(TypeError):
            variable_finder(text=junk_text, filepath=None)


    @pytest.mark.parametrize('junk_filepath',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    def test_filepath_rejects_junk(self, junk_filepath):

        with pytest.raises(TypeError):
            variable_finder(text=None, filepath=junk_filepath)


    @pytest.mark.parametrize('_text', (None, 'some words to search'))
    @pytest.mark.parametrize('_fp', (None, f'./some_fake_path'))
    def test_can_only_pass_one_thing(self, _text, _fp):

        if _text is None and _fp is None:
            # nothing passed
            with pytest.raises(ValueError):
                variable_finder(_text, _fp)
        elif _text is not None and _fp is not None:
            # both passed
            with pytest.raises(ValueError):
                variable_finder(_text, _fp)
        elif _text is not None:
            # only 'text' passed
            assert isinstance(variable_finder(_text, _fp), list)
        elif _fp is not None:
            # only 'filepath' passed
            # this should raise for invalid path
            with pytest.raises(FileNotFoundError):
                variable_finder(_text, _fp)


    @staticmethod
    @pytest.fixture(scope='function')
    def _words() -> str:
        return """
            test_1:bool = True
            self.test_2 = 'something'
            _test_3 = 'abc'
            def test_4(x:int, y:int, z:int):
                return x + y + z
            test_5: int | float | None = None
            class test_6(Object):
                pass
        """


    def test_accuracy_text(self, _words):

        out = variable_finder(text=_words)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for i in out)))

        assert 'test_1' in out
        assert 'self.test_2' in out
        assert '_test_3' in out
        assert 'def test_4' in out
        assert 'test_5' in out
        assert 'class test_6' in out


    def test_accuracy_filepath(self, _words):

        with open(r'test_dump', 'w') as f:
            f.write(_words)
            f.close()

        out = variable_finder(filepath=f'test_dump')
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for i in out)))

        assert 'test_1' in out
        assert 'self.test_2' in out
        assert '_test_3' in out
        assert 'def test_4' in out
        assert 'test_5' in out
        assert 'class test_6' in out

        os.remove('test_dump')







