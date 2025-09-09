# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    GridsType,
    ParamsType,
    BestParamsType
)

import numbers
import time

import numpy as np



def _mock_gscv(
    _GRIDS: GridsType,
    _params: ParamsType,
    _true_best: BestParamsType,
    _best_params: BestParamsType | None,
    _pass: int,
    *,
    _pause_time: numbers.Real = 5
) -> BestParamsType:
    """Simulate the behavior of `GridSearchCV`.

    Take a short pause to identify the best parameters in a grid based
    on the underlying true best value. For a string parameter, make it
    10% chance that the returned "best" is non-best option (simulate a
    discrete parameter moving around while the other parameters hone in
    on their true best.) For numerical, use min lsq to find the closest
    grid value.

    Parameters
    ----------
    _GRIDS : GridsType
        Full set of search grids for every parameter in every pass.
    _params : ParamsType
        Full set of grid-building instructions.
    _true_best : BestParamsType
        The "true best" value for every parameter as entered by the user
        or generated randomly
    _best_params : BestParamsType | None
        Best results from the previous GridSearch pass. None if on the
        first pass (pass 0).
    _pass : int
        The zero-indexed count of GridSearches performed.
    _pause_time : numbers.Real
        Seconds to pause to simulate work by GridSearchCV.

    Returns
    -------
    _best_params_ : BestParamsType
        The values in each search grid closest to the true best value.

    """


    err_msg = f"_pause_time must be a number >= 0"
    try:
        float(_pause_time)
        if not _pause_time >= 0:
            raise ValueError
    except ValueError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)


    # display info about parameters ** * ** * ** * ** * ** * ** * ** *
    def padder(words):
        _pad = 11
        try:
            return str(words)[:_pad].ljust(_pad+3)
        except:
            return 'NA'

    # build data header
    print(
        padder('param'),
        padder('type'),
        padder('true_best'),
        padder('prev_best'),
        padder('new_points'),
        padder('next_grid')
    )

    # fill data below header
    for _param in _GRIDS[_pass]:

        print(
            padder(_param),
            padder(_params[_param][-1]),
            padder(_true_best[_param]),
            padder('NA' if _pass == 0 else _best_params[_param]),
            padder(len(_GRIDS[_pass][_param])),
            end=' '  # to allow add on for grids below
        )

        _grid = _GRIDS[_pass][_param]
        try:
            # dont format this!
            print(f'{list(map(round, _grid, (3 for i in _grid)))}')
        except:
            print(f'{_grid}')  # dont format this!
        del _grid

    del padder
    # END display info about parameters ** * ** * ** * ** * ** * ** * **


    # SIMULATE WORK BY GridSearchCV ON AN ESTIMATOR ** * ** * ** * ** *
    combinations = np.prod(list(map(len, _GRIDS[_pass].values())))
    print(f'\nThere are {combinations:,.0f} combinations to run')
    print(f"Simulating GridSearchCV running on pass {_pass + 1}...")
    time.sleep(float(_pause_time))
    del combinations


    # CALCULATE WHAT THE best_params_ SHOULD BE BASED ON THE true_best_params.
    _best_params_ = dict()
    for _param in _GRIDS[_pass]:
        _grid = _GRIDS[_pass][_param]
        if len(_grid) == 1:
            _best_params_[_param] = _grid[0]
        elif _params[_param][-1] in ['fixed_string', 'fixed_bool']:
            # for a str or bool param, make it 10% chance that the returned
            # "best" is non-best option
            _p_best = 0.9
            _p_not_best = (1 - _p_best) / (len(_grid) - 1)
            _p = [0.9 if i == _true_best[_param] else _p_not_best for i in _grid]

            _best_params_[_param] = type(_grid[0])(np.random.choice(_grid, p=_p))
            del _p_best, _p_not_best, _p
        else:
            # use min lsq to find best for numerical
            # dont let best value get out of here as an np float or int!
            _LSQ = np.power(
                np.array(_grid) - _true_best[_param],
                2,
                dtype=np.float64
            )
            _best_idx = np.arange(len(_grid))[_LSQ == np.min(_LSQ)][0]
            _best_params_[_param] = _grid[_best_idx]
            del _LSQ, _best_idx

        del _grid
    # END SIMULATE WORK BY GridSearchCV ON AN ESTIMATOR ** * ** * ** *


    return _best_params_









