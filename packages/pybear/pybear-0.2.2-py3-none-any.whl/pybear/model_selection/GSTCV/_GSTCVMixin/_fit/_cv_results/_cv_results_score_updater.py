# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Literal
from ...._type_aliases import (
    CVResultsType,
    ScorerWIPType,
    MaskedHolderType
)

import numpy as np

from ..._validation._holders._f_s import _val_f_s



def _cv_results_score_updater(
    _FOLD_x_SCORER__SCORE: MaskedHolderType,
    _type: Literal['train', 'test'],
    _trial_idx: int,
    _scorer: ScorerWIPType,
    _cv_results: CVResultsType
) -> CVResultsType:
    """Update the correct permutation row (`_trial_idx`) and column
    ({'mean'/'std'/'split'}{_split/''}_{_type}_{scorer/'score'}) of
    cv_results with the scores from _FOLD_x_SCORER__SCORE.

    The _FOLD_x_SCORER__SCORE grid can contain either test scores or
    train scores (not at the same time!)

    This module supports :func:`_cv_results_update`.

    Parameters
    ----------
    _FOLD_x_SCORER__SCORE : MaskedHolderType
        Grid of shape (n splits, n scorers) that holds either train
        scores or test scores.
    _type : Literal['train', 'test']
        Indicates whether the scores being updated are for train or test.
    _trial_idx : int
        Row index of `cv_results_` to update
    _scorer : ScorerWIPType
        Dictionary of scorer names and scorer functions. Note that
        the scorer functions are sklearn metrics (or similar), not
        'make_scorer'. Used to know what column names to look for in
        `cv_results_` and nothing more.
    _cv_results : CVResultsType
        Tabulated scores, times, etc., of grid search trials.

    Returns
    -------
    _cv_results : CVResultsType
        `cv_results_` updated with scores.

    """

    # _validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    _val_f_s(
        _FOLD_x_SCORER__SCORE,
        '_FOLD_x_SCORER__SCORE',
        _FOLD_x_SCORER__SCORE.shape[0],  # deliberate fudge
        len(_scorer)
    )

    if _type not in ('train', 'test'):
        raise ValueError(f"'_type' ({_type}) must be 'train' or 'test'")

    _n_permutes = len(_cv_results[list(_cv_results.keys())[0]])
    if _trial_idx not in range(_n_permutes):
        raise ValueError(f"'_trial_idx' ({_trial_idx}) out of range for "
            f"cv_results with {_n_permutes} permutations")
    del _n_permutes

    # do not validate this, to allow for any user-defined scorer name
    # for _scorer_name in _scorer:
    #     if _scorer_name != 'score' and _scorer_name not in master_scorer_dict:
    #         raise ValueError(f"scorer names in '_scorer' ({_scorer_name}) must "
    #             f"match those in allowed: {', '.join(master_scorer_dict)}")

    assert isinstance(_cv_results, dict)

    # END _validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _err_msg = lambda _header: (f"appending scores to a column in "
        f"cv_results_ that doesnt exist ({_header})")

    for scorer_idx, scorer_suffix in enumerate(_scorer):

        if len(_scorer) == 1:
            scorer_suffix = 'score'

        # individual splits -- -- -- -- -- -- -- -- -- -- -- -- -- --
        for _split in range(_FOLD_x_SCORER__SCORE.shape[0]):

            _header = f'split{_split}_{_type}_{scorer_suffix}'

            if _header not in _cv_results:
                raise ValueError(_err_msg(_header))

            _cv_results[_header][_trial_idx] = \
                _FOLD_x_SCORER__SCORE[_split, scorer_idx]


        # mean of all splits -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _header = f'mean_{_type}_{scorer_suffix}'

        if _header not in _cv_results:
            raise ValueError(_err_msg(_header))

        _cv_results[_header][_trial_idx] = \
            np.mean(_FOLD_x_SCORER__SCORE[:, scorer_idx])


        # stdev of all splits -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _header = f'std_{_type}_{scorer_suffix}'

        if _header not in _cv_results:
            raise ValueError(_err_msg(_header))

        _cv_results[_header][_trial_idx] = \
            np.std(_FOLD_x_SCORER__SCORE[:, scorer_idx])


    del _err_msg


    return _cv_results







