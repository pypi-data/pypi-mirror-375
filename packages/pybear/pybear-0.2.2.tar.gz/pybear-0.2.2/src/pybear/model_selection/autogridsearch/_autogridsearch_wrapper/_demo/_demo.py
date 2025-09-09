# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import BestParamsType

import numbers

from ._make_true_best import _make_true_best
from ._validate_true_best import _validate_true_best
from ._display_true_best import  _display_true_best
from ._mock_gscv import _mock_gscv
from .._get_next_param_grid._get_next_param_grid import _get_next_param_grid
from .._build_first_grid_from_params import _build
from .._print_results import _print_results
from .._build_is_logspace import _build_is_logspace



def _demo(
    _DemoCls,
    _true_best: BestParamsType | None = None,
    _mock_gscv_pause_time: numbers.Real = 5
):
    """Simulated trials of this `AutoGridSearch` instance.

    Assess AutoGridSearch's ability to generate appropriate grids with
    the given parameters (`params`) against mocked true best values.
    Visually inspect the generated grids and performance of the
    `AutoGridSearch` instance in converging to the mock targets provided
    in `_true_best`. If no true best values are provided via `_true_best`,
    random true best values are generated from the set of first search
    grids provided in `params`.

    Parameters
    ----------
    _DemoCls : object
        Instance of `AutoGridSearch` created for demo purposes, not
        "self".
    _true_best : BestParamsType | None, default=None
        Dictionary of mocked true best values for an estimator's
        hyperparameters,  as provided by the user. If not passed, random
        true best values are generated based on the first round grids
        made from the instructions in `params`.
    _mock_gscv_pause_time : numbers.Real, default=5
        Time in seconds to pause, simulating work being done by the
        parent GridSearch.

    Returns
    -------
    _DemoCls: object
        The AutoGridSearch instance created to run simulations, not
        "self". This return is integral for testing demo functionality,
        but has no other internal use.

    """


    try:
        float(_mock_gscv_pause_time)
        if _mock_gscv_pause_time < 0:
            raise Exception
    except:
        raise ValueError(
            f"'_mock_gscv_pause_time' must be a non-negative number"
        )


    _IS_LOGSPACE = _build_is_logspace(_DemoCls.params)


    # STUFF FOR MIMICKING GridSearchCV.best_params_ ** * ** * ** * ** *
    if _true_best is None:
        _true_best = _make_true_best(_DemoCls.params)

    _validate_true_best(_DemoCls.params, _IS_LOGSPACE, _true_best)

    _true_best_header = f'\nTrue best params'
    print(_true_best_header)
    print(f'-' * len(_true_best_header))
    _display_true_best(_DemoCls.params, _true_best)
    # END STUFF FOR MIMICKING GridSearchCV.best_params_ ** * ** * ** *


    # MIMIC GridSearchCV.fit() FLOW AND OUTPUT
    # fit():
    #     1) run passes of GridSearchCV
    #       - 1a) get_next_param_grid()
    #       - 1b) fit GridSearchCV with next_param_grid
    #       - 1c) update self.RESULTS

    # 1) run passes of GridSearchCV
    _PHLITE = {}
    for hprmtr in _DemoCls.params:
        if 'soft' in _DemoCls.params[hprmtr][-1].lower():
            _PHLITE[hprmtr] = False
    _RESULTS = dict()
    _pass = 0
    while _pass < _DemoCls.total_passes:

        print(f"\nStart pass {_pass + 1} " + f"** * " * 15)

        # short-circuiting around fit() in _DemoCls because estimator
        # must be circumvented. Other functionality in fit() (like build
        # param_grids and update RESULTS) must be replicated separately.


        # 1a) get_next_param_grid()
        print(f'Building param grid... ', end='')
        if _pass == 0:
            _DemoCls._GRIDS = _build(_DemoCls.params)
            # points must match what is in params
        else:

            _DemoCls._GRIDS, _DemoCls.params, _DemoCls._PHLITE, \
            _DemoCls._IS_LOGSPACE, _DemoCls._shift_ctr, _DemoCls.total_passes = \
                _get_next_param_grid(
                    _DemoCls._GRIDS,
                    _DemoCls.params,
                    getattr(_DemoCls, '_PHLITE', _PHLITE),
                    getattr(_DemoCls, '_IS_LOGSPACE', _IS_LOGSPACE),
                    _RESULTS[_pass-1],
                    _pass,
                    _DemoCls.total_passes,
                    _DemoCls.total_passes_is_hard,
                    getattr(_DemoCls, '_shift_ctr', 0),
                    _DemoCls.max_shifts
                )


            # update params with possibly different points from gnpg
            for _param in _DemoCls._GRIDS[_pass]:
                _DemoCls.params[_param][1][_pass] = \
                    len(_DemoCls._GRIDS[_pass][_param])

        print(f'Done.')


        # 1b) fit GridSearchCV with next_param_grid
        _RESULTS[_pass] = _mock_gscv(
            _DemoCls.GRIDS_,
            _DemoCls.params,
            _true_best,
            None if _pass == 0 else _RESULTS[_pass - 1],
            _pass,
            _pause_time=_mock_gscv_pause_time
        )

        print(f"End pass {_pass + 1}   " + f"** * " * 15)

        _pass += 1


    # 1c) update self.RESULTS - this must be set to the DemoCls attribute
    # so that DemoCls knows how to build the next param grid
    _DemoCls._RESULTS = _RESULTS

    del _RESULTS, _pass


    print(f'\nRESULTS:')
    print(f'-'*len(f'\nRESULTS:'))
    _print_results(_DemoCls.GRIDS_, _DemoCls.RESULTS_)


    # DISPLAY THE GENERATED true_best_params AGAIN #####################
    print(_true_best_header)
    print(f'-' * len(_true_best_header))
    _display_true_best(_DemoCls.params, _true_best)
    del _true_best_header
    # END DISPLAY THE GENERATED true_best_params AGAIN #################


    print(f"demo fit successfully completed {_DemoCls.total_passes} pass(es) "
          f"with {_DemoCls._shift_ctr} shift pass(es).")


    return _DemoCls   # for test purposes only







