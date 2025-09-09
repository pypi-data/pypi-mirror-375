# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    MaskedHolderType,
    ThresholdsWIPType
)

import numpy as np

from .._validation._holders._f_t_s import _val_f_t_s



def _get_best_thresholds(
    _TEST_FOLD_x_THRESH_x_SCORER__SCORE: MaskedHolderType,
    _THRESHOLDS: ThresholdsWIPType
) -> MaskedHolderType:
    """After collecting the scores for every fold / threshold / scorer
    combination, average the scores across the folds for each scorer to
    give the mean scores of fits in vectors of shape (n_thresholds, ).

    If a fit excepted, every value in the corresponding plane on axis 0
    was set to `error_score`. If `error_score` was numeric, that fold
    is included in the mean calculations; if that number was np.nan,
    that fold is excluded from the mean calculations. For each vector of
    mean scores, apply an algorithm that finds the index position of the
    maximum mean score, and if there are multiple positions with that
    value, finds the position that is closest to 0.5. Repeat this for
    all scorers to populate a TEST_BEST_THRESH_IDXS_BY_SCORER vector
    with the index position of the best threshold for each scorer.

    Parameters
    ----------
    _TEST_FOLD_x_THRESH_x_SCORER__SCORE : MaskedHolderType
        A 3D object of shape (n_splits, n_thresholds, n_scorers). If a
        fit excepted, the corresponding plane in axis 0 holds the
        `error_score` value in every position. Otherwise, holds scores
        for every fold / threshold / scorer permutation.
    _THRESHOLDS : ThresholdsWIPType
        Vector of thresholds for the 'param grid' associated with this
        permutation of search. 'param grid' being a single dict from the
        `param_grid` list of param grids.

    Returns
    -------
    TEST_BEST_THRESH_IDXS_BY_SCORER : MaskedHolderType
        A vector of shape (n_scorers, ) that holds the index in the
        'thresholds' vector of the threshold that had the highest score
        (or lowest loss) for each scorer.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    _val_f_t_s(
        _TEST_FOLD_x_THRESH_x_SCORER__SCORE,
        '_TEST_FOLD_x_THRESH_x_SCORER__SCORE',
        # deliberate fudge
        _TEST_FOLD_x_THRESH_x_SCORER__SCORE.shape[0],
        len(_THRESHOLDS),
        _TEST_FOLD_x_THRESH_x_SCORER__SCORE.shape[2]
    )
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    TEST_BEST_THRESH_IDXS_BY_SCORER: MaskedHolderType = \
        np.ma.zeros(_TEST_FOLD_x_THRESH_x_SCORER__SCORE.shape[2],
        dtype=np.uint16
    )

    for s_idx in range(_TEST_FOLD_x_THRESH_x_SCORER__SCORE.shape[2]):

        _SCORER_THRESH_MEANS = \
            _TEST_FOLD_x_THRESH_x_SCORER__SCORE[:, :, s_idx].mean(axis=0)

        _SCORER_THRESH_MEANS = _SCORER_THRESH_MEANS.ravel()

        assert len(_SCORER_THRESH_MEANS) == len(_THRESHOLDS), \
            f"len(_SCORER_THRESH_MEANS) != len(_THRESHOLDS)"

        # IF MULTIPLE THRESHOLDS HAVE BEST SCORE, USE THE ONE CLOSEST TO 0.50
        # FIND CLOSEST TO 0.50 USING (THRESH - 0.50)**2
        BEST_SCORE_IDX_MASK = (_SCORER_THRESH_MEANS == _SCORER_THRESH_MEANS.max())
        del _SCORER_THRESH_MEANS

        MASKED_LSQ = (1 - np.power(np.array(_THRESHOLDS) - 0.50, 2, dtype=np.float64))
        MASKED_LSQ = MASKED_LSQ * BEST_SCORE_IDX_MASK
        del BEST_SCORE_IDX_MASK

        best_idx = np.argmax(MASKED_LSQ)
        del MASKED_LSQ

        assert int(best_idx) == best_idx, \
            f"int(best_idx) != best_idx"
        assert best_idx in range(len(_THRESHOLDS)), \
            f"best_idx not in range(len(THRESHOLDS))"

        TEST_BEST_THRESH_IDXS_BY_SCORER[s_idx] = int(best_idx)

    del best_idx


    return TEST_BEST_THRESH_IDXS_BY_SCORER





