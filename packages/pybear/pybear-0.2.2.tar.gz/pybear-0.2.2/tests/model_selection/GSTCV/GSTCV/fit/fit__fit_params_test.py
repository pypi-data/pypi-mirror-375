# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np



class TestCoreFit_FitParams_NotPipe:


    @staticmethod
    @pytest.fixture()
    def special_GSTCV(sk_GSTCV_est_log_one_scorer_prefit):
        # create a copy of the session fixture
        # do not mutate the session fixture!
        __ = sk_GSTCV_est_log_one_scorer_prefit
        return type(__)(**__.get_params(deep=False))


    def test_rejects_sample_weight_too_short(
        self, special_GSTCV, X_np, y_np, _rows
    ):

        short_sample_weight = np.random.uniform(0, 1, _rows//2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            special_GSTCV.fit(X_np, y_np, sample_weight=short_sample_weight)


    def test_rejects_sample_weight_too_long(
        self, special_GSTCV, X_np, y_np, _rows
    ):

        long_sample_weight = np.random.uniform(0, 1, _rows*2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            special_GSTCV.fit(X_np, y_np, sample_weight=long_sample_weight)


    def test_correct_sample_weight_works(
        self, special_GSTCV, X_np, y_np, _rows
    ):

        correct_sample_weight = np.random.uniform(0, 1, _rows)

        assert isinstance(
            special_GSTCV.fit(X_np, y_np, sample_weight=correct_sample_weight),
            type(special_GSTCV)
        )



class TestCoreFit_FitParams_Pipe:


    @staticmethod
    @pytest.fixture()
    def special_GSTCV_pipe(sk_GSTCV_pipe_log_one_scorer_prefit):
        # create a copy of the session fixture
        # do not mutate the session fixture!
        __ = sk_GSTCV_pipe_log_one_scorer_prefit
        return type(__)(**__.get_params(deep=False))


    def test_rejects_sample_weight_too_short(
        self, special_GSTCV_pipe, X_np, y_np, _rows
    ):

        short_sample_weight = np.random.uniform(0, 1, _rows//2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            # have to use s__p param format
            special_GSTCV_pipe.fit(
                X_np, y_np, sk_logistic__sample_weight=short_sample_weight
            )


    def test_rejects_sample_weight_too_long(
        self, special_GSTCV_pipe, X_np, y_np, _rows
    ):

        long_sample_weight = np.random.uniform(0, 1, _rows*2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            # have to use s__p param format
            special_GSTCV_pipe.fit(
                X_np, y_np, sk_logistic__sample_weight=long_sample_weight
            )


    def test_correct_sample_weight_works(
            self, special_GSTCV_pipe, X_np, y_np, _rows
    ):

        correct_sample_weight = np.random.uniform(0, 1, _rows)

        # have to use s__p param format
        out = special_GSTCV_pipe.fit(
            X_np, y_np, sk_logistic__sample_weight=correct_sample_weight
        )

        assert isinstance(out, type(special_GSTCV_pipe))








