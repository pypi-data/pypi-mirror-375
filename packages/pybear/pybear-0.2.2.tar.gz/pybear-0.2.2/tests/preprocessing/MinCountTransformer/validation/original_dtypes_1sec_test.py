# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._validation._original_dtypes \
    import _val_original_dtypes



class TestValOriginalDtypes:


    @pytest.mark.parametrize('junk_og_dtypes',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', {'a':1}, lambda x: x)
    )
    def test_rejects_junk_og_dtypes(self, junk_og_dtypes):

        with pytest.raises(TypeError):
            _val_original_dtypes(junk_og_dtypes, _n_features_in=5)


    @pytest.mark.parametrize('junk_dtype',
        (0, True, 3.14, min, None, lambda x: x, {'a':1})
    )
    def test_rejects_junk_values(self, junk_dtype):
        with pytest.raises(TypeError):
            _val_original_dtypes(
                np.array(['int', 'float', 'obj', junk_dtype], dtype=object),
                _n_features_in=4
            )


    @pytest.mark.parametrize('container', (list, set, tuple, np.array))
    @pytest.mark.parametrize('bad_og_dtype',
        (list('abc'), list('123'), list('xyz'))
    )
    def test_rejects_bad_values_1(self, container, bad_og_dtype):

        with pytest.raises(ValueError):
            _val_original_dtypes(
                container(bad_og_dtype),
                _n_features_in=3
            )


    @pytest.mark.parametrize('container', (list, set, tuple, np.array))
    @pytest.mark.parametrize('bad_og_dtype', ([0,1,2], (1,2,3)))
    def test_rejects_bad_values_2(self, container, bad_og_dtype):

        with pytest.raises(TypeError):
            _val_original_dtypes(
                container(bad_og_dtype),
                _n_features_in=3
            )


    @pytest.mark.parametrize('length', ('short', 'good', 'long'))
    def test_rejects_bad_length(self, length):

        if length == 'short':
            _og_dtypes = ['int', 'bin_int']
        elif length == 'good':
            _og_dtypes = ['int', 'bin_int', 'float']
        elif length == 'long':
            _og_dtypes = ['int', 'bin_int', 'float', 'obj']
        else:
            raise Exception


        if length == 'good':
            _val_original_dtypes(
                _og_dtypes,
                _n_features_in=3
            )
        else:
            with pytest.raises(ValueError):
                _val_original_dtypes(
                    _og_dtypes,
                    _n_features_in=3
                )


    VALUES = ['bin_int', 'obj', 'int', 'float']
    @pytest.mark.parametrize('good_og_dtype',
        (list(VALUES), set(VALUES), tuple(VALUES), np.array(VALUES))
    )
    def test_accepts_good_og_dtype(self, good_og_dtype):

        out = _val_original_dtypes(good_og_dtype, _n_features_in=4)

        assert out is None




