# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)

import numbers



def _val_error_score(
    _error_score: Literal['raise'] | numbers.Real
) -> None:
    """Validate that `error_score` is a non-boolean numeric value or
    literal 'raise'.

    Parameters
    ----------
    _error_score : Literal['raise'] | numbers.Real
        Score to assign if an error occurs in estimator fitting.

    Returns
    -------
    None

    """


    _err_msg = (
        f"'error_score' must be 1) literal string 'raise', or 2) any "
        f"non-boolean number-like including np.nan"
    )


    if isinstance(_error_score, str):
        if _error_score != 'raise':
            raise ValueError(_err_msg)
        return


    try:
        float(_error_score)
        if isinstance(_error_score, bool):
            raise Exception
    except:
        raise TypeError(_err_msg)


    del _err_msg








