# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._TextJustifier._validation. \
    _sep_or_line_break import _val_sep_or_line_break

import pytest

import numpy as np



class TestValSep:


    @pytest.mark.parametrize('junk_sep',
        (-2.7, -1, 0, 1, 2.7, True, False, None, [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_junk_sep(self, junk_sep):

        # must be str or Sequence[str]

        with pytest.raises(TypeError):
            _val_sep_or_line_break(junk_sep, _name='sep', _mode='str')


    @pytest.mark.parametrize('_container', (list, tuple, set, np.ndarray))
    def test_rejects_empty_string(self, _container):

        with pytest.raises(ValueError):
            _val_sep_or_line_break('', _name='sep', _mode='str')

        _base_seps = ['', ' ', '_']
        if _container is np.ndarray:
            _seps = np.array(_base_seps)
        else:
            _seps = _container(_base_seps)

        assert isinstance(_seps, _container)

        with pytest.raises(ValueError):
            _val_sep_or_line_break(_seps, _name='sep', _mode='str')


    @pytest.mark.parametrize('_container', (list, tuple, set, np.ndarray))
    def test_rejects_empty_sequence(self, _container):

        if _container is np.ndarray:
            _seps = np.array([])
        else:
            _seps = _container([])

        assert isinstance(_seps, _container)
        assert len(_seps) == 0

        with pytest.raises(ValueError):
            _val_sep_or_line_break(_seps, _name='sep', _mode='str')


    @pytest.mark.parametrize('_container', (str, list, set, tuple, np.ndarray))
    def test_good_sep(self, _container):

        _base_seps = [' ', ';', ',', '.']

        if _container is str:
            _seps = 'some string'
        elif _container is np.ndarray:
            _seps = np.array(_base_seps)
        else:
            _seps = _container(_base_seps)

        assert isinstance(_seps, _container)

        assert _val_sep_or_line_break(_seps, _name='sep', _mode='str') is None







