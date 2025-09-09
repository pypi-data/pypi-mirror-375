# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence,
    TypeAlias
)



# see _type_aliases, str subtypes for DataType, GridType, PointsType, ParamType
StrDataType: TypeAlias = str | None  # DataType sub

InStrGridType: TypeAlias = Sequence[StrDataType]
StrGridType: TypeAlias = list[StrDataType] # GridType sub

InPointsType: TypeAlias = int | Sequence[int]
PointsType: TypeAlias = list[int]

StrTypeType: TypeAlias = Literal['fixed_string']

InStrParamType: TypeAlias = Sequence[tuple[InStrGridType, InPointsType, StrTypeType]]
StrParamType: TypeAlias = list[StrGridType, PointsType, StrTypeType] # ParamType sub






