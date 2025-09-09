# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy.typing as npt

import time

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl

from uuid import uuid4

from sklearn.preprocessing import StandardScaler as sk_StandardScaler

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression

from sklearn.pipeline import Pipeline

from sklearn.model_selection import GridSearchCV as sk_GSCV
from sklearn.model_selection import ParameterGrid

from sklearn.metrics import (
    precision_score,
    recall_score,
    accuracy_score,
    balanced_accuracy_score
)

from pybear.model_selection.GSTCV._GSTCV.GSTCV import GSTCV as sk_GSTCV

from pybear.model_selection.GSTCV._GSTCVMixin._validation._scoring \
    import master_scorer_dict



# data objects ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
@pytest.fixture(scope='session')
def _rows():
    return int(np.random.randint(5, 200))


@pytest.fixture(scope='session')
def _cols():
    return int(np.random.randint(1, 10))


@pytest.fixture(scope='session')
def X_np(_rows, _cols):
    np.random.seed(19)
    return np.random.randint(0, 10, (_rows, _cols))


@pytest.fixture(scope='session')
def COLUMNS(_cols):
    return [str(uuid4())[:4] for _ in range(_cols)]


@pytest.fixture(scope='session')
def X_pd(X_np, COLUMNS):
    return pd.DataFrame(data=X_np, columns=COLUMNS)


@pytest.fixture(scope='session')
def y_np(_rows):
    np.random.seed(19)
    return np.random.randint(0, 2, (_rows,))


@pytest.fixture(scope='session')
def y_pd(y_np):
    return pd.DataFrame(data=y_np, columns=['y'])

# END data objects ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# WIP init param objects ** * ** * ** * ** * ** * ** * ** * ** * ** * **

@pytest.fixture(scope='session')
def standard_WIP_scorer():
    return {
        'precision': precision_score,
        'recall': recall_score,
        'accuracy': accuracy_score,
        'balanced_accuracy': balanced_accuracy_score
    }


# END WIP init param objects ** * ** * ** * ** * ** * ** * ** * ** * **


# estimator init params ** * ** * ** * ** * ** * ** * ** * ** * ** * **

@pytest.fixture(scope='session')
def sk_log_init_params():
    return {
        'C':1e-8,
        'tol': 1e-1,
        'max_iter': 1,
        'fit_intercept': False,
        'solver': 'lbfgs'
    }

# END estimator init params ** * ** * ** * ** * ** * ** * ** * ** * ** *

# transformers / estimators ** * ** * ** * ** * ** * ** * ** * ** * ** *
@pytest.fixture(scope='session')
def sk_standard_scaler():
    return sk_StandardScaler(with_mean=True, with_std=True)


@pytest.fixture(scope='session')
def sk_est_log(sk_log_init_params):
    return sk_LogisticRegression(**sk_log_init_params)
# END transformers / estimators ** * ** * ** * ** * ** * ** * ** * ** *


# grid search params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
@pytest.fixture(scope='session')
def param_grid_sk_log():
    return {'C': [1e-4, 1e-5]}


@pytest.fixture(scope='session')
def standard_thresholds():
    return np.linspace(0.4, 0.6, 3)


@pytest.fixture(scope='session')
def standard_cv_int():
    return 4


@pytest.fixture(scope='session')
def standard_refit():
    return False


@pytest.fixture(scope='session')
def one_scorer():
    return 'accuracy'


@pytest.fixture(scope='session')
def two_scorers():
    return ['accuracy', 'balanced_accuracy']


@pytest.fixture(scope='session')
def standard_error_score():
    return 'raise'


@pytest.fixture(scope='session')
def standard_n_jobs():
    return 1

# END grid search params ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# gs(t)cv init params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

@pytest.fixture(scope='session')
def sk_gscv_init_params(
    sk_est_log, param_grid_sk_log, one_scorer, standard_n_jobs,
    standard_refit, standard_cv_int, standard_error_score
):

    return {
        'estimator': sk_est_log,
        'param_grid': param_grid_sk_log,
        'scoring': one_scorer,
        'n_jobs': standard_n_jobs,
        'refit': standard_refit,
        'cv': standard_cv_int,
        'verbose': 0,
        'pre_dispatch': '2*n_jobs',
        'error_score': standard_error_score,
        'return_train_score': False
    }


@pytest.fixture(scope='session')
def sk_gstcv_init_params(
    sk_est_log, param_grid_sk_log, standard_thresholds, one_scorer,
    standard_n_jobs, standard_refit, standard_cv_int, standard_error_score
):
    return {
        'estimator': sk_est_log,
        'param_grid': param_grid_sk_log,
        'thresholds': standard_thresholds,
        'scoring': one_scorer,
        'n_jobs': standard_n_jobs,
        'pre_dispatch': '2*n_jobs',
        'refit': standard_refit,
        'cv': standard_cv_int,
        'verbose': 0,
        'error_score': standard_error_score,
        'return_train_score': False
    }

# END gs(t)cv init params ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ESTIMATORS - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * ** *

# gscv log est one scorer, various refits
@pytest.fixture(scope='session')
def sk_GSCV_est_log_one_scorer_prefit(sk_gscv_init_params):

    return sk_GSCV(**sk_gscv_init_params)


@pytest.fixture(scope='session')
def sk_GSCV_est_log_one_scorer_postfit_refit_false(
    sk_gscv_init_params, X_np, y_np
):

    return sk_GSCV(**sk_gscv_init_params).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSCV_est_log_one_scorer_postfit_refit_str(
    sk_gscv_init_params, one_scorer, X_np, y_np
):

    return sk_GSCV(
        **sk_gscv_init_params
    ).set_params(refit=one_scorer).fit(X_np, y_np)

# END gscv log est one scorer, various refits



# gstcv log est one scorer, various refits
@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_prefit(sk_gstcv_init_params):

    return sk_GSTCV(**sk_gstcv_init_params)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_np(
    sk_gstcv_init_params, X_np, y_np
):

    return sk_GSTCV(**sk_gstcv_init_params).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_false_fit_on_pd(
    sk_gstcv_init_params, X_pd, y_pd
):

    return sk_GSTCV(**sk_gstcv_init_params).fit(X_pd, y_pd)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_np(
    sk_gstcv_init_params, one_scorer, X_np, y_np
):
    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(refit=one_scorer).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_pd(
    sk_gstcv_init_params,one_scorer, X_pd, y_pd
):

    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(refit=one_scorer).fit(X_pd, y_pd)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_np(
    sk_gstcv_init_params, X_np, y_np
):

    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(refit=lambda x: 0).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_one_scorer_postfit_refit_fxn_fit_on_pd(
    sk_gstcv_init_params, sk_est_log, param_grid_sk_log, X_pd, y_pd
):

    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(refit=lambda x: 0).fit(X_pd, y_pd)

# END gstcv log est one scorer, various refits

# END ESTIMATORS - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * **
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *




# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ESTIMATORS - TWO SCORERS ** * ** * ** * ** * ** * ** * ** * ** * ** *

# gstcv log est two scorers, various refits
@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_prefit(sk_gstcv_init_params, two_scorers):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        scoring=two_scorers
    )


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_np(
    sk_gstcv_init_params, two_scorers, X_np, y_np
):

    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(scoring=two_scorers).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_false_fit_on_pd(
    sk_gstcv_init_params, two_scorers, X_pd, y_pd
):

    return sk_GSTCV(
        **sk_gstcv_init_params
    ).set_params(scoring=two_scorers).fit(X_pd, y_pd)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_np(
    sk_gstcv_init_params, one_scorer, two_scorers, X_np, y_np
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        scoring=two_scorers, refit=one_scorer).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_pd(
    sk_gstcv_init_params, two_scorers, one_scorer, X_pd, y_pd
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        scoring=two_scorers,
        refit=one_scorer
    ).fit(X_pd, y_pd)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_np(
    sk_gstcv_init_params, two_scorers, X_np, y_np
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        scoring=two_scorers,
        refit=lambda x: 0
    ).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_est_log_two_scorers_postfit_refit_fxn_fit_on_pd(
    sk_gstcv_init_params, two_scorers, X_pd, y_pd
):
    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        scoring=two_scorers,
        refit=lambda x: 0
    ).fit(X_pd, y_pd)

# END gstcv log est two scorers, various refits


# END ESTIMATORS - TWO SCORERS ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *





# pipeline estimators ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

@pytest.fixture(scope='session')
def sk_pipe_log(sk_standard_scaler, sk_est_log):
    return Pipeline(
        steps=[
            ('sk_StandardScaler', sk_standard_scaler),
            ('sk_logistic', sk_est_log)
        ]
    )


# END pipeline esimators ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# pipe param grids ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

@pytest.fixture(scope='session')
def param_grid_pipe_sk_log():
    return {
        'sk_StandardScaler__with_mean': [True, False],
        'sk_logistic__C': [1e-4, 1e-5]
    }

# END pipe param grids ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# PIPELINES - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * ** * **

# gscv log pipe one scorer, various refits
@pytest.fixture(scope='session')
def sk_GSCV_pipe_log_one_scorer_prefit(
    sk_gscv_init_params, sk_pipe_log, param_grid_pipe_sk_log
):

    return sk_GSCV(**sk_gscv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log
    )


@pytest.fixture(scope='session')
def sk_GSCV_pipe_log_one_scorer_postfit_refit_false(
    sk_gscv_init_params, sk_pipe_log, param_grid_pipe_sk_log, X_np, y_np
):

    return sk_GSCV(**sk_gscv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log
    ).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSCV_pipe_log_one_scorer_postfit_refit_str(
    sk_gscv_init_params, sk_pipe_log, param_grid_pipe_sk_log, one_scorer,
    X_np, y_np
):

    return sk_GSCV(**sk_gscv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log,
        refit=one_scorer
    ).fit(X_np, y_np)

# END gscv log pipe one scorer, various refits



# gstcv log pipe one scorer, various refits
@pytest.fixture(scope='session')
def sk_GSTCV_pipe_log_one_scorer_prefit(
    sk_gstcv_init_params, sk_pipe_log, param_grid_pipe_sk_log
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log
    )


@pytest.fixture(scope='session')
def sk_GSTCV_pipe_log_one_scorer_postfit_refit_false_fit_on_np(
    sk_gstcv_init_params, sk_pipe_log, param_grid_pipe_sk_log, X_np, y_np
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log
    ).fit(X_np, y_np)


@pytest.fixture(scope='session')
def sk_GSTCV_pipe_log_one_scorer_postfit_refit_str_fit_on_np(
    sk_gstcv_init_params, sk_pipe_log, param_grid_pipe_sk_log, one_scorer,
    X_np, y_np
):

    return sk_GSTCV(**sk_gstcv_init_params).set_params(
        estimator=sk_pipe_log,
        param_grid=param_grid_pipe_sk_log,
        refit=one_scorer
    ).fit(X_np, y_np)

# END gstcv log pipe one scorer, various refits


# END PIPELINES - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * **
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



@pytest.fixture(scope='module')
def _cv_results_template(request):

    _n_splits = request.param['_n_splits']
    _n_rows = request.param['_n_rows']
    _scorer_names = request.param['_scorer_names']
    _grids = request.param['_grids']
    _return_train_score = request.param['_return_train_score']
    _fill_param_columns = request.param['_fill_param_columns']

    # build _scorer ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    try:
        iter(_scorer_names)
        if isinstance(_scorer_names, (str, dict)):
            raise Exception
    except:
        raise Exception(
            f"'LIST_OF_SCORERS' must be an iterable of scorer names")

    _scorer = {}
    for _name in _scorer_names:
        if _name not in master_scorer_dict:
            raise ValueError(f"'{_name}' is not an allowed scorer")

        _scorer[_name] = master_scorer_dict[_name]

    # END build _scorer ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    col_template = lambda _dtype: np.ma.masked_array(
        np.empty(_n_rows),
        mask=True,
        dtype=_dtype
    )

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    a = {
        'mean_fit_time': col_template(np.float64),
        'std_fit_time': col_template(np.float64),
        'mean_score_time': col_template(np.float64),
        'std_score_time': col_template(np.float64)
    }
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    b = {}
    for _grid in _grids:
        for _param in _grid:
            # this will overwrite any identical, preventing duplicate
            if isinstance(_grid[_param][0], bool):
                b[f'param_{_param}'] = col_template(bool)
            else:
                try:
                    float(_grid[_param][0])
                    b[f'param_{_param}'] = col_template(float)
                except:
                    b[f'param_{_param}'] = col_template(str)

        b = b | {'params': col_template(object)}

    if _fill_param_columns:
        row_idx = 0
        for _grid in _grids:
            for _permutation in ParameterGrid(_grid):
                # ParameterGrid lays out permutations in the same order
                # as pybear.permuter

                b['params'][row_idx] = _permutation

                for _param in _grid:
                    if f'param_{_param}' not in b:
                        raise Exception
                    b[f'param_{_param}'][row_idx] = _permutation[_param]

                row_idx += 1


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    c = {}
    for metric in _scorer:
        suffix = 'score' if len(_scorer) == 1 else f'{metric}'

        if len(_scorer) == 1:
            c[f'best_threshold'] = col_template(np.float64)
        else:
            c[f'best_threshold_{metric}'] = col_template(np.float64)

        for split in range(_n_splits):
            c[f'split{split}_test_{suffix}'] = col_template(np.float64)

        c[f'mean_test_{suffix}'] = col_template(np.float64)
        c[f'std_test_{suffix}'] = col_template(np.float64)
        c[f'rank_test_{suffix}'] = col_template(np.uint32)

        if _return_train_score is True:

            for split in range(_n_splits):
                c[f'split{split}_train_{suffix}'] = col_template(np.float64)

            c[f'mean_train_{suffix}'] = col_template(np.float64)
            c[f'std_train_{suffix}'] = col_template(np.float64)
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    return a | b | c


@pytest.fixture(scope='session')
def _format_helper():


    def foo(
        _base: npt.NDArray,
        _format: str,
        _dim: int
    ):

        """Cast dummy numpy array to desired container."""

        # _new_X can be X or y in the tests

        if _format == 'ss' and _dim == 1:
            raise ValueError(f"cant have 1D scipy sparse")

        if _format == 'py_set' and _dim == 2:
            raise ValueError(f"cant have 2D set")

        if _dim == 1 and len(_base.shape)==1:
            _intrmdt_X = _base.copy()
        elif _dim == 2 and len(_base.shape)==2:
            _intrmdt_X = _base.copy()
        elif _dim == 1 and len(_base.shape)==2:
            _intrmdt_X = _base[:, 0].copy().ravel()
        elif _dim == 2 and len(_base.shape)==1:
            _intrmdt_X = _base.copy().reshape((-1, 1))
        else:
            raise Exception

        if _format == 'py_list':
            if _dim == 1:
                _new_X = list(_intrmdt_X)
            elif _dim == 2:
                _new_X = list(map(list, _intrmdt_X))
        elif _format == 'py_tup':
            if _dim == 1:
                _new_X = tuple(_intrmdt_X)
            elif _dim == 2:
                _new_X = tuple(map(tuple, _intrmdt_X))
        elif _format == 'py_set':
            if _dim == 1:
                _new_X = set(_intrmdt_X)
            elif _dim == 2:
                # should have raised above
                raise Exception
        elif _format == 'np':
            _new_X = _intrmdt_X.copy()
        elif _format == 'pd':
            if _dim == 1:
                _new_X = pd.Series(_intrmdt_X)
            elif _dim == 2:
                _new_X = pd.DataFrame(_intrmdt_X)
        elif _format == 'ss':
            if _dim == 1:
                # should have raised above
                raise Exception
            elif _dim == 2:
                _new_X = ss.csr_array(_intrmdt_X)
        elif _format == 'pl':
            if _dim == 1:
                _new_X = pl.Series(_intrmdt_X)
            elif _dim == 2:
                _new_X = pl.from_numpy(_intrmdt_X)
        else:
            raise ValueError(f"_format_helper invalid format '{_format}'")

        del _intrmdt_X

        return _new_X

    return foo


@pytest.fixture
def _mock_classifier():

    class MockClassifier:

        def __init__(self, command='run'):

            self.command = command
            self.is_fitted = False
            # command can be 'type_error', 'other_error_raise',
            # 'other_error_not_raise', 'run'

        def fit(self, X, y, **fit_params):

            time.sleep(0.5)

            if len(fit_params) and fit_params['kill'] is True:
                raise BrokenPipeError     # an obscure error

            if self.command == 'run':
                self.score_ = self.score(X, y)
                self.is_fitted = True
            elif self.command == 'type_error':
                raise TypeError
            elif self.command == 'other_error_with_raise':
                raise TabError # an obscure error
            elif self.command == 'other_error_not_raise':
                self.score_ = np.nan
                raise TabError # an obscure error

            return self


        def score(self, X, y):

            return float(np.random.uniform(0, 1))


    return MockClassifier



