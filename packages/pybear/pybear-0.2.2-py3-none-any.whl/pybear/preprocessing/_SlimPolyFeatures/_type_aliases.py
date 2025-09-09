# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Callable,
    Literal,
    Sequence,
    TypeAlias
)
import numpy.typing as npt

import pandas as pd
import polars as pl
import scipy.sparse as ss



InternalXContainer: TypeAlias = (
    npt.NDArray | pd.DataFrame | pl.DataFrame
    | ss._csr.csr_matrix | ss._csc.csc_matrix | ss._lil.lil_matrix
    | ss._dok.dok_matrix | ss._csr.csr_array | ss._csc.csc_array
    | ss._lil.lil_array | ss._dok.dok_array
)

FeatureNameCombinerType: TypeAlias = (
    Callable[[Sequence[str], tuple[int, ...]], str]
    | Literal['as_feature_names', 'as_indices']
)

CombinationsType: TypeAlias = tuple[tuple[int, ...], ...]

PolyDuplicatesType: TypeAlias = list[list[tuple[int, ...]]]

KeptPolyDuplicatesType: TypeAlias = dict[tuple[int, ...], list[tuple[int, ...]]]

DroppedPolyDuplicatesType: TypeAlias = dict[tuple[int, ...], tuple[int, ...]]

PolyConstantsType: TypeAlias = dict[tuple[int, ...], Any]

FeatureNamesInType: TypeAlias = npt.NDArray[object]



