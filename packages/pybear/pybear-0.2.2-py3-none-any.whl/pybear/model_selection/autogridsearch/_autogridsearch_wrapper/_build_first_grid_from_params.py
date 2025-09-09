# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ._type_aliases import ParamsType, GridsType



def _build(_params: ParamsType) -> GridsType:
    """Initialize `GRIDS` by filling the first round of grids based on
    the information provided in `params`.

    This is only for the first pass, and no other. After that, `GRIDS`
    are built by :func:`_get_next_param_grid`.

    Parameters
    ----------
    _params : ParamsType
        The `params` passed to agscv after conditioning.

    Returns
    -------
    GRIDS : GridsType
        The GRIDS attribute filled for the first round.

    """


    return {0: {k: v[0] for k, v in _params.items()}}







