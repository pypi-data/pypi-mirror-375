# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    ParamsType,
    BestParamsType
)


# benchmark tests only

def _display_true_best(
    _demo_cls_params: ParamsType,
    _true_best: BestParamsType
) -> None:
    """Display the best values in `_true_best` for reference against the
    best values being returned by `AutoGridSearch`.

    Parameters
    ----------
    _demo_cls_params : ParamsType
        Full set of grid-building instructions for all parameters.
    _true_best : BestParamsType
        True best values for estimator's hyperparameters, as provided by
        the user or generated randomly.

    Returns
    -------
    None

    """


    _TYPES = {'string': [], 'bool': [], 'num':[]}
    for _ in _true_best:
        _type = _demo_cls_params[_][-1]
        if 'fixed_string' in _type:
            _TYPES['string'].append(_)
        elif 'fixed_bool' in _type:
            _TYPES['bool'].append(_)
        else:
            _TYPES['num'].append(_)


    _pad = min(max(map(len, _true_best)), 65)
    _print = lambda x: print(f'{x[:_pad]}:'.ljust(_pad + 5) + f'{_true_best[x]}')
    print(f'Numerical hyperparameters:')
    for x in _TYPES['num']:
        _print(x)
    print(f'\nString hyperparameters:')
    for y in _TYPES['string']:
        _print(y)
    print(f'\nBoolean hyperparameters:')
    for z in _TYPES['bool']:
        _print(z)
    print()


    del _TYPES, _pad, _print






