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

import re

import pandas as pd
import polars as pl



PythonTypes: TypeAlias = Sequence[str] | Sequence[Sequence[str]] | set[str]

NumpyTypes: TypeAlias = npt.NDArray[str]

PandasTypes: TypeAlias = pd.Series | pd.DataFrame

PolarsTypes: TypeAlias = pl.Series | pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

XWipContainer: TypeAlias = list[str] | list[list[str]]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

PatternType: TypeAlias = \
    None | str | re.Pattern[str] | tuple[str | re.Pattern[str], ...]
RemoveType: TypeAlias = \
    PatternType | list[PatternType]

WipPatternType: TypeAlias = \
    None | re.Pattern[str] | tuple[re.Pattern[str], ...]
WipRemoveType: TypeAlias = \
    WipPatternType | list[WipPatternType]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

CaseSensitiveType: TypeAlias = bool | list[bool | None]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

RemoveEmptyRowsType: TypeAlias = bool

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

FlagType: TypeAlias = int | None
FlagsType: TypeAlias = FlagType | list[FlagType]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

RowSupportType: TypeAlias = npt.NDArray[bool]




