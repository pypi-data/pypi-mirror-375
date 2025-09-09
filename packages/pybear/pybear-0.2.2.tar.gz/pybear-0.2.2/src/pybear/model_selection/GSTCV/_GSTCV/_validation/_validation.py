# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)
from ..._type_aliases import ClassifierProtocol

from ._sk_estimator import _val_sk_estimator
from ._pre_dispatch import _val_pre_dispatch



def _validation(
    _estimator: ClassifierProtocol,
    _pre_dispatch: Literal['all'] | str | int
) -> None:
    """Centralized hub for sklearn GSTCV validation.

    See the submodules for more information.

    Parameters
    ----------
    _estimator : ClassifierProtocol
        The estimator to be validated.
    _pre_dispatch : Literal['all'] | str | int
        The number of batches (of tasks) to be pre-dispatched. See the
        joblib.Parallel docs for more information.

    Returns
    -------
    None

    """


    _val_sk_estimator(_estimator)

    _val_pre_dispatch(_pre_dispatch)






