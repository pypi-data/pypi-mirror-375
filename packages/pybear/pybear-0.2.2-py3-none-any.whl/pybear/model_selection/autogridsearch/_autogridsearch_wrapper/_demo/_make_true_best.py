# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    ParamsType,
    BestParamsType
)

import random

import numpy as np



def _make_true_best(
    _params: ParamsType
) -> BestParamsType:
    """Build a mock `best_params_` with realistic values based on the
    grid-building instructions in `_params`.

    Parameters
    ----------
    _params : ParamsType
        Grid-building instruction for all parameters

    Return
    ------
    _true_best_params : BestParamsType
        Mock best GridSearchCV results in format identical to sklearn
        GridSearchCV.best_params_

    """


    _true_best_params = dict()


    for _key, _param  in _params.items():

        _param_grid = _param[0]
        _type = _param[-1].lower()

        if 'fixed_bool' in _type or 'fixed_string' in _type:
            _best = random.choice(_param_grid)
        else:
            _min = min(_param_grid)
            _max = max(_param_grid)
            _gap = _max - _min
            if _type == 'hard_float':
                _best = int(np.random.uniform(_min, _max))
            elif _type == 'hard_integer':
                _best = int(np.random.randint(_min, _max + 1))
            elif _type in ['fixed_float', 'fixed_integer']:
                _best = int(random.choice(_param_grid))
            elif _type == 'soft_float':
                _best = int(np.random.uniform(
                    max(_min - _gap, 0),
                    _max + _gap
                ))
            elif _type == 'soft_integer':
                _best = int(np.random.randint(
                    max(_min - _gap, 1),
                    _max + _gap
                ))
            else:
                raise Exception

        _true_best_params[_key] = _best


    return _true_best_params








