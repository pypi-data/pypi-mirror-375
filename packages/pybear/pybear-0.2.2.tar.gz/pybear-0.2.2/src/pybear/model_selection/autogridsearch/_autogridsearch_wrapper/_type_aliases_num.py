# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias,
    TypeVar
)
from ._type_aliases_float import (
    FloatDataType,
    InFloatGridType,
    FloatGridType,
    FloatTypeType
)
from ._type_aliases_int import (
    IntDataType,
    InIntGridType,
    IntGridType,
    IntTypeType
)



# see _type_aliases, general num subtypes of DataType, GridType, PointsType, ParamType
NumDataType = TypeVar('NumDataType', IntDataType, FloatDataType)

InNumGridType: TypeAlias = InIntGridType | InFloatGridType
NumGridType: TypeAlias = IntGridType | FloatGridType

InPointsType: TypeAlias = int | Sequence[int]
PointsType: TypeAlias = list[int]

NumTypeType: TypeAlias = IntTypeType | FloatTypeType

InNumParamType: TypeAlias = Sequence[tuple[InNumGridType, InPointsType, NumTypeType]]
NumParamType: TypeAlias = list[NumGridType, PointsType, NumTypeType]





