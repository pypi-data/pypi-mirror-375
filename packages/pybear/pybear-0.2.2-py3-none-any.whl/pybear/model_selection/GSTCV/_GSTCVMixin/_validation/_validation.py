# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterable,
    Literal
)
from ..._type_aliases import (
    GenericKFoldType,
    ScorerInputType,
    ClassifierProtocol,
    ThresholdsInputType,
    ParamGridInputType,
    ParamGridsInputType,
    RefitType
)

import numbers

from ._estimator import _val_estimator
from ._param_grid import _val_param_grid
from ._thresholds import _val_thresholds
from ._scoring import _val_scoring
from ._n_jobs import _val_n_jobs
from ._refit import _val_refit
from ._cv import _val_cv
from ._verbose import _val_verbose
from ._error_score import _val_error_score
from ._return_train_score import _val_return_train_score



def _validation(
    _estimator: ClassifierProtocol,
    _param_grid: ParamGridInputType | ParamGridsInputType,
    _thresholds: ThresholdsInputType,
    _scoring: ScorerInputType,
    _n_jobs: int | None,
    _refit: RefitType,
    _cv: None | int | Iterable[GenericKFoldType],
    _verbose: numbers.Real,
    _error_score: Literal['raise'] | numbers.Real,
    _return_train_score: bool
) -> None:
    """Centralized hub for validation.

    See the individual submodules for more information.

    Parameters
    ----------
    _estimator:
        ClassifierProtocol
    _param_grid:
        ParamGridInputType | ParamGridsInputType
    _thresholds:
        ThresholdsInputType
    _scoring:
        ScorerInputType
    _n_jobs:
        int | None
    _refit:
        RefitType
    _cv:
        None | int | Iterable[GenericKFoldType]
    _verbose:
        numbers.Real
    _error_score:
        numbers.Real | Literal['raise']
    _return_train_score:
        bool

    Returns
    -------
    None

    """

    _val_estimator(_estimator)

    _val_param_grid(_param_grid, _must_be_list_dict=False)

    _val_thresholds(
        _thresholds,
        _is_from_kwargs=True,
        _idx=0,
        _must_be_list_like=False
    )

    _val_scoring(_scoring, _must_be_dict=False)

    _val_n_jobs(_n_jobs)

    # this must be after _val_scoring
    _val_refit(_refit, _scoring)

    _val_cv(_cv, _can_be_None=True, _can_be_int=True)

    _val_verbose(_verbose, _can_be_raw_value=True)

    _val_error_score(_error_score)

    _val_return_train_score(_return_train_score)






