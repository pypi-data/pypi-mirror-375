# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_int import (
    IntDataType,
    IntGridType
)
from ..._type_aliases import LogspaceType

import sys

from .._int._int_logspace_core import _int_logspace_core
from ..._get_next_param_grid._validation._validate_int_float_linlogspace import \
    _validate_int_float_linlogspace
from ......utilities._get_module_name import get_module_name



def _int_logspace_unit_gap(
    _SINGLE_GRID: IntGridType,
    _is_logspace: LogspaceType,
    _posn: int,
    _is_hard: bool,
    _hard_min: IntDataType,
    _hard_max: IntDataType,
    _points: int
) -> IntGridType:
    """Build a new grid in linspace for a single integer parameter based
    on the previous search round's logspace grid and the best value
    discovered by GridSearch, subject to constraints imposed by 'hard',
    universal lower bound on integers, etc.

    With additional validation for unitary log intervals. This should
    only be accessed on the first regular pass after shifts. Logspaces
    convert to linspace.

    Parameters
    ----------
    _SINGLE_GRID : IntGridType
        The last round's logspace search grid for a single parameter.
        `_SINGLE_GRID` must be sorted ascending, and is presumed to be
        by :func:`_param_conditioning._params` (at least initially).
    _is_logspace : LogspaceType
        For numerical params, if the space is linear, or some other
        non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _posn : int
        The index position in the previous round's grid where the best
        value fell.
    _is_hard : bool
        Whether the parameter has hard left and right boundaries. This
        field is read from the dtype/search field in _params. If hard,
        the left and right bounds are set from the lowest and highest
        values in the first round's search grid (the grid that was
        passed to `params` at init.)
    _hard_min : IntDataType
        The minimum value in the first round's search grid. Ignored if
        not hard.
    _hard_max : IntDataType
        The maximum value in the first round's search grid. Ignored if
        not hard.
    _points : int
        The target number of points for the next search grid. This
        number may not be achieved exactly on ranges that are not evenly
        divisible.

    Returns
    -------
    _OUT_GRID : IntGridType
        New linspace search grid for the current pass' upcoming search.

    See Also
    --------
    _int_logspace_core

    """


    # 24_05_18_19_27_00 _validation must stay here to get the module name,
    # cannot put in _int
    _validate_int_float_linlogspace(
        _SINGLE_GRID,
        _is_logspace,
        _posn,
        _is_hard,
        _hard_min,
        _hard_max,
        _points,
        get_module_name(str(sys.modules[__name__]))
    )


    return _int_logspace_core(
        _SINGLE_GRID,
        _is_logspace,
        _posn,
        _is_hard,
        _hard_min,
        _hard_max,
        _points
    )






