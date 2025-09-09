# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    DoNotDropType,
    ConflictType,
    KeepType,
    FeatureNamesInType
)
from ...__shared._type_aliases import XContainer

import numbers

from ._conflict import _val_conflict
from ._do_not_drop import _val_do_not_drop
from ._keep import _val_keep

from ...__shared._validation._X import _val_X
from ...__shared._validation._equal_nan import _val_equal_nan
from ...__shared._validation._atol import _val_atol
from ...__shared._validation._rtol import _val_rtol
from ...__shared._validation._n_jobs import _val_n_jobs
from ...__shared._validation._any_integer import _val_any_integer



def _validation(
    _X: XContainer,
    _columns: FeatureNamesInType | None,
    _conflict: ConflictType,
    _do_not_drop: DoNotDropType,
    _keep: KeepType,
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
    _columns : FeatureNamesInType | None
        An vector of shape (n_features,) if `X` was passed in a container
        that has a header, otherwise None.
    _conflict : ConflictType
        How to manage a conflict between the instructions.
    _do_not_drop : DoNotDropType
        Columns to preferentially keep during deduplication.
    _keep : KeepType
        Instructions for what column to keep out of a set of duplicates
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _equal_nan : bool
        How to handle nan values during comparisons.
    _n_jobs : int | None
        The number of joblib Parallel jobs to use when scanning the data
        for duplicates.
    _job_size : int
        The number of columns to send to a joblib job. Must be an integer
        greater than or equal to 2.

    Returns
    -------
    None

    """


    _val_keep(_keep)

    _val_X(_X)

    _val_do_not_drop(_do_not_drop, _X.shape[1], _columns)

    _val_conflict(_conflict)

    _val_rtol(_rtol)

    _val_atol(_atol)

    _val_equal_nan(_equal_nan)

    _val_n_jobs(_n_jobs)

    # _val_any_integer allows lists
    if not isinstance(_job_size, numbers.Integral):
        raise TypeError(f"'job_size' must be an integer >= 2. Got {_job_size}.")
    _val_any_integer(_job_size, 'job_size', _min=2)



