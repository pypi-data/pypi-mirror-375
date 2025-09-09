# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases_num import (
    NumDataType,
    NumGridType
)
from ..._type_aliases import LogspaceType

from copy import deepcopy
import warnings

import numpy as np



def _validate_int_float_linlogspace(
    _SINGLE_GRID: NumGridType,
    _is_logspace: LogspaceType,
    _posn: int,
    _is_hard: bool,
    _hard_min: NumDataType,
    _hard_max: NumDataType,
    _points: int,
    _module_name: str
) -> None:
    """
    Validate params for:

        :func:`_float_linspace`

        :func:`_float_logspace`

        :func:`_int_linspace_unit_gap`

        :func:`_int_linspace_gap_gt1`

        :func:`_int_logspace_unit_gap`

        :func:`_int_logspace_gap_gt1`

    Parameters
    ----------
    _SINGLE_GRID : NumGridType
        Numerical parameter search grid from the previous round.
    _posn : int
        Index in `_SINGLE_GRID` where best value found by GridSearch
        fell.
    _is_logspace : LogspaceType
        Whether `_SINGLE_GRID` is in lin or logspace, and if in logspace,
        what the log interval is.
    _is_hard : bool
        Whether the parameter has hard left and right boundaries. This
        field is read from the dtype/search field in `_params`. If hard,
        the left and right bounds are set from the lowest and highest
        values in the first round's search grid (the grid that was
        passed to `params` at init.)
    _hard_min : NumDataType
        If hard, the minimum value in the first round's search grid.
    _hard_max : NumDataType
        If hard, the maximum value in the first round's search grid.
    _points : int
        Number of points to use in the next search grid, subject to
        constraints of `_hard_min`, `_hard_max`, universal lower bound,
        etc.
    _module_name : str
        The name of the module calling this module.

    Returns
    -------
    _SINGLE_GRID : NumGridType
        Search grid converted to a list.

    """

    # module_name ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if not isinstance(_module_name, str):
        raise TypeError(
            f"_module_name must be a string of the calling module's name"
        )

    _module_name = _module_name.upper()

    _valid_module_name = False
    if 'FLOAT' in _module_name:
        _valid_module_name = True
    elif 'INT' not in _module_name:
        raise ValueError(
            f"'_module_name' must contain 'FLOAT' OR 'INT' to correctly "
            f"set '_universal_lower_bound'"
        )
    else:
        for _gap_type in ['UNIT', 'GT_1']:
            if _gap_type in _module_name:
                _valid_module_name = True

    if not _valid_module_name:
        raise ValueError(
            f"for 'int' modules, _module_name must contain either ('unit' "
            f"or 'gt_1') \nto indicate which gap validation and universal "
            f"lower bound to use"
        )

    if not any(map(lambda x: x in _module_name, ('LINSPACE', 'LOGSPACE'))):
        raise ValueError(
            f"'_module_name' must contain either 'linspace' or 'logspace"
        )

    del _valid_module_name
    # END module_name ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # universal lower bound ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if 'INT' in _module_name:
        _univeral_lower_bound = 1
    elif 'FLOAT' in _module_name:
        _univeral_lower_bound = 0

    # END universal lower bound ** * ** * ** * ** * ** * ** * ** * ** *

    # search grid ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    try:
        iter(_SINGLE_GRID)
        if isinstance(_SINGLE_GRID, (dict, str)):
            raise TypeError
        _SINGLE_GRID = list(_SINGLE_GRID)
    except TypeError:
        raise TypeError(f"_SINGLE_GRID must be a list-like")
    except Exception as e:
        raise Exception(
            f"grid validation excepted for uncontrolled reason -- {e}"
        )

    try:
        list(map(float, _SINGLE_GRID))
    except:
        raise TypeError(f"GRID must contain numerics")

    if all(map(lambda x: x in _module_name, ('INT', 'LINSPACE'))):
        try:
            if not np.array_equiv(_SINGLE_GRID, list(map(int, _SINGLE_GRID))):
                raise Exception
        except:
            raise TypeError(f"GRID contains floats")

    _gaps = np.array(_SINGLE_GRID)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _log_gaps = np.log10(_SINGLE_GRID)
    if 'LINSPACE' in _module_name:
        pass # _gaps = _gaps
    elif 'LOGSPACE' in _module_name:
        _gaps = deepcopy(_log_gaps)
    _gaps = np.unique(_gaps[1:] - _gaps[:-1])
    if 0 in _gaps:
        raise ValueError(f"duplicate entries in _SINGLE_GRID")
    _log_gaps = np.unique(_log_gaps[1:] - _log_gaps[:-1])
    if 'FLOAT' in _module_name:
        pass
    elif 'UNIT' in _module_name and (len(_gaps) > 1 or _gaps[0] != 1):
        raise ValueError(f"_SINGLE_GRID does not have unit gaps")
    elif 'GT_1' in _module_name and (len(_gaps) == 1 and _gaps[0] == 1):
        raise ValueError(f"_SINGLE_GRID has unit gaps")

    del _gaps

    if min(_SINGLE_GRID) < _univeral_lower_bound:
        raise ValueError(f"min(_SINGLE_GRID) < {_univeral_lower_bound}")

    # END search grid ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _posn ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    err_msg = f"'_posn' must be an integer >= 0"
    try:
        float(_posn)
        if isinstance(_posn, bool):
            raise Exception
        if int(_posn) != _posn:
            raise Exception
        if _posn < 0:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except:
        raise TypeError(err_msg)

    del err_msg

    if _posn not in range(len(_SINGLE_GRID)):
        raise ValueError(
            f"'_posn' ({_posn}) out of range for grid of len "
            f"({len(_SINGLE_GRID)})"
        )

    # END _posn ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _is_logspace ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    if not isinstance(_is_logspace, (bool, float)):
        raise TypeError(f"'_is_logspace' must be False or a float > 0")

    if len(_log_gaps) > 1 and _is_logspace:
        raise ValueError(
            f"a log-space search grid has unexpectedly become not "
            f"log-space. \nyou may have a runaway condition that has "
            f"caused floating point round-off error. \nconsider using a "
            f"linear search space or setting `total_passes_is_hard` to "
            f"True."
        )

    if len(_log_gaps) == 1 and not _is_logspace:
        raise ValueError(
            f"_is_logspace False for log search space."
            f"\n{_SINGLE_GRID=}"
        )

    del _log_gaps

    # END _is_logspace ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _is_hard ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    if not isinstance(_is_hard, bool):
        raise TypeError(f"_is_hard must be a bool")
    # END _is_hard ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # _hard_min, _hard_max ** * ** * ** * ** * ** * ** * ** * ** * ** *

    __ = [_hard_min, _hard_max]

    err_msg = (f"_hard_min ({_hard_min}), _hard_max ({_hard_max}) must be integers")
    if any(list(map(isinstance, __, (bool for _ in __)))):
        raise TypeError(err_msg)

    if 'INT' in _module_name:
        try:
            if not np.array_equiv(list(map(int, __)), list(__)):
                raise Exception
        except:
            raise TypeError(err_msg)

    del __, err_msg


    if _hard_min < _univeral_lower_bound:
        raise ValueError(f"hard_min < {_univeral_lower_bound}")

    if _hard_max < _univeral_lower_bound:
        raise ValueError(f"hard_max < {_univeral_lower_bound}")

    if _is_hard and _hard_min > min(_SINGLE_GRID):
        raise ValueError(f"hard_min > min(GRID)")

    if _is_hard and _hard_max < max(_SINGLE_GRID):
        raise ValueError(f"hard_max < max(GRID)")

    # END _hard_min, _hard_max ** * ** * ** * ** * ** * ** * ** * ** *


    # _points ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    try:
        if int(_points) != _points:
            raise Exception
    except:
        raise TypeError(f"_points must be an integer")

    if _points < 3:
        raise ValueError(
            f"_points must be >= 3 (_points == 1 should not be able to "
            f"reach these modules, _points == 2 for softs should be "
            f"caught in initial validation and blocked thereafter)"
        )

    # _points ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **









