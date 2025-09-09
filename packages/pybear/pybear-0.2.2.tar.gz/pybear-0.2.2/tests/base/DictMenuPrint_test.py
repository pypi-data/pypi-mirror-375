# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# See the sandbox file for an interactive assessment of display


import pytest
from unittest.mock import patch

import io

from pybear.base._DictMenuPrint import DictMenuPrint as DMP



class TestDMPInit:


    # VALIDATION ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    # MENU_DICT -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_MENU_DICT',
        (-2.7, 2.7, True, False, None, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    def test_MENU_DICT_rejects_non_dict(self, junk_MENU_DICT):

        with pytest.raises(TypeError):
            DMP(junk_MENU_DICT)


    @pytest.mark.parametrize('bad_MENU_DICT_key', (0, 1, 2.7, True, None, [0,1]))
    @pytest.mark.parametrize('bad_MENU_DICT_value', (0, 1, 2.7, True, None, [0,1]))
    def test_MENU_DICT_rejects_bad_dict(self, bad_MENU_DICT_key, bad_MENU_DICT_value):

        with pytest.raises(TypeError):
            DMP({bad_MENU_DICT_key: bad_MENU_DICT_value})


    def test_MENU_DICT_rejects_long_keys(self):

        with pytest.raises(ValueError):
            DMP({'AA': 'make chicken'})

        with pytest.raises(ValueError):
            DMP({'BBB': 'drink beer'})


    def test_MENU_DICT_rejects_empty(self):

        with pytest.raises(ValueError):
            DMP({})


    def test_MENU_DICT_accepts_good(self):
        DMP({'A': 'Test 1', 'B': 'Test 2'})
    # END MENU_DICT -- -- -- -- -- -- -- -- -- -- -- --

    # disp_width -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_disp_width',
        (-2.7, 2.7, True, False, None, 'trash', [0,1], (1,), {1,2}, {'A':1},
         lambda x: x)
    )
    def test_disp_width_rejects_non_integer(self, junk_disp_width):

        with pytest.raises(TypeError):
            DMP({'A': 'Test 1', 'B': 'Test 2'}, disp_width=junk_disp_width)


    @pytest.mark.parametrize('_disp_width', (-1, 0, 1))
    def test_disp_width_rejects_low_integer(self, _disp_width):
        with pytest.raises(ValueError):
            DMP({'A': 'Test 1', 'B': 'Test 2'}, disp_width=_disp_width)


    @pytest.mark.parametrize('_disp_width', (10, 80, 1000))
    def test_disp_width_accepts_good_integer(self, _disp_width):
        DMP({'A': 'Test 1', 'B': 'Test 2'}, disp_width=_disp_width)
    # END disp_width -- -- -- -- -- -- -- -- -- -- -- --

    # fixed_col_width -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_fixed_col_width',
        (-2.7, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, {'A':1},
         lambda x: x)
    )
    def test_fixed_col_width_rejects_non_integer_None(
        self, junk_fixed_col_width
    ):

        with pytest.raises(TypeError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2'},
                fixed_col_width=junk_fixed_col_width
            )


    @pytest.mark.parametrize('_fixed_col_width', (-1, 0, 1))
    def test_fixed_col_width_rejects_low_integer(self, _fixed_col_width):

        with pytest.raises(ValueError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2'},
                fixed_col_width=_fixed_col_width
            )


    @pytest.mark.parametrize('_fixed_col_width', (10, 80, 1000, None))
    def test_fixed_col_width_accepts_good_integer_None(self, _fixed_col_width):
        DMP(
            {'A': 'Test 1', 'B': 'Test 2'},
            disp_width=_fixed_col_width or 1000,   # must be >= fixed_col_width
            fixed_col_width=_fixed_col_width
        )
    # END fixed_column_width -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_allowed',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (1,), {1,2}, {'A':1}, lambda x: x)
    )
    def test_allowed_rejects_non_str_None(
        self, junk_allowed
    ):

        with pytest.raises(TypeError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2'},
                allowed=junk_allowed
            )


    def test_allowed_must_be_in_MENU_DICT(self):

        with pytest.raises(ValueError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'},
                allowed='q'
            )


    @pytest.mark.parametrize('_allowed', ('abc', 'ABC', '!$!(##$', None))
    def test_allowed_accepts_str_None(
        self, _allowed
    ):
        DMP(
            {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
             'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
             '(': 'Test 9', '#': 'Test 10'},
            allowed=_allowed
        )
    # END allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # disallowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_disallowed',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (1,), {1,2}, {'A':1}, lambda x: x)
    )
    def test_disallowed_rejects_non_str_None(
        self, junk_disallowed
    ):

        with pytest.raises(TypeError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2'},
                disallowed=junk_disallowed
            )


    def test_disallowed_must_be_in_MENU_DICT(self):

        with pytest.raises(ValueError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'},
                disallowed='q'
            )


    @pytest.mark.parametrize('_disallowed', ('abc', 'ABC', '!$!(##$', None))
    def test_disallowed_accepts_str_None(
        self, _disallowed
    ):
        DMP(
            {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
             'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
             '(': 'Test 9', '#': 'Test 10'},
            disallowed=_disallowed
        )
    # END allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # TEST EXCEPTS allowed & disallowed PASSED -- -- -- -- -- -- -- -- -- --
    def test_cant_take_both_allowed_and_disallowed(self):
        DICT = {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3'}
        with pytest.raises(ValueError):
            DMP(DICT, allowed='A', disallowed='B')
    # END TEST EXCEPTS allowed & disallowed PASSED -- -- -- -- -- -- -- -- --

    # END VALIDATION ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


class TestDMPchoose:


    # VALIDATION ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    # allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_allowed',
        (-2.7, -1, 0, 1, 2.7, True, False, [0, 1], (1,), {1, 2}, {'A': 1}, lambda x: x)
    )
    def test_allowed_rejects_non_str_None(
            self, junk_allowed
    ):
        with pytest.raises(TypeError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2'}
            ).choose('pick one > ', allowed=junk_allowed)


    def test_allowed_must_be_in_MENU_DICT(self):

        with pytest.raises(ValueError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'}
            ).choose('pick one > ', allowed='q')


    @pytest.mark.parametrize('_allowed', ('abc', 'ABC', '!$!(##$', None))
    def test_allowed_accepts_str_None(
            self, _allowed
    ):

        user_inputs = (_allowed[0] if _allowed else 'A') + f"\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a': 'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'},
            ).choose('pick one an move on > ', allowed=_allowed)

    # END allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # disallowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_disallowed',
        (-2.7, -1, 0, 1, 2.7, True, False, [0, 1], (1,), {1, 2}, {'A': 1}, lambda x: x)
    )
    def test_disallowed_rejects_non_str_None(
            self, junk_disallowed
    ):
        with pytest.raises(TypeError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a': 'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'},
            ).choose(
                'pick one and get on with your life > ',
                disallowed=junk_disallowed
            )


    def test_disallowed_must_be_in_MENU_DICT(self):

        with pytest.raises(ValueError):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a':'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'}
            ).choose('pick one an move on > ', disallowed='q')


    @pytest.mark.parametrize('_disallowed', ('abc', 'aBC', '!$!(##$', None))
    def test_disallowed_accepts_str_None(
            self, _disallowed
    ):

        user_inputs = "A\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(
                {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3', 'a': 'Test 4',
                 'b': 'Test 5', 'c': 'Test 6', '!': 'Test 7', '$': 'Test 8',
                 '(': 'Test 9', '#': 'Test 10'}
            ).choose(
                'make up your mind already > ',
                disallowed=_disallowed
            )

    # END allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # TEST EXCEPTS allowed & disallowed PASSED -- -- -- -- -- -- -- -- -- --
    def test_cant_take_both_allowed_and_disallowed(self):

        DICT = {'A': 'Test 1', 'B': 'Test 2', 'C': 'Test 3'}
        with pytest.raises(ValueError):
            DMP(DICT).choose(
                'I dont know what I want > ',
                allowed='A',
                disallowed='B'
            )
    # END TEST EXCEPTS allowed & disallowed PASSED -- -- -- -- -- -- -- -- --

    # END VALIDATION ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **



class TestAccuracy:


    @pytest.mark.parametrize('_disp_width', (50, 120))
    def test_margin_of_many_small_options(self, capsys, _disp_width):

        VALUES = [f'Test{_}' for _ in range(0, 27)]
        DICT = dict((zip(list('ABCDEFGHIJKLMNOPQURSTUVWXYZ'), VALUES)))

        user_inputs = "A\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(DICT, disp_width=_disp_width).choose('pick one > ')

        captured = capsys.readouterr().out.strip().split('\n')

        for idx, line in enumerate(captured[:-1]):
            # skip the last row, it is the prompt
            # second to last row might be short, just see something is there
            if idx == len(captured) - 2:
                assert len(line) > 0
            else:
                assert 0.8*_disp_width <= len(line) <= _disp_width


    @pytest.mark.parametrize('_disp_width', (90, 140))
    def test_margin_of_many_medium_options(self, capsys, _disp_width):

        VALUES = [f'Test of many medium-sized options{_}' for _ in range(0, 27)]
        DICT = dict((zip(list('ABCDEFGHIJKLMNOPQURSTUVWXYZ'), VALUES)))

        user_inputs = "B\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(DICT, disp_width=_disp_width).choose('pick one > ')

        captured = capsys.readouterr().out.strip().split('\n')
        # on this one there is a empty line between the last menu
        # row and prompt
        # skip the last row, it is the prompt
        for idx, line in enumerate(captured[:-2]):
            assert 0.8 * _disp_width <= len(line) <= _disp_width


    @pytest.mark.parametrize('_disp_width', (90, 140))
    def test_margin_of_many_long_options(self, capsys, _disp_width):

        VALUES = [(f'Test of extremely long options, so long they go past the '
                   f'disp_width, so they should be truncated{_}') for _ in
                  range(0, 27)]
        DICT = dict((zip(list('ABCDEFGHIJKLMNOPQURSTUVWXYZ'), VALUES)))

        user_inputs = "A\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(DICT, disp_width=_disp_width).choose('pick one > ')

        captured = capsys.readouterr().out.strip().split('\n')

        # on this one there is a empty line between the last menu
        # row and prompt
        # skip the last row, it is the prompt
        for idx, line in enumerate(captured[:-2]):
            assert 0.8 * _disp_width <= len(line) <= _disp_width


    @pytest.mark.parametrize('_len', ('short', 'medium', 'long'))
    def test_fixed_col_width_displays_correctly(self, capsys, _len):

        fixed_col_width = 40

        if _len == 'short':
            _DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}
        elif _len == 'medium':
            _DICT = {
                'a': 'Medium len text Test 1',
                'b': 'Medium len text Test 2',
                'c': 'Medium len text Test 3'
            }
        elif _len == 'long':
            _DICT = {
                'a': 'Print long display of text Test 1',
                'b': 'Print long display of text text Test 2',
                'c': 'Print long display of text Test 3'
            }
        else:
            raise Exception


        user_inputs = "b\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(_DICT, fixed_col_width=fixed_col_width).choose('Hurry up! > ')

        captured = capsys.readouterr().out.strip().split('\n')

        for line in captured[:-1]:
            # skip the last row, it is the prompt
            chopped_line = line.split(')')
            for fragment in chopped_line:
                assert 0 <= len(fragment.strip()) <= fixed_col_width


    def test_allowed_displays_correctly(self, capsys):

        DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}

        user_inputs = "a\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(DICT, allowed='ac').choose('pick one > ')

        captured = capsys.readouterr().out

        assert '(a)' in captured
        assert '(c)' in captured
        assert '(b)' not in captured


    def test_disallowed_displays_correctly(self, capsys):
        DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}

        user_inputs = "a\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            DMP(DICT, disallowed='c').choose('pick one > ')

        captured = capsys.readouterr().out

        assert '(a)' in captured
        assert '(b)' in captured
        assert '(c)' not in captured


    def test_choose_returns_correcly(self):
        DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}

        user_inputs = "c\n"
        with patch('sys.stdin', io.StringIO(user_inputs)):
            out = DMP(DICT).choose(f'Enter selection')

        assert out == 'c'








