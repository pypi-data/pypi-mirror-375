# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from .._type_aliases import KeepType
from ...__shared._type_aliases import XContainer

import numbers

from ._keep_and_columns import _val_keep_and_columns

from ...__shared._validation._X import _val_X
from ...__shared._validation._equal_nan import _val_equal_nan
from ...__shared._validation._atol import _val_atol
from ...__shared._validation._rtol import _val_rtol



def _validation(
    _X: XContainer,
    _columns: npt.NDArray[str] | None,
    _keep: KeepType,
    _equal_nan: bool,
    _rtol: numbers.Real,
    _atol: numbers.Real
) -> None:
    """Centralized hub for performing parameter validation.

    See the individual modules for more information.

    Parameters
    ----------
    _X : XContainer of shape (n_samples, n_features)
        The data to be searched for constant columns.
    _columns : NDArray[str] | None of shape (n_features,)
        Exposed if `X` was passed in a container that has a header,
        otherwise None.
    _keep : KeepType
        The strategy for handling the constant columns. See 'The Keep
        Parameter' discussion section for a lengthy explanation of the
        `keep` parameter.
    _equal_nan : bool
        If `equal_nan` is True, exclude nan-likes from computations that
        discover constant columns. This essentially assumes that the nan
        value would otherwise be equal to the mean of the non-nan values
        in the same column. If `equal_nan` is False and any value in a
        column is nan, do not assume that the nan value is equal to the
        mean of the non-nan values in the same column, thus making the
        column non-constant. This is in line with the normal numpy
        handling of nan values.
    _rtol : numbers.Real
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    _atol : numbers.Real
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.

    Returns
    -------
    None

    """


    _val_X(_X)

    _val_keep_and_columns(_keep, _columns, _X)

    _val_equal_nan(_equal_nan)

    _val_rtol(_rtol)

    _val_atol(_atol)



