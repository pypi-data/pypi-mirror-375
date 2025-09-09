# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._TextJustifier._validation. \
    _sep_or_line_break import _val_sep_or_line_break

import pytest

import re

import numpy as np



class TestValLinebreak:


    @pytest.mark.parametrize('junk_line_break',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_junk_line_break(self, junk_line_break):

        # must be None | re.compile | Sequence[re.compile]

        with pytest.raises(TypeError):
            _val_sep_or_line_break(
                junk_line_break, _name='line_break', _mode='regex'
            )


    @pytest.mark.parametrize('_container', (list, tuple, set, np.ndarray))
    def test_rejects_zero_len_pattern(self, _container):

        with pytest.raises(ValueError):
            _val_sep_or_line_break(
                re.compile(''), _name='line_break', _mode='regex'
            )

        _base_line_breaks = list(map(re.compile, ('', ' ', '_')))
        if _container is np.ndarray:
            _line_breaks = np.array(_base_line_breaks)
        else:
            _line_breaks = _container(_base_line_breaks)

        assert isinstance(_line_breaks, _container)

        with pytest.raises(ValueError):
            _val_sep_or_line_break(
                _line_breaks, _name='line_break', _mode='regex'
            )


    @pytest.mark.parametrize('_container', (list, tuple, set, np.ndarray))
    def test_rejects_empty_sequence(self, _container):

        if _container is np.ndarray:
            _line_breaks = np.array([])
        else:
            _line_breaks = _container([])

        assert isinstance(_line_breaks, _container)
        assert len(_line_breaks) == 0

        with pytest.raises(ValueError):
            _val_sep_or_line_break(
                _line_breaks, _name='line_break', _mode='regex'
            )


    @pytest.mark.parametrize('_container',
        (None, 'compile', list, set, tuple, np.ndarray)
    )
    def test_good_line_break(self, _container):

        _base_line_breaks = list(map(re.compile, (' ', ';', ',', '.')))

        if _container is None:
            _line_breaks = None
        elif _container == 'compile':
            _line_breaks = re.compile('some string')
        elif _container is np.ndarray:
            _line_breaks = np.array(_base_line_breaks)
        else:
            _line_breaks = _container(_base_line_breaks)

        if not isinstance(_container, (type(None), str)):
            assert isinstance(_line_breaks, _container)

        assert _val_sep_or_line_break(
            _line_breaks, _name='line_break', _mode='regex'
        ) is None






