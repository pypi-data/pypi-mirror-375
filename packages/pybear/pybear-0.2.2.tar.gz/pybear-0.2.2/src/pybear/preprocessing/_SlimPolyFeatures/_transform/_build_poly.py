# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CombinationsType,
    InternalXContainer
)

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from .._partial_fit._columns_getter import _columns_getter



def _build_poly(
    _X: InternalXContainer,
    _active_combos: CombinationsType
) -> ss.csc_array:
    """Build the polynomial expansion for `_X` as a scipy sparse
    csc array using `_X` and `_active_combos`. `_X` is passed
    to :func:`_columns_getter` and must observe the restrictions
    imposed there. That is, `_X` can be np.ndarray, pd.DataFrame,
    pl.DataFrame, or scipy sparse csc matrix/array. `_X` should already
    be conditioned for this when passed here.

    `_active_combos` is all combinations from the original combinations
    that are not in `dropped_poly_duplicates_` or `poly_constants_`.

    Parameters
    ----------
    _X : InternalXContainer
        The data to undergo polynomial expansion.
    _active_combos : CombinationsType
        The index tuple combinations to be kept in the final polynomial
        expansion.

    Returns
    -------
    POLY : scipy sparse csc array of shape (n_samples, n_kept_polynomial_features)
        The polynomial expansion component of the final output.

    """


    # validation - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )

    assert isinstance(_active_combos, tuple)
    for _tuple in _active_combos:
        assert isinstance(_tuple, tuple)
        assert all(map(isinstance, _tuple, (int for _ in _tuple)))
    # END validation - - - - - - - - - - - - - - - - - - - - - - - - - -

    if not len(_active_combos):
        POLY = ss.csc_array(np.empty((_X.shape[0], 0), dtype=np.float64))
        return POLY

    POLY = ss.csc_array(np.empty((_X.shape[0], 0))).astype(np.float64)
    for combo in _active_combos:
        _poly_feature = _columns_getter(_X, combo).prod(1).reshape((-1, 1))
        POLY = ss.hstack((POLY, ss.csc_array(_poly_feature)))

    assert POLY.shape == (_X.shape[0], len(_active_combos))


    # LINUX TIME TRIALS INDICATE A REGULAR FOR LOOP IS ABOUT HALF THE
    # TIME OF JOBLIB
    # @wrap_non_picklable_objects
    # def _poly_stacker(_columns):
    #     return ss.csc_array(_columns.prod(1).reshape((-1,1)))
    # with joblib.parallel_config(
    #     prefer='processes', n_jobs=_n_jobs, backend='loky', max_nbytes="100M"
    # ):
    #     POLY = joblib.Parallel(return_as='list')(
    #         joblib.delayed(_poly_stacker)(
    #             _columns_getter(_X, combo)
    #         ) for combo in _active_combos
    #     )
    #
    # POLY = ss.hstack(POLY).astype(np.float64)
    # assert POLY.shape == (_X.shape[0], len(_active_combos))


    return POLY



