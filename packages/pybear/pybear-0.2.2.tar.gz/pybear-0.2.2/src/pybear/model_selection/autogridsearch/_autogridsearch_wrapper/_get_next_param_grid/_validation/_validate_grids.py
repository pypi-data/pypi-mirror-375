# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import GridsType

import numbers



def _validate_grids(_GRIDS: GridsType) -> None:
    """Validate `_GRIDS` is dict[int, dict[str, GridType]].

    `_GRIDS` is the object in the main :func:`autogridsearch_wrapper`
    and :func:`get_next_param_grid` modules that holds all the search
    grids that have been run and the grid that is to be run.

    Parameters
    ----------
    _GRIDS : GridsType
        Search grids for completed GridSearchCV passes.

    Returns
    -------
    None

    """


    err_msg = f"_GRIDS must be a dict with int keys and dict values"
    if not isinstance(_GRIDS, dict):
        raise TypeError(err_msg)

    # all keys must be ints
    if any(map(isinstance, _GRIDS.keys(), (bool for _ in _GRIDS))):
        raise TypeError(err_msg)
    if not all(map(isinstance, _GRIDS.keys(), (numbers.Integral for _ in _GRIDS))):
        raise TypeError(err_msg)

    # all values must be dicts
    if not all(map(isinstance, _GRIDS.values(), (dict for _ in _GRIDS))):
        raise TypeError(err_msg)
    del err_msg


    err_msg = (f"_GRIDS values must be dicts with str keys and list values "
        f"holding ints, floats, bools, or strs")
    # all inner dicts keys must be strs
    for pass_idx in _GRIDS:

        __ = _GRIDS[pass_idx]

        if __ == {}:
            continue

        # all inner dicts keys must be str
        if not all(map(isinstance, __.keys(),  (str for _ in __))):
            raise TypeError(err_msg)

        # all inner dicts values must be lists
        if not all(map(isinstance, __.values(), (list for _ in __))):
            raise TypeError(err_msg)




