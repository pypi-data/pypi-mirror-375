# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ...._type_aliases import (
    MaskedHolderType
)

import numpy as np



def _val_f_s(
    _FOLD_x_SCORER: MaskedHolderType,
    _name: str,
    _n_splits: int,
    _n_scorers: int
) -> None:
    """Validate the dimensions of _FOLD_x_SCORER, either the score holder
    or the time holder.

    Parameters
    ----------
    _FOLD_x_SCORER : MaskedHolderType
        The raw scores from :func:`_parallelized_scorer`.
    _name : str
        Which object is being validated.
    _n_splits : int
        The number of folds.
    _n_scorers : int
        The number of scorers.

    Returns
    -------
    None

    """

    _TFS = _FOLD_x_SCORER

    if not isinstance(_TFS, np.ma.masked_array):
        raise TypeError(f"expected np masked array, got {type(_TFS)}")

    if len(_TFS.shape) != 2:
        raise ValueError(f"expected 2D, got {len(_TFS.shape)}")

    if not _TFS.dtype == np.float64:
        raise TypeError(f"expected float dtype")

    _exp_shape = (_n_splits, _n_scorers)
    _act_shape = _TFS.shape

    if _act_shape != _exp_shape:
        raise ValueError(
            f"{_name} is misshapen. \nwas expecting {_exp_shape}, "
            f"got {_act_shape}."
        )


    del _TFS, _exp_shape, _act_shape






