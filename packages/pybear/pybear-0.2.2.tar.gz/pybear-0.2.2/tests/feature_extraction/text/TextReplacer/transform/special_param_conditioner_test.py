# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextReplacer._transform.\
    _special_param_conditioner import _special_param_conditioner

from pybear.feature_extraction.text._TextReplacer._validation. \
    _replace import _val_replace



class TestSpecialParamConditioner:


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return np.random.choice(list('abcde'), (10, ), replace=True)


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_replace',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', {1,2}, lambda x: x)
    )
    def test_rejects_junk_regexp_replace(self, _text, junk_replace):
        # could be None, tuple, tuple[tuple], list
        with pytest.raises(TypeError):
            _special_param_conditioner(
                junk_replace, _case_sensitive=True, _flags=None, _n_rows=len(_text)
            )

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_cs',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_cs(self, _text, junk_cs):
        # could be bool, list[None or bool]
        with pytest.raises(AssertionError):
            _special_param_conditioner(
                None, _case_sensitive=junk_cs, _flags=None, _n_rows=len(_text)
            )

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_flags',
        (-2.7, 2.7, 'trash', list('abc'), (1,), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_flags(self, _text, junk_flags):
        # could be bool, list[None or bool]
        with pytest.raises(AssertionError):
            _special_param_conditioner(
                None, _case_sensitive=True, _flags=junk_flags, _n_rows=len(_text)
            )

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_n_rows',
        (-2.7, -1, 2.7, True, None, 'trash', [0,1], (1,), {1,2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_n_rows(self, _text, junk_n_rows):
        # could be bool, list[None or bool]
        with pytest.raises(AssertionError):
            _special_param_conditioner(
                None, _case_sensitive=True, _flags=None, _n_rows=junk_n_rows
            )

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_rr',
        (None, ('a', ''), (('b', 'B'),), [((re.compile('c'), 'C'),)]*10)
    )
    @pytest.mark.parametrize('_cs', (True, False))
    @pytest.mark.parametrize('_f', (None, re.I))
    @pytest.mark.parametrize('_nr', (10, ))
    def test_accepts_all_good(self, _text, _rr, _cs, _f, _nr):
        _special_param_conditioner(_rr, _cs, _f, _nr)


    # END validation ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('rr_desc',
         (None, 'tuple_1', 'tuple_2', 'tuple_3', 'list_1')
    )
    @pytest.mark.parametrize('cs_desc', ('bool_1', 'bool_2', 'list_1', 'list_2'))
    @pytest.mark.parametrize('f', (re.X, re.I, re.I | re.M, 'list_1'))
    def test_accuracy(self, _text, rr_desc, cs_desc, f):

        if rr_desc is None:
            rr = None
        elif rr_desc == 'tuple_1':
            rr = ('a', '')
        elif rr_desc == 'tuple_2':
            rr = (('a', ''),)
        elif rr_desc == 'tuple_3':
            # this is the only one that tests compile & callable
            rr = (('a', ''), (re.compile('b', re.I), lambda x: 10*x))
        elif rr_desc == 'list_1':
            rr = [('b', 'B') for _ in range(len(_text))]
        else:
            raise Exception

        if cs_desc == 'bool_1':
            cs = True
        elif cs_desc == 'bool_2':
            cs = False
        elif cs_desc == 'list_1':
            cs = [False for _ in _text]
        elif cs_desc == 'list_2':
            cs = [None for _ in _text]
        else:
            raise Exception

        if f == 'list_1':
            f = [re.M for _ in _text]

        out = _special_param_conditioner(
            rr, _case_sensitive=cs, _flags=f, _n_rows=len(_text)
        )


        # whatever is returned should pass the validation for a _replace
        # object! and should have re.compile in the 'find' position of
        # every tuple. we know that OG _param_conditioner is good from
        # its own tests.

        _val_replace(out, _n_rows=len(_text))

        # all the re.Pattern should have the escaped original strings
        # and the flags

        # need the re.U because re.compile assigns it as default.
        # remember most patterns passed in this test is a literal,
        # so cant pull the starting flags off given re.compile objects
        # and pipe new flags onto them. but where a compile was passed,
        # can get the starting flags.
        _base_f = re.U | (re.I if cs_desc in ('bool_2', 'list_1') else 0)
        if isinstance(f, list):
            _exp_f = f[0] | _base_f
        else:
            _exp_f = f | _base_f

        if rr_desc is None:
            assert out is None
        elif rr_desc == 'tuple_1':
            # rr = ('a', '')
            assert isinstance(out, tuple)
            assert isinstance(out[0], re.Pattern)
            assert out[0].pattern == 'a'
            assert out[0].flags == _exp_f
            assert out[1] == ''
        elif rr_desc == 'tuple_2':
            # rr = (('a', ''),)
            assert isinstance(out, tuple)
            assert isinstance(out[0], re.Pattern)
            assert out[0].pattern == 'a'
            assert out[0].flags == _exp_f
            assert out[1] == ''
        elif rr_desc == 'tuple_3':
            # rr = (('a', ''), ('b', ''))
            assert isinstance(out, tuple)
            for _idx, _tuple in enumerate(out):
                assert isinstance(_tuple[0], re.Pattern)
                assert _tuple[0].pattern == {0:'a', 1:'b'}[_idx]
                if _idx == 0:
                    assert _tuple[0].flags == _exp_f
                    assert _tuple[1] == ''
                elif _idx == 1:
                    assert _tuple[0].flags == _exp_f | re.I
                    assert callable(_tuple[1])
                else:
                    raise Exception
        elif rr_desc == 'list_1':
            # rr = [('b', 'B') for _ in range(len(_text))]
            assert isinstance(out, tuple)
            assert isinstance(out[0], re.Pattern)
            assert out[0].pattern == 'b'
            assert out[0].flags == _exp_f
            assert out[1] == 'B'
        else:
            raise Exception


    def test_repeated_replaces_are_not_condensed(self):

        _replace = (('  ', ''), ('  ', ''), ('  ', ''), ('  ', ''))

        out = _special_param_conditioner(
            _replace,
            _case_sensitive=True,
            _flags=None,
            _n_rows=1_000
        )

        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for _ in out)))

        for _tuple in out:
            assert _tuple == (re.compile(re.escape('  ')), '')









