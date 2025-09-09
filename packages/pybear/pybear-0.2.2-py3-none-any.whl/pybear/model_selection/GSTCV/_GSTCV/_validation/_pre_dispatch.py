# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from typing import (
    Literal,
)



def _val_pre_dispatch(
    _pre_dispatch:Literal['all'] | str | int
) -> None:
    """Validate `_pre_dispatch`.

    This file is a placeholder. There is no validation here, any errors
    would be raised by joblib.Parallel().

    Parameters
    ----------
    _pre_dispatch : Literal['all'] | str | int
        The number of batches (of tasks) to be pre-dispatched. See the
        joblib.Parallel docs for more information.

    Returns
    -------
    None

    """


    return









