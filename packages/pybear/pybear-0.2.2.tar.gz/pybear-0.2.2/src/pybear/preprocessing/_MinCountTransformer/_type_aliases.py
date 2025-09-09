# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Literal,
    Sequence,
    TypeAlias
)
import numpy.typing as npt
from ..__shared._type_aliases import XContainer

import numbers

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss



# see __shared XContainer

InternalXContainer: TypeAlias = \
    npt.NDArray | pd.DataFrame | pl.DataFrame | ss.csc_array | ss.csc_matrix

YContainer: TypeAlias = \
    npt.NDArray | pd.DataFrame | pd.Series | pl.DataFrame | pl.Series | None

DataType:TypeAlias = numbers.Number | str

CountThresholdType: TypeAlias = int | Sequence[int]

OriginalDtypesType: TypeAlias = \
    npt.NDArray[Literal['bin_int', 'int', 'float', 'obj']]

TotalCountsByColumnType: TypeAlias = dict[int, dict[DataType, int]]

InstrLiterals: TypeAlias = Literal['INACTIVE', 'DELETE ALL', 'DELETE COLUMN']

InstructionsType: TypeAlias = dict[int, list[DataType | InstrLiterals]]

IcHabCallable: TypeAlias = \
    Callable[[XContainer], Sequence[int] | Sequence[str]]

IgnoreColumnsType: TypeAlias = \
    None | Sequence[int] | Sequence[str] | IcHabCallable

HandleAsBoolType: TypeAlias = \
    None | Sequence[int] | Sequence[str] | IcHabCallable

InternalIgnoreColumnsType: TypeAlias = npt.NDArray[np.int32]

InternalHandleAsBoolType: TypeAlias = npt.NDArray[np.int32]

FeatureNamesInType: TypeAlias = npt.NDArray[object]





