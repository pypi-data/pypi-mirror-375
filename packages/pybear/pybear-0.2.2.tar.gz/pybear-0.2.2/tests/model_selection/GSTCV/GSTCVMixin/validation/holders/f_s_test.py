# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import scipy.sparse as ss

from pybear.model_selection.GSTCV._GSTCVMixin._validation._holders._f_s \
    import _val_f_s



class TestValFS:


    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        return (5, 21)


    @staticmethod
    @pytest.fixture(scope='module')
    def _good_fs(_shape):
        return np.ma.zeros(_shape, dtype=np.float64)


    @pytest.mark.parametrize('_bad_fs',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0,1], (0,1), {0,1},
         {'a': 1}, lambda x: x, 'np', 'pd', 'csr', 'csc')
    )
    def test_rejects_non_np_masked(self, _shape, _bad_fs):

        _base_X = np.random.randint(0, 10, _shape)

        if _bad_fs == 'np':
            _bad_fs = _base_X
        elif _bad_fs == 'pd':
            _bad_fs = pd.DataFrame(np.random.randint(0, 10, _shape))
        elif _bad_fs == 'csr':
            _bad_fs = ss.csr_array(_base_X)
        elif _bad_fs == 'csc':
            _bad_fs = ss.csc_array(_base_X)

        with pytest.raises(TypeError):
            _val_f_s(_bad_fs, 'whatever', *_shape)


    @pytest.mark.parametrize('_bad_dtype', ('int8', 'int32', 'flt32'))
    def test_rejects_bad_dtype(self, _shape, _good_fs, _bad_dtype):

        if _bad_dtype == 'int8':
            _fs = _good_fs.copy().astype(np.int8)
        elif _bad_dtype == 'int32':
            _fs = _good_fs.copy().astype(np.int32)
        elif _bad_dtype == 'flt32':
            _fs = _good_fs.copy().astype(np.float32)
        else:
            raise Exception


        with pytest.raises(TypeError):
            _val_f_s(_fs, 'whatever', *_shape)


    def test_rejects_bad_dim(self, _shape, _good_fs):

        with pytest.raises(ValueError):
            _val_f_s(
                np.ma.zeros((_shape[0], _shape[1], 9)),
                'whatever',
                _shape[0],
                _shape[1]
            )


    @pytest.mark.parametrize('_dim1', ('high', 'low', 'correct'))
    @pytest.mark.parametrize('_dim2', ('high', 'low', 'correct'))
    @pytest.mark.parametrize('_dim3', ('high', 'low', 'correct'))
    def test_rejects_bad_shape(
        self, _shape, _good_fs, _dim1, _dim2, _dim3
    ):

        if all(map(lambda x: x=='correct', (_dim1, _dim2, _dim3))):
            pytest.skip(reason=f"should pass")

        with pytest.raises(ValueError):
            _val_f_s(
                _good_fs,
                'whatever',
                _shape[0] + 1,
                _shape[1] - 1
            )


    def test_accepts_good(self, _shape, _good_fs):

        assert _val_f_s(_good_fs, 'whatever', *_shape) is None





