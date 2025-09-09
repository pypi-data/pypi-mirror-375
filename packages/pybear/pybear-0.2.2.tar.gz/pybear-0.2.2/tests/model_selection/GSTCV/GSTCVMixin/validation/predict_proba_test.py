# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._validation._predict_proba \
    import _val_predict_proba



class TestValPredictProba:


    # 'len' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_len',
        (-1, 0, True, False, 3.14, None, min, 'junk', [0,1], {'a':1}, lambda x: x)
    )
    def test_len_rejects_junk(self, junk_len):
        # 'is_from_kwargs'
        with pytest.raises((TypeError, ValueError)):
            _val_predict_proba(
                np.random.uniform(0, 1, (10, )),
                junk_len
            )


    @pytest.mark.parametrize('good_len', (1, 2, 100))
    def test_len_accepts_int(self, good_len):
        assert _val_predict_proba(
            np.random.uniform(0, 1, (good_len, )),
            good_len
        ) is None

    # END 'len' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *


    @pytest.mark.parametrize('_len', (1, 5, 10))
    @pytest.mark.parametrize('junk_pp',
        (-2.7, -1, 0, 1, 2.7, None, True, False, 'trash', min, {'a':1}, lambda x: x)
    )
    def test_rejects_non_iter(self, junk_pp, _len):
        with pytest.raises(TypeError):
            _val_predict_proba(junk_pp, _len)


    def test_junk_in_list(self):

        with pytest.raises(TypeError):
            _val_predict_proba(['a','b','c'], 3)

        with pytest.raises(ValueError):
            _val_predict_proba([-3.14, 3.14], 2)


    def test_rejects_pp_bad_shape(self):

        with pytest.raises(ValueError):
            _val_predict_proba(np.random.uniform(0, 1, (20, 5)), 20)

        with pytest.raises(ValueError):
            _val_predict_proba(np.random.uniform(0, 1, (3,3,3)), 3)


    @pytest.mark.parametrize('_len', (1, 5, 10))
    def test_rejects_pp_out_of_range(self, X_np, _len):

        with pytest.raises(ValueError):
            _val_predict_proba(X_np[:_len, 0], _len)


    @pytest.mark.parametrize('_format',
        ('py_list', 'py_tup', 'py_set', 'np', 'pd', 'pl')
    )
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_len', (2, 5, 10, 100))
    def test_accepts_good_pp(self, _format_helper, _format, _dim, _len):

        if _format == 'py_set' and _dim == 2:
            pytest.skip(reason=f'cant have 2D set')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        good_pp = _format_helper(
            np.random.uniform(0, 1, (_len,)), _format, _dim
        )


        assert _val_predict_proba(good_pp, _len) is None






