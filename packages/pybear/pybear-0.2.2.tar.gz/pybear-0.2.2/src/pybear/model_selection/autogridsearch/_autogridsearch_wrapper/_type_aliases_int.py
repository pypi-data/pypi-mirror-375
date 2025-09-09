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



# see _type_aliases - int subtypes for DataType, GridType
IntDataType: TypeAlias = int

InIntGridType: TypeAlias = Sequence[IntDataType]
IntGridType: TypeAlias = list[IntDataType]

InPointsType: TypeAlias = int | Sequence[int]
PointsType: TypeAlias = list[int]

IntTypeType: TypeAlias = Literal['soft_integer', 'hard_integer', 'fixed_integer']

InIntParamType: TypeAlias = \
    Sequence[tuple[InIntGridType, InPointsType, IntTypeType]]
IntParamType: TypeAlias = list[IntGridType, PointsType, IntTypeType]








