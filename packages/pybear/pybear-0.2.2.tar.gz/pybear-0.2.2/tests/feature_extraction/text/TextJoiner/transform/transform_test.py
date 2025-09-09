# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextJoiner._transform._transform import \
    _transform



class TestTransform:


    @staticmethod
    @pytest.fixture(scope='function')
    def _text():
        return [
            ['Whan', 'that', 'Aprille'],
            ['with', 'his', 'shoures', 'soote'],
            ['The', 'droghte', 'of', 'March', 'hath', 'perced', 'to', 'the', 'roote'],
            ['And', 'bathed', 'every', 'veyne', 'in', 'swich', 'licóur'],
            ['Of', 'which', 'vertú', 'engendred', 'is', 'the', 'flour'],
        ]

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('_X_container', (list, tuple))
    @pytest.mark.parametrize('_sep_container', (list, tuple, set, np.array))
    def test_accepts_only_lists(
        self, _text, _X_container, _sep_container
    ):

        _base_sep = list('abcdefghijklmnopqrstuv')[:len(_text)]

        if _sep_container is np.array:
            _sep = np.array(_base_sep)
        else:
            _sep = _sep_container(_base_sep)

        _X = _X_container(map(_X_container, _text))

        if _X_container is list and _sep_container is list:
            _transform(_X, _sep)
        else:
            with pytest.raises(AssertionError):
                _transform(_X, _sep)
    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



    def test_accuracy_1(self, _text):

        out = _transform(_text, ['' for _ in range(len(_text))])

        exp = [
            'WhanthatAprille',
            'withhisshouressoote',
            'ThedroghteofMarchhathpercedtotheroote',
            'Andbathedeveryveyneinswichlicóur',
            'Ofwhichvertúengendredistheflour'
        ]

        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], str)
            assert out[r_idx] == exp[r_idx]
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_accuracy_2(self, _text):

        out = _transform(_text, [' ' for _ in range(len(_text))])

        exp = [
            'Whan that Aprille',
            'with his shoures soote',
            'The droghte of March hath perced to the roote',
            'And bathed every veyne in swich licóur',
            'Of which vertú engendred is the flour'
        ]

        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], str)
            assert out[r_idx] == exp[r_idx]
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_accuracy_3(self, _text):

        out = _transform(_text, [',' for _ in range(len(_text))])

        exp = [
            'Whan,that,Aprille',
            'with,his,shoures,soote',
            'The,droghte,of,March,hath,perced,to,the,roote',
            'And,bathed,every,veyne,in,swich,licóur',
            'Of,which,vertú,engendred,is,the,flour'
        ]

        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], str)
            assert out[r_idx] == exp[r_idx]
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def test_accuracy_4(self, _text):

        out = _transform(_text, list('abcde'))

        exp = [
            'WhanathataAprille',
            'withbhisbshouresbsoote',
            'ThecdroghtecofcMarchchathcpercedctocthecroote',
            'Anddbatheddeverydveynedindswichdlicóur',
            'Ofewhichevertúeengendredeisetheeflour'
        ]

        assert isinstance(out, list)
        for r_idx in range(len(out)):
            assert isinstance(out[r_idx], str)
            assert out[r_idx] == exp[r_idx]
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --






