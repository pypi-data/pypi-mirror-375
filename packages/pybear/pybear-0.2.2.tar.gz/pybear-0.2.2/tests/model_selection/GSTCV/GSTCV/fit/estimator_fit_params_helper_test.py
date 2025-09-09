# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.model_selection import KFold as sk_KFold

from pybear.model_selection.GSTCV._GSTCV._fit._estimator_fit_params_helper \
    import _estimator_fit_params_helper



class TestEstimatorFitParamsHelper:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def good_sk_fit_params(_rows):
        return {
            'sample_weight': np.random.uniform(0, 1, _rows),
            'fake_sample_weight': np.random.uniform(0, 1, _rows//2),
            'made_up_param_1':  'something',
            'made_up_param_2': True,
            'some_other_param_1': {'abc': 123}
        }


    @staticmethod
    @pytest.fixture
    def good_sk_kfold(standard_cv_int, X_np, y_np):
        return list(sk_KFold(n_splits=standard_cv_int).split(X_np, y_np))


    @staticmethod
    @pytest.fixture
    def exp_sk_helper_output(_rows, good_sk_fit_params, good_sk_kfold):

        sk_helper = {}

        for idx, (train_idxs, test_idxs) in enumerate(good_sk_kfold):
            sk_helper[idx] = {}
            for k, v in good_sk_fit_params.items():
                try:
                    iter(v)
                    if isinstance(v, (dict, str)):
                        raise Exception
                    if len(v) != _rows:
                        raise Exception
                    np.array(list(v))
                    sk_helper[idx][k] = v.copy()[train_idxs]
                except:
                    sk_helper[idx][k] = v

        return sk_helper

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



    # test validation of args ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('bad_data_len',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), {'a': 1}, min,
         lambda x: x)
    )
    def test_data_len_rejects_not_pos_int(
        self, bad_data_len, good_sk_fit_params, good_sk_kfold
    ):

        with pytest.raises(TypeError):
            _estimator_fit_params_helper(
                bad_data_len, good_sk_fit_params, good_sk_kfold
            )


    @pytest.mark.parametrize('bad_fit_params',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), min, lambda x: x)
    )
    def test_fit_params_rejects_not_dict(
        self, _rows, bad_fit_params, good_sk_kfold
    ):

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, bad_fit_params, good_sk_kfold
            )


    @pytest.mark.parametrize('bad_kfold',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), {'a': 1}, min,
         lambda x: x)
    )
    def test_kfold_rejects_not_list_of_tuples(
        self, _rows, good_sk_fit_params, bad_kfold
    ):

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, good_sk_fit_params, bad_kfold
            )


    # END test validation of args ** * ** * ** * ** * ** * ** * ** * ** *




    # test accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def test_saccuracy(
        self, _rows, good_sk_fit_params, good_sk_kfold, exp_sk_helper_output
    ):

        _fit_params = good_sk_fit_params

        out = _estimator_fit_params_helper(_rows, _fit_params, good_sk_kfold)

        for f_idx, exp_fold_fit_param_dict in exp_sk_helper_output.items():

            for param, exp_value in exp_fold_fit_param_dict.items():
                _act = out[f_idx][param]
                if isinstance(exp_value, np.ndarray):
                    assert len(_act) < _rows
                    assert len(exp_value) < _rows
                    assert np.array_equiv(_act, exp_value)
                else:
                    assert _act == exp_value


    def test_accuracy_empty(self, _rows, good_sk_kfold):

        out = _estimator_fit_params_helper(
            _rows,
            {},
            good_sk_kfold
        )

        assert np.array_equiv(list(out), list(range(len(good_sk_kfold))))

        for idx, fit_params in out.items():
            assert fit_params == {}


