# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Sequence,
    TypeAlias,
)
import numpy.typing as npt

import re

import pandas as pd
import polars as pl



PythonTypes: TypeAlias = Sequence[Sequence[str]]

NumpyTypes: TypeAlias = npt.NDArray[str]

PandasTypes: TypeAlias = pd.DataFrame

PolarsTypes: TypeAlias = pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

XWipContainer: TypeAlias = list[list[str]]

NGramsType: TypeAlias = \
    Sequence[Sequence[str | re.Pattern[str]]] | None

NGramsWipType: TypeAlias = list[tuple[re.Pattern[str], ...]] | None

NGCallableType: TypeAlias = Callable[[list[str]], str] | None

SepType: TypeAlias = str | None

WrapType: TypeAlias = bool

CaseSensitiveType: TypeAlias = bool

RemoveEmptyRowsType: TypeAlias = bool

FlagsType: TypeAlias = int | None







