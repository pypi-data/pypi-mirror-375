# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ...._type_aliases import (
    MaskedHolderType
)

import numpy as np



def _val_f_t_s(
    _TEST_FOLD_x_THRESH_x_SCORER: MaskedHolderType,
    _name: str,
    _n_splits: int,
    _n_thresh: int,
    _n_scorers: int
) -> None:
    """Validate the dimensions of _TEST_FOLD_x_THRESH_x_SCORER, either
    the score holder or the time holder.

    Parameters
    ----------
    _TEST_FOLD_x_THRESH_x_SCORER : MaskedHolderType
        The raw scores from _parallelized_scorer.
    _name : str
        Which object is being validated.
    _n_splits : int
        The number of folds.
    _n_thresh : int
        The number of thresholds.
    _n_scorers : int
        The number of scorers.

    Returns
    -------
    None

    """


    _TFTS = _TEST_FOLD_x_THRESH_x_SCORER

    if not isinstance(_TFTS, np.ma.masked_array):
        raise TypeError(f"expected np masked array, got {type(_TFTS)}")

    if len(_TFTS.shape) != 3:
        raise ValueError(f"expected 3D, got {len(_TFTS.shape)}")

    if not _TFTS.dtype == np.float64:
        raise TypeError(f"expected float dtype")

    _exp_shape = (_n_splits, _n_thresh, _n_scorers)
    _act_shape = _TFTS.shape

    if _act_shape != _exp_shape:
        raise ValueError(
            f"{_name} is misshapen. \nwas expecting {_exp_shape}, "
            f"got {_act_shape}."
        )


    del _TFTS, _exp_shape, _act_shape






