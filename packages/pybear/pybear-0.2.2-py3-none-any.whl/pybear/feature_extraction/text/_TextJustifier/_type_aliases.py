# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias
)
import numpy.typing as npt

import numbers
import re

import pandas as pd
import polars as pl



PythonTypes: TypeAlias = Sequence[str] | Sequence[Sequence[str]] | set[str]

NumpyTypes: TypeAlias = npt.NDArray

PandasTypes: TypeAlias = pd.Series | pd.DataFrame

PolarsTypes: TypeAlias = pl.Series | pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

XWipContainer: TypeAlias = list[str] | list[list[str]]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

NCharsType: TypeAlias = int

CoreSepBreakType: TypeAlias = \
    str | Sequence[str] | re.Pattern[str] | Sequence[re.Pattern[str]]

SepType: TypeAlias = CoreSepBreakType

LineBreakType: TypeAlias = CoreSepBreakType | None

CoreSepBreakWipType: TypeAlias = re.Pattern[str] | tuple[re.Pattern[str], ...]

SepWipType: TypeAlias = CoreSepBreakWipType

LineBreakWipType: TypeAlias = CoreSepBreakWipType | None

CaseSensitiveType: TypeAlias = bool

SepFlagsType: TypeAlias = int | None

LineBreakFlagsType: TypeAlias = int | None

BackfillSepType: TypeAlias = str

Join2DType: TypeAlias = str








