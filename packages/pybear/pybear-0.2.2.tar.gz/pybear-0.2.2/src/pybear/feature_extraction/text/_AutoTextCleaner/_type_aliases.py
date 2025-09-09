# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Literal,
    Sequence,
    TypeAlias,
    TypedDict
)
from typing_extensions import (
    NotRequired,
    Required
)

import numpy.typing as npt

import re

import pandas as pd
import polars as pl



PythonTypes: TypeAlias = Sequence[str] | set[str] | Sequence[Sequence[str]]

NumpyTypes: TypeAlias = npt.NDArray[str]

PandasTypes: TypeAlias = pd.Series | pd.DataFrame

PolarsTypes: TypeAlias = pl.Series | pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

XWipContainer: TypeAlias = list[str] | list[list[str]]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

ReturnDimType: TypeAlias = Literal[1, 2] | None

FindType: TypeAlias = str | re.Pattern[str]
SubstituteType: TypeAlias = str | Callable[[str], str]
PairType: TypeAlias = tuple[FindType, SubstituteType]
ReplaceType: TypeAlias = PairType | tuple[PairType, ...] | None

RemoveType: TypeAlias = FindType | tuple[FindType, ...] | None

class LexiconLookupType(TypedDict):
    update_lexicon: NotRequired[bool]
    skip_numbers: NotRequired[bool]
    auto_split: NotRequired[bool]
    auto_add_to_lexicon: NotRequired[bool]
    auto_delete: NotRequired[bool]
    DELETE_ALWAYS: NotRequired[Sequence[str] | None]
    REPLACE_ALWAYS: NotRequired[dict[str, str] | None]
    SKIP_ALWAYS: NotRequired[Sequence[str] | None]
    SPLIT_ALWAYS: NotRequired[dict[str, Sequence[str]] | None]
    remove_empty_rows: NotRequired[bool]
    verbose: NotRequired[bool]

class NGramsType(TypedDict):
    ngrams: Required[Sequence[Sequence[FindType]]]
    wrap: Required[bool]

class GetStatisticsType(TypedDict):
    before: Required[bool | None]
    after: Required[bool | None]









