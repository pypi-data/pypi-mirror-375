# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    ContextManager,
    Iterable,
    Literal,
    Sequence,
    TypeAlias
)



PreDispatchType: TypeAlias = Literal['all'] | str | int

SKXType: TypeAlias = Iterable
SKYType: TypeAlias = Sequence[int] | None

SKSlicerType: TypeAlias = Sequence[int]

SKKFoldType: TypeAlias = tuple[SKSlicerType, SKSlicerType]

SKSplitType: TypeAlias = tuple[SKXType, SKYType]

SKSchedulerType: TypeAlias = ContextManager    # nullcontext




