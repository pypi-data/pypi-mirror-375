# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    CVResultsType,
    RefitCallableType
)

import sys

import numpy as np



def _verify_refit_callable(
    refit_callable: RefitCallableType,
    DUMMY_CV_RESULTS: CVResultsType
) -> None:
    """If refit is a callable, fill the just-built and mostly empty
    `cv_results_` arrays with dummy data (all empties should take floats.)

    Pass the dummy `cv_results_` to the callable to see if it returns an
    integer within range of `cv_results_`, before running the entirety
    of `GSTCV` which could be hours or days just to have the whole thing
    crash because of a bad refit function. Remember that the refit
    callable finds `best_idx_`, which is the row of `cv_results_` whose
    search grid params are deemed "best".

    Parameters
    ----------
    refit_callable : RefitCallableType
        A callable that takes `cv_results_` as an argument and returns
        an integer that is `best_index_`, that indicates the row of
        `cv_results_` that is "best".

    DUMMY_CV_RESULTS : CVResultsType
        A deepcopy of the just-built `cv_results_` dictionary to be
        filled with dummy floats and used to test the`output of the
        refit callable.

    Returns
    -------
    None

    """

    param_permutations = len(DUMMY_CV_RESULTS['params'])

    for column in DUMMY_CV_RESULTS:
        if column[:5] == 'param':
            continue
        elif column[:4] == 'rank':
            DUMMY_CV_RESULTS[column] = \
                np.ma.masked_array(np.arange(1, param_permutations+1))
        else:
            # time, threshold, score, mean, std, etc.
            DUMMY_CV_RESULTS[column] = \
                np.ma.masked_array(np.random.uniform(0, 1, param_permutations))

    try:
        refit_fxn_test_output = refit_callable(DUMMY_CV_RESULTS)
    except:
        raise ValueError(
            f"refit callable excepted during function validation. \n"
            f"reason={sys.exc_info()[1]}"
        )

    del DUMMY_CV_RESULTS

    _msg = lambda output: (
        f"If a callable is passed to refit, it must yield or return an "
        f"integer, and it must be within range of cv_results_ rows. \nThe "
        f"failure has occurred on a randomly filled copy of cv_results "
        f"\nthat allows testing of the refit function before running the "
        f"entire grid search.\nrefit function output = {output}, "
        f"cv_results rows = {param_permutations}"
    )

    try:
        if not int(refit_fxn_test_output) == refit_fxn_test_output:
            raise Exception
    except:
        raise ValueError(_msg(refit_fxn_test_output))


    if refit_fxn_test_output < 0 or refit_fxn_test_output > param_permutations:
        raise ValueError(_msg(refit_fxn_test_output))

    del refit_fxn_test_output, _msg


    return






