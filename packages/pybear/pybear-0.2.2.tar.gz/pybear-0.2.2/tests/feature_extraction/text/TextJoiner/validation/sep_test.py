# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextJoiner._validation._sep import _val_sep



class TestValSep:


    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        # n rows must be 3
        return (3, 25)


    @staticmethod
    @pytest.fixture(scope='module')
    def _base_X(_shape):
        return np.random.choice(list('abcdefg'), _shape, replace=True)

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('junk_sep',
        (-2.7, -1, 0, 1, 2.7, True, None, [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_sep, _base_X):

        with pytest.raises(TypeError):
            _val_sep(junk_sep, _base_X)


    @pytest.mark.parametrize('bad_len', ('n-1', 'n+1'))
    def test_rejects_bad_1D_len(self, _shape, _base_X, bad_len):

        if bad_len == 'n-1':
            _n = _shape[0] - 1
        elif bad_len == 'n+1':
            _n = _shape[0] + 1
        else:
            raise Exception

        _bad_sep = np.random.choice(list('abcdef'), (_n, ))

        with pytest.raises(ValueError):
            _val_sep(_bad_sep, _base_X)


    @pytest.mark.parametrize('_sep',
        ('good', 'strings', 'are', 'hard', 'to', 'come', 'by', '', ' ',
         ['more', 'good', 'strings'], ('good', 'strings', 'abound'))
    )
    def test_accepts_strings_or_1D_of_strings(self, _base_X, _sep):

        assert _val_sep(_sep, _base_X) is None





