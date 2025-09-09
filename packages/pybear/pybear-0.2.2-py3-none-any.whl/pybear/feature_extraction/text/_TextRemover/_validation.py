# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ._type_aliases import (
    XContainer,
    RemoveType,
    CaseSensitiveType,
    RemoveEmptyRowsType,
    FlagsType
)

from ..__shared._validation._1D_X import _val_1D_X
from ..__shared._validation._2D_X import _val_2D_X
from ..__shared._validation._any_bool import _val_any_bool
from ..__shared._validation._case_sensitive import _val_case_sensitive
from ..__shared._validation._flags import _val_flags
from ..__shared._validation._pattern_holder import _val_pattern_holder



def _validation(
    _X: XContainer,
    _remove: RemoveType,
    _case_sensitive: CaseSensitiveType,
    _remove_empty_rows: RemoveEmptyRowsType,
    _flags: FlagsType
) -> None:
    """Centralized hub for validation.

    See the individual modules for more details.

    Beyond the individual modules' validation, this module also checks:
    1) cannot pass anything to `flags` if `remove` is None
    2) cannot pass a list to `case_sensitive` if `remove` is None

    Parameters:
    -----------
    _X : XContainer
        The data. 1D or (possible ragged) 2D array of strings.
    _remove : RemoveType
        The string literals or re.compile patterns to look for and remove.
    _case_sensitive : CaseSensitiveType
        Whether to make searches for strings to remove case-sensitive.
    _remove_empty_rows : RemoveEmptyRowsType
        Whether to remove empty rows from 2D data. This does not apply
        to 1D data, by definition rows will always be removed from 1D
        data.
    _flags : FlagsType
        Externally provided flags if using re.compile objects.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]] | set[str]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[str] | list[list[str]]

    RemoveType:
        PatternType | list[PatternType]

    CaseSensitiveType:
        bool | list[bool | None]

    RemoveEmptyRowsType:
        bool

    FlagsType:
        FlagType | list[FlagType]

    """


    try:
        _val_2D_X(_X, _require_all_finite=False)
        raise UnicodeError
    except UnicodeError:
        # remove_empty_rows only applies to 2D data
        _val_any_bool(_remove_empty_rows, _name='remove_empty_rows')
    except Exception as e:
        try:
            _val_1D_X(_X, _require_all_finite=False)
        except Exception as f:
            raise TypeError(
                f"Expected X to be 1D sequence or (possibly ragged) 2D "
                f"array of string-like values."
            )


    _n_rows = _X.shape[0] if hasattr(_X, 'shape') else len(_X)

    _val_pattern_holder(_remove, _n_rows, 'remove')

    _val_case_sensitive(_case_sensitive, _n_rows)

    _val_flags(_flags, _n_rows)

    del _n_rows

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    #########
    if _remove is None and isinstance(_case_sensitive, list):
        raise ValueError(
            f"cannot pass 'case_sensitive' as a list if 'remove' is not "
            f"passed."
        )

    #########
    if _remove is None and _flags is not None:
        raise ValueError(f"cannot pass 'flags' if 'remove' is not passed.")






