# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias,
    TypedDict
)
from typing_extensions import Required
import numpy.typing as npt

import numbers

import pandas as pd
import polars as pl



class OverallStatisticsType(TypedDict):

    size: Required[int]
    uniques_count: Required[int]
    average_length: Required[numbers.Real]
    std_length: Required[numbers.Real]
    max_length: Required[int]
    min_length: Required[int]



PythonTypes: TypeAlias = Sequence[str] | Sequence[Sequence[str]] | set[str]

NumpyTypes: TypeAlias = npt.NDArray[str]

PandasTypes: TypeAlias = pd.Series | pd.DataFrame

PolarsTypes: TypeAlias = pl.Series | pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes






