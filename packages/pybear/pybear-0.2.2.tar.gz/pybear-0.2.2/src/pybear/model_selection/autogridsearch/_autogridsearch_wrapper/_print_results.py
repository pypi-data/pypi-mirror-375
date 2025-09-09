# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ._type_aliases import (
    GridsType,
    ResultsType
)


# no pytest, but there is a benchmarking sandbox


def _print_results(
    _GRIDS: GridsType,
    _RESULTS: ResultsType
) -> None:
    """Print the contents of `GRIDS_` and `RESULTS_`.

    `GRIDS_` are the search grids used for every pass of a real or demo
    agscv session. `RESULTS_` are the `best_params_` outputs for every
    pass of a real or demo agscv session.

    Parameters
    ----------
    _GRIDS : GridsType
        The grids used in each pass of a real or demo agscv session.
    _RESULTS : ResultsType
        The `best_params_` outputs for each pass of a real or demo agscv
        session.

    Returns
    -------
    None

    """


    for _pass in _RESULTS:
        print(f'Pass {_pass + 1} results:')
        for _param in _RESULTS[_pass]:
            _grid_pad = 80 - 15 - 10
            try:
                _grid = _GRIDS[_pass][_param]
                _grid = list(map(round, _grid, (3 for _ in _grid)))
                # try to round, if except, is str, handle in exception
                print(
                    f' ' * 5 + f'{_param}:'.ljust(15) +
                    f'{str(_grid)[:_grid_pad - 5]}'.ljust(_grid_pad) +
                    f'Result = {round(_RESULTS[_pass][_param], 3)}'
                )
            except:
                print(
                    f' ' * 5 + f'{_param}:'.ljust(15) +
                    f'{str(_GRIDS[_pass][_param])[:_grid_pad - 5]}'.ljust(_grid_pad) +
                    f'Result = {_RESULTS[_pass][_param]}'
                )
        print()





