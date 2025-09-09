# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import PhliteType



def _validate_phlite(
    _PHLITE: PhliteType
) -> None:
    """Validate `_PHLITE` is dict[str, bool].

    Parameters
    ----------
    _PHLITE : PhliteType (param has landed inside the edges)
        Boolean indicating if a parameter has or has not landed off
        the extremes of its last search grid. String params are not in
        a continuous space and cannot be on the edges. Hard integers,
        hard floats, fixed integers, and fixed floats cannot "land on
        the edges". The only parameters that can land inside or on the
        edges are soft floats and soft integers. If on the edges, that
        parameter's grid is shifted, otherwise the search window is
        narrowed.

    """


    err_msg = f"_PHLITE must be a dict with str keys and bool values"

    if not isinstance(_PHLITE, dict):
        raise TypeError(err_msg)

    if not all(map(isinstance, _PHLITE.keys(), (str for _ in _PHLITE))):
        raise TypeError(err_msg)

    if not all(map(isinstance, _PHLITE.values(), (bool for _ in _PHLITE))):
        raise TypeError(err_msg)

    del err_msg







