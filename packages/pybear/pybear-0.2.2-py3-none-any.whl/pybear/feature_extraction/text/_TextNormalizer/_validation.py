# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ._type_aliases import (
    XContainer,
    UpperType
)

from ..__shared._validation._1D_2D_X import _val_1D_2D_X
from ..__shared._validation._any_bool import _val_any_bool



def _validation(
    _X: XContainer,
    _upper: UpperType
) -> None:
    """Centralized hub for validation.

    See the individual modules for more details.

    Parameters:
    -----------
    _X : XContainer
        The data.
    _upper : UpperType
        If True, covert all text to upper-case; if False, convert all
        text to lower-case; if None, do a no-op.

    Return
    ------
    None

    Notes
    -----

    **Type Aliases**

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    UpperType:
        bool | None

    """


    _val_1D_2D_X(_X, _require_all_finite=False)

    _val_any_bool(_upper, _name='upper', _can_be_None=True)






