# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextStatistics._lookup._lookup_string \
    import _lookup_string



class TestLookupString:


    @staticmethod
    @pytest.fixture(scope='function')
    def uniques():
        return [
            'aardvark', 'AARDvark', 'aardVARK', 'AARDVARK',
            'aardwolf', 'AARDwolf', 'aardWOLF', 'AARDWOLF',
        ]

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # pattern -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_pattern',
        (-2.7, -1, 0, 1, 2.7, True, None, [0,1], ('a', ), {'a': 1}, lambda x: x)
    )
    def test_blocks_non_str_non_compile(self, junk_pattern, uniques):

        with pytest.raises(TypeError):
            _lookup_string(junk_pattern, uniques, True)


    @pytest.mark.parametrize('pattern',
        ('green', 'eggs', re.compile('and', re.I), re.compile('ham'))
    )
    def test_accepts_str_compile_pattern(self, pattern, uniques):

        _lookup_string('look me up', uniques, _case_sensitive=True)
    # END pattern -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # uniques -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_uniques',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1, ), {'a': 1}, lambda x: x)
    )
    def test_blocks_non_sequence_str_uniques(self, junk_uniques):

        with pytest.raises(TypeError):
            _lookup_string('look me up', junk_uniques, _case_sensitive=False)


    def test_allows_empty_uniques(self):
        _lookup_string('look me up', [], _case_sensitive=False)


    @pytest.mark.parametrize('container', (set, tuple, list, np.ndarray))
    def test_accepts_sequence_str_uniques(self, container, uniques):

        if container is np.ndarray:
            uniques = np.array(uniques)
        else:
            uniques = container(uniques)

        assert isinstance(uniques, container)

        _lookup_string('look me up', uniques, _case_sensitive=False)
    # END uniques -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # case_sensitive -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_case_sensitive',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], ('a', ), {'a': 1}, lambda x: x)
    )
    def test_blocks_non_bool_case_sensitive(self, junk_case_sensitive, uniques):

        with pytest.raises(TypeError):
            _lookup_string('look me up', uniques, junk_case_sensitive)


    @pytest.mark.parametrize('case_sensitive', (True, False))
    def test_accepts_bool_case_sensitive(self, case_sensitive, uniques):

        _lookup_string('look me up', uniques, case_sensitive)
    # END case_sensitive -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_empty_uniques_returns_empty(self):
        out = _lookup_string('this is only a test', [], _case_sensitive=False)
        assert isinstance(out, list)
        assert len(out) == 0


    def test_empty_char_seq_does_not_match(self):
        out = _lookup_string('', ['A', 'AA', 'AAA', 'AARDVARK'])
        assert len(out) == 0


    def test_substring_does_not_match(self, uniques):
        out = _lookup_string(re.compile('AARD', re.I), uniques)
        assert len(out) == 0


    def test_literal_is_escaped(self):
        out = _lookup_string(r'^\s\n\t$', ['green', r'^\s\n\t$', 'and', 'ham'])
        assert isinstance(out, list)
        assert np.array_equal(out, [r'^\s\n\t$'])


    @pytest.mark.parametrize('case_sensitive', (True, False))
    @pytest.mark.parametrize('test_pattern',
        ('AARDVARK', 'aardwolf', 'JACKAL',  re.compile('aard[a-z+]'),
        re.compile('[A-Z+]WOLF', re.I), re.compile('MONGOOSE'))
    )
    @pytest.mark.parametrize('uniques_container', (tuple, list, np.ndarray))
    def test_accuracy(
        self, case_sensitive, test_pattern, uniques_container, uniques
    ):

        # dont test sets here, it messes up the order. we did prove above
        # that sets are accepted, though.

        if uniques_container is np.ndarray:
            uniques = np.array(uniques)
            assert isinstance(uniques, np.ndarray)
        else:
            uniques = uniques_container(uniques)
            assert isinstance(uniques, uniques_container)

        out = _lookup_string(
            test_pattern,
            uniques,
            _case_sensitive=case_sensitive
        )

        assert isinstance(out, list)

        if isinstance(test_pattern, str):
            if test_pattern == 'AARDVARK':
                if case_sensitive:
                    assert np.array_equal(out, ['AARDVARK'])
                elif not case_sensitive:
                    assert np.array_equal(
                        out,
                        ['AARDVARK', 'AARDvark', 'aardVARK', 'aardvark']
                    )
            elif test_pattern == 'aardwolf':
                if case_sensitive:
                    assert np.array_equal(out, ['aardwolf'])
                elif not case_sensitive:
                    assert np.array_equal(
                        out,
                        ['AARDWOLF', 'AARDwolf', 'aardWOLF', 'aardwolf']
                    )
            elif test_pattern == 'JACKAL':
                if case_sensitive:
                    assert len(out) == 0
                elif not case_sensitive:
                    assert len(out) == 0
            else:
                raise Exception
        elif isinstance(test_pattern, re.Pattern):
            if test_pattern.pattern == 'aard[a-z+]':
                if test_pattern.flags == 0:
                    assert np.array_equal(out, ['aardvark', 'aardwolf'])
                elif test_pattern.flags == re.I:
                    assert np.array_equal(
                        out,
                        ['AARDVARK', 'AARDvark', 'aardVARK', 'aardvark']
                    )
            elif test_pattern.pattern == '[A-Z+]WOLF':
                if test_pattern.flags == 0:
                    assert np.array_equal(out, ['AARDWOLF'])
                elif test_pattern.flags == re.I:
                    assert np.array_equal(
                        out,
                        ['AARDVARK', 'AARDvark', 'aardVARK', 'aardvark']
                    )
            elif test_pattern.pattern == 'MONGOOSE':
                if test_pattern.flags == 0:
                    assert len(out) == 0
                elif test_pattern.flags == re.I:
                    assert len(out) == 0
            else:
                raise Exception
        else:
            raise Exception















