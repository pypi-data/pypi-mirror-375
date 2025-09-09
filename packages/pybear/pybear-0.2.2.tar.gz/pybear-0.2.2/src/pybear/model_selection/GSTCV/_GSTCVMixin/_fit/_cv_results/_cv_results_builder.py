# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Type,
)
from ...._type_aliases import (
    ParamGridsWIPType,
    ScorerWIPType,
    CVResultsType,
    NDArrayHolderType
)

import numpy as np

from ..._validation._param_grid import _val_param_grid
from ..._validation._scoring import _val_scoring

from ......utilities._permuter import permuter



def _cv_results_builder(
    _param_grid: ParamGridsWIPType,
    _n_splits: int,
    _scorer: ScorerWIPType,
    _return_train_score: bool
) -> tuple[CVResultsType, NDArrayHolderType]:
    """Build the `cv_results_` attribute.

    `cv_results_` is a Python dictionary that represents the columns of
    a data table that contains times, scores, and other pertinent
    information gathered during the grid search trials. The dictionary
    keys are column headers that describe the contents of the column and
    the dictionary values are numpy masked arrays. The dictionary format
    can be quickly converted into a pandas DataFrame.

    Consider the following `param_grid` passed to `GSTCV` for an SVC
    classifier:

    [
        {'kernel': ['poly'], 'degree': [2,3], 'thresholds': np.linspace(0,1,21)},

        {'kernel': ['rbf'], 'gamma': [0.1, 0.2], 'thresholds': np.linspace(0,1,21)}
    ],

    using 2 folds for cv.

    An example of `GSTCV` `cv_results_` output might look like:

    {
        'mean_fit_time'      : [0.73, 0.63, 0.43, 0.49],

        'std_fit_time'       : [0.01, 0.02, 0.01, 0.01],

        'mean_score_time'    : [0.007, 0.06, 0.04, 0.04],

        'std_score_time'     : [0.001, 0.002, 0.003, 0.005]

        'param_kernel'       : masked_array(
                                    data = ['poly', 'poly', 'rbf', 'rbf'],
                                    mask = [False False False False]
                               ),

        'param_gamma'        : masked_array(
                                    data = [np.nan, np.nan, 0.1, 0.2],
                                    mask = [ True  True False False]
                               ),

        'param_degree'       : masked_array(
                                    data = [2.0, 3.0, np.nan, np.nan],
                                    mask = [False False  True  True]
                               ),

        'params'             : [{'kernel': 'poly', 'degree': 2}, ...],

        'best_threshold'     : [0.45, 0.55, 0.50, 0,50],

        'split0_test_score'  : [0.8, 0.7, 0.8, 0.9],

        'split1_test_score'  : [0.82, 0.5, 0.7, 0.78],

        'mean_test_score'    : [0.81, 0.60, 0.75, 0.84],

        'std_test_score'     : [0.02, 0.01, 0.03, 0.03],

        'rank_test_score'    : [2, 4, 3, 1],

        'split0_train_score' : [0.8, 0.7, 0.8, 0.9],

        'split1_train_score' : [0.82, 0.7, 0.82, 0.5],

        'mean_train_score'   : [0.81, 0.7, 0.81, 0.7],

        'std_train_score'    : [0.03, 0.04, 0.03, 0.03]
    }

    *** ** * ** *** ** * ** *** ** * ** *** ** * ** *** ** * ** *** ** *

    For construction, in order:

    Format of sklearn `cv_results_` has:
        numerical columns are np.ma.zeros, masked=True with mask fill = np.nan
        other columns are np.ma.empty, masked=True with mask fill = np.nan

    # ALWAYS THE SAME
    'mean_fit_time': []
    'std_fit_time': []
    'mean_score_time': []
    'std_score_time': []

    The mean_fit_time, std_fit_time, mean_score_time and std_score_time
    are all in seconds.

    ** **** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    THEN ALWAYS 'param_{param}' (UNIQUE PARAMETERS IN ALL PARAM GRIDS
    in param_grid)
    for idx, _grid in enumerate(param_grid):
        params = sorted(list(_grid.keys()))
        for param in params:
            if param not in cv_results:
                cv_results[f'param_{param}'] = empty

    In our example
    'param_gamma': []
    'param_kernel': []
    'param_degree': []

    ** **** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    THEN ALWAYS params, WHICH FILLS WITH DICTS FOR EVERY POSSIBLE
    PERMUTATION FOR THE PARAM GRIDS IN `param_grid`.
    Note that `cv_results_` dict key 'params' stores a vector of dictionaries
    that are the parameter settings for every search permutation.
    PASS THESE DICTS TO set_params FOR THE ESTIMATOR.

    In our example:
    'params': [{'kernel': 'poly', 'degree': 2}, ...]

    ** **** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    #THEN ALWAYS
    for metric in scoring:
        suffix = 'score' if len(scoring)==1 else f'{metric}'

        # THEN ALWAYS
        'best_threshold_{suffix}': []

        # THEN ALWAYS
        for split in range(cv):
            f'split{split}_test_{suffix}': []

        e.g,:
        f'split0_test_score': []
        f'split1_test_score': []
        --- or ---
        f'split0_test_accuracy': []
        f'split1_test_accuracy': []

        THEN ALWAYS
        f'mean_test_{suffix}': [],
        f'std_test_{suffix}': [],
        f'rank_test_{suffix}': [],

        e.g.:
        f'mean_test_accuracy': [],
        f'std_test_accuracy': [],
        f'rank_test_accuracy': [],

        ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # CONDITIONALLY:
        if `return_train_score` is True:

            for split in range(cv):
                f'split{split}_train_{suffix}'

            e.g.:
            f'split0_train_score': []
            f'split1_train_score': []
            --- or ---
            f'split0_train_accuracy': []
            f'split1_train_accuracy': []

            THEN:
            f'mean_train_{suffix}': []
            f'std_train_{suffix}': []

            e.g.:
            f'mean_train_accuracy': []
            f'std_train_accuracy': []

        ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    Parameters
    ----------
    _param_grid : ParamGridsWIPType
        List of dictionaries, each dictionary being keyed with parameter
        names and the values are iterables of their respective values to
        be searched.
    _n_splits : int
        The number of folds (splits) to use for cross validation.
    _scorer : ScorerWIPType
        A dictionary keyed by scorer name with the scorer callables as
        values. Note that these callables are sklearn metrics and not
        sklearn 'make_scorer'.
    _return_train_score : bool
        When True, calculate the scores for the train folds in addition
        to the test folds.

    Returns
    -------
    __ : tuple[CVResultsType, NDArrayHolderType]
        cv_results_ : CVResultsType
            A cv_results dictionary, empty other than the individual
            'param' columns and the 'params' column, which are pre-filled
            with the hyperparameter values to be run on the corresponding
            search permutation.

        PARAM_GRID_KEY : NDArrayHolderType
            A vector of integers with length equal to the number of
            trials in the grid search, i.e., the length of the masked
            arrays in `cv_results_`. Indicates the index of the param
            grid in `param_grid` that the search trial is associated
            with.

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _val_param_grid(_param_grid, _must_be_list_dict=True)

    if int(_n_splits) != _n_splits:
        raise TypeError(f"'cv' must be int >= 2")
    if _n_splits < 2:
        raise ValueError(f"'cv' must be int >= 2")

    _val_scoring(_scorer, _must_be_dict=True)

    if not isinstance(_return_train_score, bool):
        raise TypeError("'return_train_score' must be bool")
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # BUILD VECTOR OF COLUMN NAMES ** ** ** ** ** ** ** ** ** ** ** **

    COLUMNS: list[str] = []
    DTYPES: list[Type[np.float64 | object]] = []

    COLUMNS += ['mean_fit_time', 'std_fit_time', 'mean_score_time', 'std_score_time']
    DTYPES += [np.float64 for _ in range(4)]

    # PARAM NAMES
    _unq = []
    for _grid in _param_grid:
        _unq += sorted([f'param_{i}' for i in _grid.keys() if i not in _unq])

    COLUMNS += _unq
    DTYPES += [object for _ in _unq]

    del _unq
    assert len(COLUMNS) == len(DTYPES), "len(COLUMNS) != len(DTYPES)"


    # PARAM DICTS
    COLUMNS += ['params']
    DTYPES += [object]


    # SCORES
    for metric in _scorer:

        if len(_scorer) == 1:
            metric = 'score'   # sneaky, this sets the name for everything below
            COLUMNS += [f'best_threshold']
            DTYPES += [np.float64]
        else:
            COLUMNS += [f'best_threshold_{metric}']
            DTYPES += [np.float64]

        for split in range(_n_splits):
            COLUMNS += [f'split{split}_test_{metric}']
            DTYPES += [np.float64]


        for _type in ['mean', 'std', 'rank']:
            COLUMNS += [f'{_type}_test_{metric}']
            DTYPES += [np.float64]

        if _return_train_score:
            for split in range(_n_splits):
                COLUMNS += [f'split{split}_train_{metric}']
                DTYPES += [np.float64]

            for _type in ['mean', 'std']:
                COLUMNS += [f'{_type}_train_{metric}']
                DTYPES += [np.float64]

    # END BUILD VECTOR OF COLUMN NAMES ** ** ** ** ** ** ** ** ** ** **

    # ABOVE WE SET THE WIDTH OF CV RESULTS, NOW GET THE LENGTH
    # GET FULL COUNT OF ROWS FOR ALL PERMUTATIONS ACROSS ALL GRIDS
    total_rows = 0
    for _grid in _param_grid:
        if _grid == {}:
            # if an empty grid is passed one permutation will be run with
            # the default parameters for the estimator. (set_params() will
            # apply {} and no parameters will be set, the parameters will
            # not be changed away from the default for the estimator.)
            total_rows += 1
        else:
            total_rows += np.prod(list(map(len, _grid.values())))

    total_rows = int(total_rows)

    # BUILD cv_results_
    cv_results_ = {}
    for column_name, _dtype in zip(COLUMNS, DTYPES):

        # 24_07_11, empirically verified that sk cv_results_ columns are
        # masked empty for str (object) params and masked zeros otherwise
        if 'float' in str(_dtype).lower():
            cv_results_[column_name] = np.ma.zeros(total_rows, dtype=_dtype)
        else:
            cv_results_[column_name] = np.ma.empty(total_rows, dtype=_dtype)

        cv_results_[column_name].mask = True
        cv_results_[column_name] = cv_results_[column_name].filled(fill_value=np.nan)


    PARAM_GRID_KEY: NDArrayHolderType = np.empty(total_rows, dtype=np.uint8)

    del COLUMNS, DTYPES, total_rows

    # ##################################################################
    # POPULATE KNOWN FIELDS IN cv_results_ (only columns associated with params)

    ctr = 0
    for grid_idx, _grid in enumerate(_param_grid):

        # sort grid keys to get same fill as sk GSCV
        _grid = {k:_grid[k] for k in sorted(list(_grid.keys()))}

        PARAMS = list(_grid.keys())
        VALUES = list(_grid.values())

        # if an empty grid, put in an empty grid for 'params'
        if len(VALUES) == 0:
            PARAM_GRID_KEY[ctr] = grid_idx
            cv_results_['params'][ctr] = _grid
            ctr += 1
            continue

        # a permutation IN permuter(VALUES) LOOKS LIKE (grid_idx_param_0,
        # grid_idx_param_1, grid_idx_param_2,....)
        # BUILD INDIVIDUAL param_grids TO GIVE TO estimator.set_params()
        # FROM THE PARAMS IN "PARAMS" AND VALUES KEYED FROM "VALUES"
        for TRIAL in permuter(VALUES):
            trial_param_grid = dict()
            for param_idx, value_idx in enumerate(TRIAL):

                # 24_08_31 convert np ints to py ints, np bool to py bool
                # (and why not do floats too) to get GSTCV to pass an
                # autogridsearch test that sk_GSCV was passing.
                # 24_09_01 this is (was) a must because these values will
                # be transferred to best_params_, then in autogridsearch
                # those values will be transferred into the next param
                # grid, and cannot have np.True_ or np.int because of
                # 'params' grid validation in autogridsearch
                # 24_09_02 the validation of contents of 'params' grids
                # has been disabled, but keep this anyway.
                value = VALUES[param_idx][value_idx]
                _type = str(type(value))
                if 'int' in _type:
                    value = int(value)
                elif 'float' in _type:
                    value = float(value)
                elif 'bool' in _type:
                    value = bool(value)
                else:
                    pass
                # end added this 24_08_31 ** * ** * ** * ** * ** * ** *

                cv_results_[f'param_{PARAMS[param_idx]}'][ctr] = value
                trial_param_grid[PARAMS[param_idx]] = value

            cv_results_['params'][ctr] = trial_param_grid

            PARAM_GRID_KEY[ctr] = grid_idx

            ctr += 1

    del ctr, grid_idx, _grid, PARAMS, VALUES
    try:
        del TRIAL, trial_param_grid, param_idx, value_idx, value, _type
    except:
        pass

    # END POPULATE KNOWN FIELDS IN cv_results_ (only columns associated
    # with params) #####################################################


    return cv_results_, PARAM_GRID_KEY




