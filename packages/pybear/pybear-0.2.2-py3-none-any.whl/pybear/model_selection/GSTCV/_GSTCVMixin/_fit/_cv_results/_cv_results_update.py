# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

from ...._type_aliases import (
    CVResultsType,
    MaskedHolderType,
    ScorerWIPType,
    ThresholdsWIPType
)

from ._cv_results_score_updater import _cv_results_score_updater
from ..._validation._holders._f_t_s import _val_f_t_s
from ..._validation._holders._f_s import _val_f_s
from ..._validation._scoring import _val_scoring



def _cv_results_update(
    _trial_idx: int,
    _THRESHOLDS: ThresholdsWIPType,
    _FOLD_FIT_TIMES_VECTOR: MaskedHolderType,
    _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME: MaskedHolderType,
    _TEST_BEST_THRESH_IDXS_BY_SCORER: MaskedHolderType,
    _TEST_FOLD_x_SCORER__SCORE: MaskedHolderType,
    _TRAIN_FOLD_x_SCORER__SCORE: MaskedHolderType,
    _scorer: ScorerWIPType,
    _cv_results: CVResultsType,
    _return_train_score: bool
) -> CVResultsType:
    """Fills a row of `cv_results_` with thresholds, scores, and times,
    but not ranks.

    (Ranks must be done after cv_results is full.)

    Parameters
    ----------
    _trial_idx : int
        The row index of `cv_results_` to update.
    _THRESHOLDS : ThresholdsWIPType
        Vector of thresholds for the 'param grid' associated with this
        permutation of search. 'param grid' being a single dict from the
        `param_grid` list of param grids.
    _FOLD_FIT_TIMES_VECTOR : MaskedHolderType
        The times to fit each of the folds for this permutation. If a
        fit excepted, the corresponding position is masked and excluded
        from aggregate calculations.
    _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME : MaskedHolderType
        A 3D object of shape (n_splits, n_thresholds, n_scorers). If a
        fit excepted, the corresponding plane in axis 0 is masked, and
        is excluded from aggregate calculations. Otherwise, holds score
        times for every fold / threshold / scorer permutation.
    _TEST_BEST_THRESH_IDXS_BY_SCORER : MaskedHolderType
        Vector of shape (n_scorers,) that matches position-for-position
        against the scorers in `scorer_`. It holds the index location in
        the original threshold vector of the best threshold for each
        scorer.
    _TEST_FOLD_x_SCORER__SCORE : MaskedHolderType
        Masked array of shape (n_splits, n_scorers) that holds the test
        scores corresponding to the best threshold for that fold and
        scorer. If a fit excepted, the corresponding row in axis 0 holds
        the `error_score` value in every position.
    _TRAIN_FOLD_x_SCORER__SCORE : MaskedHolderType
        Masked array of shape (n_splits, n_scorers) that holds the train
        scores corresponding to the best threshold for that fold and
        scorer. If a fit excepted, the corresponding row in axis 0 holds
        the `error_score` value in every position.
    _scorer : ScorerWIPType
        Dictionary of scorer names and scorer functions. Note that the
        scorer functions are sklearn metrics (or similar), not
        'make_scorer'. Used to know what column names to look for in
        `cv_results_` and nothing more.
    _cv_results : CVResultsType
        Empty `cv_results_` dictionary other than the 'param_{}' columns
        and the 'params' column.
    _return_train_score : bool
        When True, calculate the scores for the train folds in addition
        to the test folds.

    Returns
    -------
    _cv_results : CVResultsType
        `cv_results_` updated with scores, thresholds, and times.

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert _trial_idx >= 0, f"'_trial_idx' must be >= 0"
    assert len(_THRESHOLDS) >= 1, f"'len(_THRESHOLDS) must be >= 1 "
    _val_scoring(_scorer, _must_be_dict=True)
    assert len(_TEST_BEST_THRESH_IDXS_BY_SCORER) == len(_scorer)

    assert len(_FOLD_FIT_TIMES_VECTOR) == \
            _TEST_FOLD_x_SCORER__SCORE.shape[0] == \
            _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME.shape[0] == \
            _TRAIN_FOLD_x_SCORER__SCORE.shape[0], \
            f"disagreement of number of splits"

    _val_f_t_s(
        _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME,
        '_TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME',
        len(_FOLD_FIT_TIMES_VECTOR), len(_THRESHOLDS), len(_scorer)
    )

    _val_f_s(
        _TEST_FOLD_x_SCORER__SCORE,
        '_TEST_FOLD_x_SCORER__SCORE',
        len(_FOLD_FIT_TIMES_VECTOR), len(_scorer)
    )

    _val_f_s(
        _TRAIN_FOLD_x_SCORER__SCORE,
        '_TRAIN_FOLD_x_SCORER__SCORE',
        len(_FOLD_FIT_TIMES_VECTOR), len(_scorer)
    )

    assert isinstance(_cv_results, dict), \
        f"'_cv_results' must be a dictionary"
    assert isinstance(_return_train_score, bool), \
        f"'_return_train_score' must be bool"
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *


    # UPDATE cv_results_ WITH THRESHOLDS ###############################

    for s_idx, scorer in enumerate(_scorer):

        best_threshold_idx = int(_TEST_BEST_THRESH_IDXS_BY_SCORER[s_idx])
        best_threshold = _THRESHOLDS[best_threshold_idx]

        scorer = '' if len(_scorer) == 1 else f'_{scorer}'
        if f'best_threshold{scorer}' not in _cv_results:
            raise ValueError(
                f"appending threshold scores to a column in cv_results_ "
                f"that doesnt exist but should (best_threshold{scorer})"
            )

        _cv_results[f'best_threshold{scorer}'][_trial_idx] = best_threshold
    # END UPDATE cv_results_ WITH THRESHOLDS ###########################

    # UPDATE cv_results_ WITH SCORES ###################################
    _cv_results = _cv_results_score_updater(
        _TEST_FOLD_x_SCORER__SCORE,
        'test',
        _trial_idx,
        _scorer,
        _cv_results
    )

    if _return_train_score:
        _cv_results = _cv_results_score_updater(
            _TRAIN_FOLD_x_SCORER__SCORE,
            'train',
            _trial_idx,
            _scorer,
            _cv_results
        )
    # END UPDATE cv_results_ WITH SCORES ###############################


    # UPDATE cv_results_ WITH TIMES ####################################
    for cv_results_column_name in \
        ['mean_fit_time', 'std_fit_time', 'mean_score_time', 'std_score_time']:
        if cv_results_column_name not in _cv_results:
            raise ValueError(
                f"appending time results to a column in cv_results_ that "
                f"doesnt exist but should ({cv_results_column_name})"
            )

    _cv_results['mean_fit_time'][_trial_idx] = np.mean(_FOLD_FIT_TIMES_VECTOR)
    _cv_results['std_fit_time'][_trial_idx] = np.std(_FOLD_FIT_TIMES_VECTOR)

    _cv_results['mean_score_time'][_trial_idx] = \
        np.mean(_TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME)
    _cv_results['std_score_time'][_trial_idx] = \
        np.std(_TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME)
    # END UPDATE cv_results_ WITH TIMES ################################


    return _cv_results





