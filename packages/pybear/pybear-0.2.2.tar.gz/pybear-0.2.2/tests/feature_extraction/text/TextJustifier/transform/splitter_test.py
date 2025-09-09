# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextJustifier._transform._splitter \
    import _splitter



class TestSplitter:

    # no validation

    # splitter must receive fully built compile object (that is, has gone
    # thru _param_conditioner())

    # def _splitter(
    #     _X: list[str],
    #     _sep: re.Pattern[str] | tuple[re.Pattern[str], ...]
    #     _line_break: None | re.Pattern[str] | tuple[re.Pattern[str], ...]
    # ) -> list[str]:


    @staticmethod
    @pytest.fixture(scope='function')
    def ex1():

        return [
            'want to split. on a period here.',
            'no-op here',
            'want to split, on comma here',
            'zebras split on z and q here',
            'they split at the end in alcatraz',
            'last split on; a semicolon.',
        ]

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('_sep', (re.compile(' '), re.compile('(?!x)')))
    @pytest.mark.parametrize('_line_break', (re.compile(' '), re.compile('(?!x)')))
    def test_splitter_doesnt_hang(self, _sep, _line_break):

        _X = ['sknaspdouralmnbpasoiruaaskdrua']

        assert isinstance(_splitter(_X, _sep, _line_break), list)


    def test_line_break_is_None(self, ex1):

        _sep = re.compile('[;QZ]', re.I)
        _line_break = None

        out = _splitter(ex1, _sep, _line_break)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        exp = [
            'want to split. on a period here.',
            'no-op here',
            'want to split, on comma here',
            'z',
            'ebras split on z',
            ' and q',
            ' here',
            'they split at the end in alcatraz',
            'last split on;',
            ' a semicolon.'
        ]

        for _idx in range(len(exp)):
            assert np.array_equal(out[_idx], exp[_idx])


    def test_accuracy_single_compile(self, ex1):

        # it is important that in ex1 q is after z but in _sep z is after q
        _sep = re.compile('[;QZ]', re.I)
        _line_break = re.compile('[.,]')

        out = _splitter(ex1, _sep, _line_break)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        exp = [
            'want to split.',
            ' on a period here.',
            'no-op here',
            'want to split,',
            ' on comma here',
            'z',
            'ebras split on z',
            ' and q',
            ' here',
            'they split at the end in alcatraz',
            'last split on;',
            ' a semicolon.'
        ]

        for _idx in range(len(exp)):
            assert np.array_equal(out[_idx], exp[_idx])


    def test_accuracy_tuple_of_compiles(self, ex1):

        # it is important that in ex1 q is after z but in _sep z is after q
        _sep = (re.compile(';', re.I), re.compile('Q', re.I), re.compile('Z', re.I))
        _line_break = re.compile('[.,]')

        out = _splitter(ex1, _sep, _line_break)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))

        exp = [
            'want to split.',
            ' on a period here.',
            'no-op here',
            'want to split,',
            ' on comma here',
            'z',
            'ebras split on z',
            ' and q',
            ' here',
            'they split at the end in alcatraz',
            'last split on;',
            ' a semicolon.'
        ]

        for _idx in range(len(exp)):
            assert np.array_equal(out[_idx], exp[_idx])








