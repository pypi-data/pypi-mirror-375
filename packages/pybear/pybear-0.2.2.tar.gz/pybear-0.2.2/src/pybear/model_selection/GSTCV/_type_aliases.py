# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    Protocol,
    Sequence,
    TypeAlias,
    TypedDict
)
from typing_extensions import (
    NotRequired,
    Self
)
import numpy.typing as npt

import numbers

import numpy as np



class ClassifierProtocol(Protocol):

    def fit(self, X: Any, y: Any) -> Self:
        ...

    # The default 'score' method of the estimator can never be used, as
    # the decision threshold cannot be manipulated. Therefore, it is not
    # necessary for the estimator to have a 'score' method.
    # def score(self, y_pred: Any, y_act: Any) -> Any:
    #     ...

    def get_params(self, **kwargs) -> dict[str, Any]:
        ...

    def set_params(self, **kwargs) -> Self:
        ...

    def predict_proba(self, X: Any) -> Any:
        ...


ParamGridInputType: TypeAlias = dict[str, Sequence[Any]]
ParamGridsInputType: TypeAlias = Sequence[ParamGridInputType]
ParamGridWIPType: TypeAlias = dict[str, list[Any]]
ParamGridsWIPType: TypeAlias = list[ParamGridWIPType]

ThresholdsInputType: TypeAlias = None | numbers.Real | Sequence[numbers.Real]
ThresholdsWIPType: TypeAlias = list[float]

GenericSlicerType: TypeAlias = Sequence[int]

GenericKFoldType: TypeAlias = tuple[GenericSlicerType, GenericSlicerType]

# scoring / scorer ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
ScorerNameTypes: TypeAlias = Literal[
    'accuracy',
    'balanced_accuracy',
    'average_precision',
    'f1',
    'precision',
    'recall'
]


ScorerCallableType: TypeAlias = Callable[[Iterable, Iterable], numbers.Real]


ScorerInputType: TypeAlias = (
    ScorerNameTypes |  Sequence[ScorerNameTypes] | ScorerCallableType
    | dict[str, ScorerCallableType]
)


class ScorerWIPType(TypedDict):

    accuracy: NotRequired[ScorerCallableType]
    balanced_accuracy: NotRequired[ScorerCallableType]
    average_precision: NotRequired[ScorerCallableType]
    f1: NotRequired[ScorerCallableType]
    precision: NotRequired[ScorerCallableType]
    recall: NotRequired[ScorerCallableType]
    score: NotRequired[ScorerCallableType]

# END scoring / scorer ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *


CVResultsType: TypeAlias = dict[str, np.ma.masked_array[Any]]


RefitCallableType: TypeAlias = Callable[[CVResultsType], int]
RefitType: TypeAlias = bool | ScorerNameTypes | RefitCallableType


MaskedHolderType: TypeAlias = np.ma.masked_array[float]
NDArrayHolderType: TypeAlias = npt.NDArray[numbers.Real]


FeatureNamesInType: TypeAlias = npt.NDArray[str]


ErrorScoreType: TypeAlias = numbers.Real | Literal['raise']




