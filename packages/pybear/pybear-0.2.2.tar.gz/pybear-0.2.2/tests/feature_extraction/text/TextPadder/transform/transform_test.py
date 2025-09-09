# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from copy import deepcopy

import pytest
import numpy as np

from pybear.feature_extraction.text._TextPadder._transform._transform import \
    _transform



class TestTransform:


    @staticmethod
    @pytest.fixture(scope='module')
    def _text():
        return [
            ['Macbeth!', 'Macbeth!', 'Macbeth!'],
            ['Beware', 'Macduff!'],
            ['Beware', 'the', 'Thane', 'of', 'Fife!'],
            ['Dismiss', 'me.'],
            ['Enough.']
        ]


    @staticmethod
    @pytest.fixture(scope='module')
    def _exp():
        return [
            ['Macbeth!', 'Macbeth!', 'Macbeth!', '', ''],
            ['Beware', 'Macduff!', '', '', ''],
            ['Beware', 'the', 'Thane', 'of', 'Fife!'],
            ['Dismiss', 'me.', '', '', ''],
            ['Enough.', '', '', '', '']
        ]


    @pytest.mark.parametrize('_fill',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'up', [0,1], (1,), {1,2}, {"a":1},
         lambda x: x)
    )
    def test_fill_must_be_str(self, _text, _fill):

        if isinstance(_fill, str):
            _transform(
                deepcopy(_text),
                _fill=_fill,
                _n_features=5   # dont pass None here!
            )
        else:
            with pytest.raises(AssertionError):
                _transform(
                    deepcopy(_text),
                    _fill=_fill,
                    _n_features=5  # dont pass None here!
                )


    @pytest.mark.parametrize('n_features', (-1, 0, 1, 2))
    def test_rejects_n_features_too_low(self, _text, n_features):

        with pytest.raises(ValueError):
            _transform(
                deepcopy(_text),
                _fill='',
                _n_features=n_features
            )


    def test_accuracy(self, _text, _exp):

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # n_features is exact (would have been set by fit)
        # fill is ''

        out = _transform(
            deepcopy(_text),
            _fill='',
            _n_features=5   # dont pass None here!
        )

        assert isinstance(out, list)
        for _ in out:
            assert isinstance(out, list)
            assert all(map(isinstance, _, (str for i in _)))

        assert all(map(np.array_equal, out, _exp))
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # n_features is exact (would have been set by fit)
        # fill is 'abc'

        out = _transform(
            deepcopy(_text),
            _fill='abc',
            _n_features=5
        )

        assert isinstance(out, list)
        for _ in out:
            assert isinstance(out, list)
            assert all(map(isinstance, _, (str for i in _)))

        _new_exp = deepcopy(_exp)

        for _idx, _row in enumerate(_new_exp):
            for _str_idx, _str in enumerate(_row):
                if _str == '':
                    _new_exp[_idx][_str_idx] = 'abc'

        assert all(map(np.array_equal, out, _new_exp))
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # n_features is greater than n strings
        # fill is ''

        _fill = ''
        _n_features = 10

        out = _transform(
            deepcopy(_text),
            _fill=_fill,
            _n_features=_n_features
        )

        assert isinstance(out, list)
        for _ in out:
            assert isinstance(out, list)
            assert all(map(isinstance, _, (str for i in _)))

        _new_exp = deepcopy(_exp)
        for _idx, _list in enumerate(_new_exp):
            _new_exp[_idx] += [_fill for _ in range(_n_features - len(_list))]

        assert all(map(np.array_equal, out, _new_exp))
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # n_features is greater than n strings
        # fill is 'abc'

        _fill = 'abc'
        _n_features = 13

        out = _transform(
            deepcopy(_text),
            _fill=_fill,
            _n_features=_n_features
        )

        assert isinstance(out, list)
        for _ in out:
            assert isinstance(out, list)
            assert all(map(isinstance, _, (str for i in _)))

        _new_exp = deepcopy(_exp)

        for _idx, _list in enumerate(_new_exp):
            for _str_idx, _str in enumerate(_list):
                if _str == '':
                    _new_exp[_idx][_str_idx] = _fill
            _new_exp[_idx] += [_fill for _ in range(_n_features - len(_list))]

        assert all(map(np.array_equal, out, _new_exp))
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --




