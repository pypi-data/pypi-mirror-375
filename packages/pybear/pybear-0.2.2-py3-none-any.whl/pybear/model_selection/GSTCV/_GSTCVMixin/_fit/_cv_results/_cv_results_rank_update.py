# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

from ...._type_aliases import (
    CVResultsType,
    ScorerWIPType
)



def _cv_results_rank_update(
    _scorer: ScorerWIPType,
    _cv_results: CVResultsType
) -> CVResultsType:
    """Calculate rank for each 'mean_score...' column and update the
    `cv_results_` attribute.

    Within each parameter search trial, every cv split has a test set
    that is scored using all the given scorers. The scores populate
    columns created for each split/scorer combination, in the row
    corresponding to the parameter search trial. For each scorer, the
    scores are averaged over all the splits and those results are put in
    their respective 'mean_test_{scorer}' columns in the same row.
    Finally, once all the parameter searches are complete, the mean
    scores in each mean score column are ranked descending, with the
    value '1' indicating the best score.

    Parameters
    ----------
    _scorer : ScorerWIPType
        The dictionary of scorers keyed by the names of the scorers,
        used for locating columns in `cv_results_`. The callables are
        not used here.
    _cv_results : CVResultsType
        Summary of results.

    Returns
    -------
    _cv_results : CVResultsType
        `cv_results_` dictionary with updated rank columns.

    """


    for scorer_suffix in _scorer:

        if f'rank_test_{scorer_suffix}' not in _cv_results:
            raise ValueError(
                f"appending tests scores to a column in cv_results_ "
                f"that doesnt exist but should (rank_test_{scorer_suffix})"
            )

        # in ties, like [.8, .8, .3, .8] sklearn does [1,1,4,1], not [1,2,4,3]
        og_col = _cv_results[f'mean_test_{scorer_suffix}']
        # unique sorts ascending
        _means, _counts = np.unique(og_col, return_counts=True)
        _means = np.flip(_means)
        _counts = np.flip(_counts)

        rank_dict = dict((zip(_means, np.arange(1, len(_means) + 1))))

        offset = 0
        for idx, _ct in enumerate(_counts[1:], 1):
            offset += (_counts[idx - 1] - 1)
            rank_dict[_means[idx]] += offset

        _cv_results[f'rank_test_{scorer_suffix}'] = np.ma.masked_array(
            np.fromiter(map(lambda x: rank_dict[x], og_col), dtype=np.uint16)
        )

        del og_col, _means, offset, rank_dict


    return _cv_results




