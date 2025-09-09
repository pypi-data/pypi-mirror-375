# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)
from .._type_aliases import FeatureNameCombinerType
from ...__shared._type_aliases import XContainer

import numbers
import warnings

from ._degree__min_degree import _val_degree__min_degree
from ._feature_name_combiner import _val_feature_name_combiner
from ._keep import _val_keep
from ._X_supplemental import _val_X_supplemental

from ...__shared._validation._X import _val_X
from ...__shared._validation._equal_nan import _val_equal_nan
from ...__shared._validation._atol import _val_atol
from ...__shared._validation._rtol import _val_rtol
from ...__shared._validation._n_jobs import _val_n_jobs
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer



def _validation(
    _X: XContainer,
    _degree: int,
    _min_degree: int,
    _scan_X: bool,
    _keep: Literal['first', 'last', 'random'],
    _interaction_only: bool,
    _sparse_output: bool,
    _feature_name_combiner: FeatureNameCombinerType,
    _rtol: numbers.Real,
    _atol: numbers.Real,
    _equal_nan: bool,
    _n_jobs: int | None,
    _job_size: int
) -> None:
    """Centralized hub for performing parameter validation.

    See the individual modules for more information.

    Parameters
    ----------
    _X : XContainer of shape (n_samples, n_features)
        The data.
    _degree : int
        The maximum degree of the polynomial expansion.
    _min_degree : int
        The minimum degree of the polynomial expansion.
    _scan_X : bool
        Whether to scan X for constants with `InterceptManager` and
        duplicates with `ColumnDeduplicator`.
    _keep : Literal['first', 'last', 'random']
        The instruction for choosing a column to keep out of a set of
        duplicates.
    _interaction_only : bool
        Whether to only include first-order interaction terms in the
        expansion.
    _sparse_output : bool
        Whether to return the output as a scipy sparse array.
    _feature_name_combiner : FeatureNameCombinerType
        The instruction for how to build the polynomial expansion feature
        name.
    _rtol : numbers.Real
        The relative difference tolerance for equality.
    _atol : numbers.Real
        The absolute difference tolerance for equality.
    _equal_nan : bool
        How to handle nans in equality comparisons.
    _n_jobs : int | None
        The number of joblib Parallel jobs to use when scanning for
        duplicate columns.
    _job_size : int
        The number of columns to send to a joblib job. Must be an
        integer greater than or equal to 2.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    FeatureNameCombinerType:
        Callable[[Sequence[str], tuple[int, ...]], str]
        | Literal['as_feature_names', 'as_indices']

    """


    _val_keep(_keep)

    _val_any_bool(_scan_X, 'scan_X', _can_be_None=False)

    if _scan_X is False:
        warnings.warn(
            f"'scan_X' is set to False. Do this with caution, only when "
            f"you are certain that X does not have constant or duplicate "
            f"columns. Otherwise the results from :meth: 'transform' will "
            f"be nonsensical."
        )

    _val_degree__min_degree(_degree, _min_degree)

    _val_feature_name_combiner(_feature_name_combiner)

    _val_any_bool(_interaction_only, 'interaction_only', _can_be_None=False)

    _val_any_bool(_sparse_output, 'sparse_output', _can_be_None=False)

    _val_equal_nan(_equal_nan)

    _val_rtol(_rtol)

    _val_atol(_atol)

    _val_n_jobs(_n_jobs)

    # _val_any_integer allows lists
    if not isinstance(_job_size, numbers.Integral):
        raise TypeError(f"'job_size' must be an integer >= 2. Got {_job_size}.")
    _val_any_integer(_job_size, 'job_size', _min=2)

    _val_X(_X)

    _val_X_supplemental(_X, _interaction_only)



