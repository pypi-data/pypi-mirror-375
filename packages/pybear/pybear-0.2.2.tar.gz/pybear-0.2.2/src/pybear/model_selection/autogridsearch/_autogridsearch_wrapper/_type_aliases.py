# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence,
    TypeAlias,
)
from ._type_aliases_float import (
    FloatDataType,
    InFloatGridType,
    FloatGridType,
    InFloatParamType,
    FloatParamType,
)
from ._type_aliases_int import (
    IntDataType,
    InIntGridType,
    IntGridType,
    InIntParamType,
    IntParamType
)
from ._type_aliases_str import (
    StrDataType,
    InStrGridType,
    StrGridType,
    InStrParamType,
    StrParamType
)
from ._type_aliases_bool import (
    BoolDataType,
    InBoolGridType,
    BoolGridType,
    InBoolParamType,
    BoolParamType
)



DataType: TypeAlias = BoolDataType | StrDataType | IntDataType | FloatDataType

InGridType: TypeAlias = \
    InBoolGridType | InStrGridType | InIntGridType | InFloatGridType
GridType: TypeAlias = BoolGridType | StrGridType | IntGridType | FloatGridType

InPointsType: TypeAlias = int | Sequence[int]
PointsType: TypeAlias = list[int]

InParamType: TypeAlias = \
    InBoolParamType | InStrParamType | InIntParamType | InFloatParamType
ParamType: TypeAlias = \
    BoolParamType | StrParamType | IntParamType | FloatParamType

InParamsType: TypeAlias = dict[
    str,
    InBoolParamType | InStrParamType | InIntParamType | InFloatParamType
]
ParamsType: TypeAlias = dict[
    str,
    BoolParamType | StrParamType | IntParamType | FloatParamType
]

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

LogspaceType: TypeAlias = Literal[False] | int
IsLogspaceType: TypeAlias = dict[str, LogspaceType]

PhliteType: TypeAlias = dict[str, bool]

ParamGridType: TypeAlias = dict[str, GridType]

GridsType: TypeAlias = dict[int, ParamGridType]

BestParamsType: TypeAlias = dict[str, DataType]

ResultsType: TypeAlias = dict[int, BestParamsType]






