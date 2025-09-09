# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._validation._feature_names_in \
    import _val_feature_names_in



class TestValFeatureNamesIn:


    @pytest.mark.parametrize('junk_fni',
        (-2.7, -1, 0, 1, 2.7, True, 'trash', {'a':1}, lambda x: x)
    )
    def test_rejects_junk_fni(self, junk_fni):
        with pytest.raises(TypeError):
            _val_feature_names_in(junk_fni)


    @pytest.mark.parametrize('bad_fni', ([0,1,2], (True, False), {-3, -2, -1}))
    def test_rejects_bad_fni(self, bad_fni):
        with pytest.raises(ValueError):
            _val_feature_names_in(bad_fni)


    @pytest.mark.parametrize('good_fni',
        (list('abc'), tuple('abc'), set('abc'), np.array(list('abc')))
    )
    def test_accept_good_fni(self, good_fni):
        _val_feature_names_in(good_fni)


    @pytest.mark.parametrize('fni',
        (list('abc'), tuple('abc'), set('abc'), np.array(list('abc')))
    )
    @pytest.mark.parametrize('nfi', (2, 3, 4))
    def test_len_fni_against_n_features_in(self, fni, nfi):

        if  len(fni) == nfi:
            _val_feature_names_in(
                fni,
                _n_features_in=nfi
            )
        else:
            with pytest.raises(ValueError):
                _val_feature_names_in(
                    fni,
                    _n_features_in=nfi
                )




