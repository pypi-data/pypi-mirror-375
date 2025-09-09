# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    GridsType,
    ParamsType,
    BestParamsType,
    IsLogspaceType,
    PhliteType
)

from copy import deepcopy
import numpy as np

from ._update_phlite import _update_phlite
from ._shift._shift import _shift
from ._regap_logspace import _regap_logspace
from ._drill._drill import _drill

from ._validation._validate_best_params import _validate_best_params
from ._validation._validate_grids import _validate_grids
from ._validation._validate_phlite import _validate_phlite
from ._validation._validate_is_logspace import _validate_is_logspace
from .._validation._total_passes import _val_total_passes
from .._validation._params import _val_params
from .._validation._total_passes_is_hard import _val_total_passes_is_hard
from .._validation._max_shifts import _val_max_shifts



def _get_next_param_grid(
    _GRIDS: GridsType,
    _params: ParamsType,
    _PHLITE: PhliteType,
    _IS_LOGSPACE: IsLogspaceType,
    _best_params_from_previous_pass: BestParamsType,
    _pass: int,
    _total_passes: int,
    _total_passes_is_hard: bool,
    _shift_ctr: int,
    _max_shifts: int
) -> tuple[GridsType, ParamsType, PhliteType, IsLogspaceType, int, int]:
    """The core functional method.

    This should not be reached on the first pass (pass zero). First pass
    grids should be built by :func:`_build_first_grid`. For subsequent
    passes, this module generates new grids based on the previous
    grid (as held in GRIDS[_pass-1]) and its associated `best_params_`
    (as held in `best_params_from_previous_pass`) returned from the
    `GridSearchCV` parent.

    Parameters
    ----------
    _GRIDS : GridsType
        Search grids for completed `GridSearchCV` passes and an incomplete
        search grid for the upcoming pass.
    _params : ParamsType
        Full list of all params to be searched with their respective
        grid construction instructions.
    _PHLITE : PhliteType (param has landed inside the edges)
        Boolean that indicates if a parameter has or has not landed off
        the extremes of its search grid. Comes in with the results from
        pass n-2 and is updated with the results from the last pass, n-1,
        to inform on building the grids for the current pass, n. String
        params and bools are not in a continuous space and cannot be on
        the edges. Hard integers, hard floats, fixed integers, and fixed
        floats cannot "land on the edges". The only parameters that can
        land inside or on the edges are soft floats and soft integers.
        If on the edges, that parameter's grid is shifted, otherwise the
        search window is narrowed.
    _IS_LOGSPACE : IsLogspaceType
        For all numerical parameters, if the space is linear, or some
        other non-standard interval, it is False. If it is logspace, the
        'truth' of being a logspace is represented by a number indicating
        the interval of the logspace. E.g., np.logspace(-5, 5, 11) would
        be represented by 1.0, and np.logspace(-20, 20, 9) would be
        represented by 5.0.
    _best_params_from_previous_pass : BestParamsType
        `best_params_` returned by the parent Gridsearch on the previous
        pass.
    _pass : int
        Zero-indexed counter indicating the number of the current pass.
    _total_passes : int
        The number of `GridSearchCV` passes to perform.
    _total_passes_is_hard : bool
        If True, 'shift' rounds do not add another pass to total passes;
        if False, shift rounds add another round to total passes,
        preserving the number of rounds where soft search grids are
        narrowed.
    _shift_ctr : int
        Number of GridSearchCV passes where search grids have shifted.
    _max_shifts : int
        Maximum number of GridSearchCV passes allowed that only shift
        grids.

    Returns
    -------
    __ : tuple[GridsType, ParamsType, PhliteType, IsLogspaceType, int, int]
        _GRIDS : GridsType
            Search grids for completed GridSearchCV passes and the
            filled grid for the upcoming search.
        _params : ParamsType
            Full list of grid construction instructions for all params
            to be searched updated with any modifications made during
            build of the next search's grids (i.e., the current call
            to :func:`_get_next_param_grid`).
        _PHLITE : PhliteType (Param has landed inside the edges)
            `_PHLITE` updated with the results from the previous round.
        _IS_LOGSPACE : IsLogspaceType
            Updated for any parameters that may have converted from
            logspace to linspace on the last pass.
        _shift_ctr : int
            `_shift_ctr` incremented if the currently constructed grid
            requires a shift for the upcoming search.
        _total_passes : int
            The number of `GridSearchCV` passes to perform.
            Incremented by one if a shift is going to be performed and
            `total_passes_is_hard` is False.

    """

    # 0) validate!
    # 1) update PHLITE with results from last round
    # 2) if any Falses in PHLITE, shift those grids (dont return yet)
    # 3) look for params with True in PHLITE and value > 1.0 in
    #       _IS_LOGSPACE, if so, regap to 1.0 (return if regapped)
    # 4) if still shifting (False in PHLITE) and _shift_ctr < _max_shifts,
    #       return
    # 5) if all in PHLITE True, drill and return


    # * ** * ** * ** * ** * ** * ** ** ** * ** * ** * ** * ** * ** * **
    # _validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if _pass == 0:
        ValueError(f"accessing _get_next_param_grid on pass 0")

    # GRIDS
    # core GRIDS _validation
    _validate_grids(_GRIDS)

    # there must be at least one grid (_pass zero's) in _GRIDS; the last
    # round in _GRIDS must be full
    if len(_GRIDS) == 0 or len(_GRIDS[max(_GRIDS.keys())]) == 0:
        raise ValueError(
            f"an empty GRIDS has been passed to get_next_param_grid()"
        )

    if _pass - 1 not in _GRIDS:
        raise ValueError(
            f"attempting to operate on pass {_pass} when pass {_pass-1} "
            f"is not in GRIDS"
        )

    # _total_passes
    _val_total_passes(_total_passes)

    #     _params
    _val_params(_params, _total_passes)


    #     _PHLITE
    # core _PHLITE
    _validate_phlite(_PHLITE)
    # extra _PHLITE
    for _param in _params:
        if 'soft' in _params[_param][-1] and _param not in _PHLITE:
            raise ValueError(f"soft param '{_param}' not in PHLITE")

    #     _IS_LOGSPACE
    # core _IS_LOGSPACE _validation
    _validate_is_logspace(_IS_LOGSPACE, _params)

    # _best_params
    _validate_best_params( _GRIDS, _pass, _best_params_from_previous_pass)

    # _pass, _shift_ctr
    err_msg = lambda name: f"'{name}' must be an integer >= 0"
    for name, x in zip(['_pass', '_shift_ctr'], [_pass, _shift_ctr]):

        try:
            float(x)
        except:
            raise TypeError(err_msg(name))

        if int(x) != x:
            raise ValueError(err_msg(name))

    del err_msg

    # the rest
    _val_max_shifts(_max_shifts, _can_be_None=False)

    _val_total_passes_is_hard(_total_passes_is_hard)

    # END _validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # * ** * ** * ** * ** * ** * ** ** ** * ** * ** * ** * ** * ** * **


    _GRIDS[_pass] = dict()

    # must establish if a soft num param has fallen inside the edges of
    # its grid. string_parameters, bool_parameters, AND hard/fixed
    # numerical_parameters CANNOT BE "ON AN EDGE"!
    # this is not needed after the pass where all soft num fall inside
    # the edges (all values in PHLITE will be True and cannot gain
    # re-entry to the place where they could be set back to False.)
    # Update PHLITE with the results from the last pass to assess the
    # need for shifting. ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    if False in _PHLITE.values() and _shift_ctr <= _max_shifts:

        if _shift_ctr < _max_shifts:

            _PHLITE = _update_phlite(
                _PHLITE,
                _GRIDS[_pass-1],
                _params,
                _best_params_from_previous_pass
            )

        elif _shift_ctr == _max_shifts:
            _PHLITE = {k: True for k in _PHLITE}

    # END UPDATE PHLITE ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # After update to PHLITE, if any params are still landing on the edges
    # (False), must slide their grids and rerun all the other params with
    # their same grids.
    # not elif!
    if False in _PHLITE.values(): # _shift_ctr < _max_shifts

        _shift_ctr += 1

        if not _total_passes_is_hard:
            _total_passes += 1

        _GRIDS, _params = _shift(
            _GRIDS,
            _PHLITE,
            _IS_LOGSPACE,
            _params,
            _pass,
            _best_params_from_previous_pass,
            _total_passes_is_hard
        )

    # END SHIFT ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # not elif!
    if any((v > 1 and _PHLITE.get(k, True)) for k, v in _IS_LOGSPACE.items()):
        # must let 'fixed' and 'bool' in here also if they get a shrink

        # REGAP LOG > 1 ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # 24_05_20 _total_passes_is_hard should not matter here,
        # this is a "drill" that can happen concurrently with a "shift",
        # or could happen without a shift.

        # 24_05_27 _regap only overwrites impacted _params, does not touch
        # _params otherwise -- if _GRIDS is empty (because all values in
        # PHLITE are True and _shift() was not accessed) then those other
        # params wont be put in by _regap. must add those separately.
        if _GRIDS[_pass] == {}:

            _GRIDS[_pass] = deepcopy(_GRIDS[_pass - 1])

            # 24_05_27 this was not allowing access to shrink code if doing
            # a regap and a shrink is supposed to happen on the same pass.
            # doing shrink here is easier than making a regap pass bump
            # points like a shift.
            for _param in _GRIDS[_pass]:

                if _params[_param][1][_pass] == 1:
                    _GRIDS[_pass][_param] = \
                        [_best_params_from_previous_pass[_param]]
                    _IS_LOGSPACE[_param] = False # may have already been False

        for _param in _params:

            # 24_05_28 params with logspace already == 1 are not converted
            # to linspace, the log gap == 1 params (and all the other
            # non-logspace params) run the same thing again with the
            # log gap > 1 params regapped to 1

            # dont let fixed in here, not allowed to regap (thinking that
            # all fixed are always set to False in IS_LOGSPACE anyway)
            if _PHLITE.get(_param, True) and _IS_LOGSPACE[_param] > 1 and \
                'fixed' not in _params[_param][-1]:

                _grid, _param_value, _is_logspace = \
                    _regap_logspace(
                        _param,
                        _GRIDS[_pass - 1][_param],
                        _IS_LOGSPACE[_param],
                        _params[_param],
                        _pass,
                        _best_params_from_previous_pass[_param],
                        _GRIDS[0][_param][0],  # hard min
                        _GRIDS[0][_param][-1]  # hard max
                    )

                # update GRIDS for the current param & pass
                _GRIDS[_pass][_param] = _grid
                # OVERWRITE _IS_LOGSPACE WITH NEW GAP
                _IS_LOGSPACE[_param] = _is_logspace
                _params[_param] = _param_value

        try:
            del _grid, _param_value, _is_logspace
        except:
            pass

        # END REGAP LOG ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        return _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes

    elif False in _PHLITE.values(): # _shift_ctr < _max_shifts
        return _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes

    else:
        # all values in _PHLITE are True and no log gaps > 1.0
        pass

    # IF REACHED THIS POINT:
    # (i) EVERYTHING IN PARAM_HAS_LANDED_INSIDE_THE_EDGES IS True,
    # (ii) ANY LOGSPACES HAVE AN INTERVAL OF <= 1 AND WILL CONVERT TO
    #       LINSPACES


    if (np.fromiter(_IS_LOGSPACE.values(), dtype=float) > 1).any():
        ValueError(f"an integer logspace with log10 gap > 1 has made it "
                   f"into digging section")

    for _param in _params:

        if _param not in _GRIDS[max(_GRIDS.keys()) - 1]:
            raise ValueError(f"attempting to insert a param key that is "
                 f"not in GRIDS")

        _grid, _param_value, _is_logspace = _drill(
             _param,
             _GRIDS[_pass - 1][_param],
             _params[_param],
             _IS_LOGSPACE[_param],
             _pass,
             _best_params_from_previous_pass[_param]
        )

        _GRIDS[_pass][_param] = _grid
        _params[_param] = _param_value
        _IS_LOGSPACE[_param] = _is_logspace

        if 'fixed_string' not in _param_value[-1] \
                and 'fixed_bool' not in _param_value[-1]:
            _params[_param][-2][_pass] = len(_grid)

        del _grid, _param_value, _is_logspace

    del _param


    return _GRIDS, _params, _PHLITE, _IS_LOGSPACE, _shift_ctr, _total_passes





