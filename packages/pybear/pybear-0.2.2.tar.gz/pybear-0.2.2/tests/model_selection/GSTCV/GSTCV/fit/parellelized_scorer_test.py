# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import time
import numpy as np

from pybear.model_selection.GSTCV._GSTCV._fit._parallelized_scorer import \
    _parallelized_scorer

from sklearn.metrics import accuracy_score, balanced_accuracy_score

from sklearn.linear_model import LogisticRegression as sk_Logistic





class TestParallelizedScorer:


    # def _parallelized_scorer(
    #     _X_test: SKXType,
    #     _y_test: SKYType,
    #     _FIT_OUTPUT_TUPLE: tuple[ClassifierProtocol, float, bool],
    #     _f_idx: int,
    #     _SCORER_DICT: ScorerWIPType,
    #     _THRESHOLDS: ThresholdsWIPType,
    #     _error_score: numbers.Real | None,
    #     _verbose: int
    # ) -> tuple[MaskedHolderType, MaskedHolderType]:

    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def _fit_output_excepted(X_np, y_np):

        # [ClassifierProtocol, fit time, fit excepted]
        return (sk_Logistic(), 0.1, True)


    @staticmethod
    @pytest.fixture
    def _fit_output_good(X_np, y_np):

        sk_clf = sk_Logistic()

        t0 = time.perf_counter()

        sk_clf.fit(
            X_np[:int(0.8 * X_np.shape[0])],
            y_np[:int(0.8 * y_np.shape[0])]
        )

        tf = time.perf_counter()

        # [ClassifierProtocol, fit time, fit excepted]
        return (sk_clf, tf-t0, False)

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **







    def test_fit_excepted_accuracy(
        self, X_np, y_np, _fit_output_excepted
    ):

        # 5 folds
        _X_test = X_np[int(0.8 * X_np.shape[0]):, :]
        _y_test = y_np[int(0.8 * y_np.shape[0]):]

        # error_score == np.nan
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _THRESHOLDS=np.linspace(0,1,21).tolist(),
            _error_score=np.nan,
            _verbose=10
        )

        assert out_scores.mask.all()
        assert out_times.mask.all()


        # error_score == 0.4 (any arbitrary number)
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _THRESHOLDS=np.linspace(0,1,21).tolist(),
            _error_score=0.4,
            _verbose=10
        )

        assert round(out_scores.mean(), 8) == 0.4
        assert out_times.mask.all()









    def test_fit_good_accuracy(
        self, X_np, y_np, _fit_output_good
    ):

        # 5 folds
        _X_test = X_np[int(0.8 * X_np.shape[0]):, :]
        _y_test = y_np[int(0.8 * y_np.shape[0]):]

        # error_score == np.nan
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_good,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _THRESHOLDS=np.linspace(0, 1, 21).tolist(),
            _error_score=np.nan,
            _verbose=10
        )

        assert out_scores.shape == (21, 2)
        assert not out_scores.mask.any()
        assert out_scores.min() >= 0
        assert out_scores.max() <= 1
        assert out_scores.mean() > 0

        assert out_times.shape == (21, 2)
        assert not out_times.mask.any()
        assert out_times.min() > 0
        assert out_times.mean() > 0




