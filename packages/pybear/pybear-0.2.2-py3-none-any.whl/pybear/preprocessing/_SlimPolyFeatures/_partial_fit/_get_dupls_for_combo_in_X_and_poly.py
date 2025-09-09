# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import InternalXContainer

import itertools
import math
import numbers

import joblib
import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from .._partial_fit._parallel_chunk_comparer import _parallel_chunk_comparer
from .._partial_fit._columns_getter import _columns_getter



def _get_dupls_for_combo_in_X_and_poly(
    _X: InternalXContainer,
    _poly_combos: list[tuple[int, ...]],
    _min_degree: int,
    _equal_nan: bool,
    _rtol: numbers.Real,
    _atol: numbers.Real,
    _n_jobs: int | None,
    _job_size: int
) -> list[tuple[tuple[int,...], tuple[int, ...]]]:
    """Scan the polynomial columns generated as products of combinations
    of columns from X across X itself and themselves, looking for
    duplicates.

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_features)
        The data to undergo polynomial expansion. `_X` will be passed
        to :func:`_columns_getter` which allows ndarray, pd.DataFrame,
        pl.DataFrame, scipy sparse csr matrix/array. `_X` should already
        be conditioned for this when passed here.
    _poly_combos : list[tuple[int, ...]]
        The combinations of columns from `_X` to use to build the
        polynomial columns.
    _min_degree : int
        The minimum degree of polynomial terms to return in the output.
    _equal_nan : bool
        How to handle nan-like values when checking for equality. See
        the detailed explanation in the SPF main module.
    _rtol : numbers.Real
        The relative difference tolerance for equality. See numpy.allclose.
    _atol : numbers.Real
        The absolute tolerance parameter for equality. See numpy.allclose.
    _n_jobs : int | None
        The number of joblib Parallel jobs to use when looking for
        duplicate columns.
    _job_size : int
        The number of columns to send to a joblib job. Must be an integer
        greater than or equal to 2.

    Returns
    -------
    _all_dupls : list[tuple[tuple[int,...], tuple[int, ...]]]
        1D list of tuples, each tuple holding two groups of indices.
        Each group of indices indicate column indices from `_X` that
        produce a duplicate column.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
        ss.csc_matrix)
    )
    assert _X.shape[1] >= 1   # must always have 1 or more features

    try:
        list(iter(_poly_combos))
        assert all(map(isinstance, _poly_combos, (tuple for i in _poly_combos)))
    except Exception as e:
        raise AssertionError

    assert isinstance(_equal_nan, bool)

    assert isinstance(_rtol, numbers.Real)
    assert not isinstance(_rtol, bool)
    assert _rtol >= 0
    assert isinstance(_atol, numbers.Real)
    assert not isinstance(_atol, bool)
    assert _atol >= 0

    assert isinstance(_n_jobs, (numbers.Integral, type(None)))
    assert not isinstance(_n_jobs, bool)
    assert _n_jobs is None or (_n_jobs >= -1 and _n_jobs != 0)

    assert isinstance(_job_size, numbers.Integral)
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _job_size = int(_job_size)

    args = {'_rtol': _rtol, '_atol': _atol, '_equal_nan': _equal_nan}


    # convert combos to np for slicing out poly combos
    _wip_poly_combos = np.array(list(map(tuple, _poly_combos)), dtype=object)

    # look for duplicates in X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
    # there can be more than one hit for duplicates in X in one partial fit

    _X_dupls = []
    if _min_degree == 1:

        # get the indices for scanning X ahead of time -- -- -- -- -- --
        # this just makes the scanning code less messy
        _n_X_batches = math.ceil(_X.shape[1] / _job_size)
        _n_poly_batches = math.ceil(len(_wip_poly_combos) / _job_size)
        _X_batches: list[tuple[tuple[int, ...], ...]] = []
        _poly_batches: list[tuple[tuple[int, ...], ...]] = []

        # X & poly are asymmetrics, cannot use itertools
        for i in range(0, _n_X_batches):   # _X chunks
            for j in range(i, _n_poly_batches):   # _combos chunks

                _X_low = i * _job_size
                _X_high = min((i + 1) * _job_size, _X.shape[1])
                _X_batches.append(tuple((k,) for k in range(_X_low, _X_high)))

                _poly_low = j * _job_size
                _poly_high = min((j + 1) * _job_size, len(_wip_poly_combos))
                # notice that the batch idxs are slicing _wip_poly_combos
                # whereas the X batch idxs directly slice the col idxs of X
                _poly_batches.append(
                    tuple(list(map(
                        tuple,
                        _wip_poly_combos[list(range(_poly_low, _poly_high))]
                    )))
                )

        del _n_X_batches, _n_poly_batches, _X_low, _X_high, _poly_low, _poly_high
        # END get indices for jobs -- -- -- -- -- -- -- -- -- -- -- --


        if _X.shape[1] < 2 * _job_size:
            for _X_idxs, _poly_idxs in zip(_X_batches, _poly_batches):

                _X_dupls.append(
                    _parallel_chunk_comparer(
                        _chunk1=_columns_getter(_X, _X_idxs),
                        _chunk1_X_indices=_X_idxs,
                        _chunk2=_columns_getter(_X, _poly_idxs),
                        _chunk2_X_indices=_poly_idxs,
                        **args
                    )
                )
        else:
            with joblib.parallel_config(
                prefer='processes', n_jobs=_n_jobs, backend='loky', max_nbytes="100M"
            ):
                _X_dupls = joblib.Parallel(return_as='list')(
                    joblib.delayed(_parallel_chunk_comparer)(
                        _chunk1=_columns_getter(_X, _X_idxs),
                        _chunk1_X_indices=_X_idxs,
                        _chunk2=_columns_getter(_X, _poly_idxs),
                        _chunk2_X_indices=_poly_idxs,
                        **args
                    ) for _X_idxs, _poly_idxs in zip(_X_batches, _poly_batches)
                )

        del _X_batches, _poly_batches

        _X_dupls = list(itertools.chain(*_X_dupls))

    else:
        # poly combos are not scanned against X if min_degree > 1
        _X_dupls = []

    # END look for duplicates in X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v



    # look for duplicates in POLY v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # get the indices for scanning poly ahead of time -- -- -- -- -- --
    # this just makes the scanning code less messy
    _n_poly_batches = math.ceil(len(_wip_poly_combos) / _job_size)
    _poly1_batches: list[tuple[tuple[int, ...], ...]] = []
    _poly2_batches: list[tuple[tuple[int, ...], ...]] = []

    for m, n in itertools.combinations_with_replacement(
        list(range(_n_poly_batches)), 2
    ):

        _poly1_low = m * _job_size
        _poly1_high = min((m + 1) * _job_size, len(_wip_poly_combos))
        _poly1_batches.append(
            tuple(map(
                tuple, _wip_poly_combos[list(range(_poly1_low, _poly1_high))]
            ))
        )

        _poly2_low = n * _job_size
        _poly2_high = min((n + 1) * _job_size, len(_wip_poly_combos))
        _poly2_batches.append(
            tuple(map(
                tuple, _wip_poly_combos[list(range(_poly2_low, _poly2_high))]
            ))
        )

    del _n_poly_batches, _poly1_low, _poly1_high, _poly2_low, _poly2_high
    # END get indices for jobs -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _poly_dupls = []
    if len(_wip_poly_combos) < 2 * _job_size:
        for _poly1_idxs, _poly2_idxs in zip(_poly1_batches, _poly2_batches):
            _poly_dupls.append(_parallel_chunk_comparer(
                _chunk1=_columns_getter(_X, _poly1_idxs),
                _chunk1_X_indices=_poly1_idxs,
                _chunk2=_columns_getter(_X, _poly2_idxs),
                _chunk2_X_indices=_poly2_idxs,
                **args
                )
            )
    else:
        with joblib.parallel_config(
            prefer='processes', n_jobs=_n_jobs, backend='loky', max_nbytes="100M"
        ):
            _poly_dupls = joblib.Parallel(return_as='list')(
                joblib.delayed(_parallel_chunk_comparer)(
                    _chunk1=_columns_getter(_X, _poly1_idxs),
                    _chunk1_X_indices=_poly1_idxs,
                    _chunk2=_columns_getter(_X, _poly2_idxs),
                    _chunk2_X_indices=_poly2_idxs,
                    **args
                ) for _poly1_idxs, _poly2_idxs in zip(_poly1_batches, _poly2_batches)
            )

    del _poly1_batches, _poly2_batches

    _poly_dupls = list(itertools.chain(*_poly_dupls))

    # END look for duplicates in POLY v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^


    _all_dupls = _X_dupls + _poly_dupls


    return _all_dupls




