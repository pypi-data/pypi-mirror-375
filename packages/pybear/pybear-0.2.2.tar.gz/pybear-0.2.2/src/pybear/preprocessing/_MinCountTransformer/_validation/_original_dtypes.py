# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import OriginalDtypesType

import numpy as np

from ...__shared._validation._any_integer import _val_any_integer



def _val_original_dtypes(
    _original_dtypes: OriginalDtypesType,
    _n_features_in: int
) -> None:
    """Validate that datatypes in the passed `_original_datatypes`
    container are valid MCT internal datatypes. Allowed values are
    'bin_int', 'int', 'float', and 'obj'. Entries are case-sensitive.
    Validate number of entries against the number of features in the
    data.

    Parameters
    ----------
    _original_dtypes : OriginalDtypesType
        The datatypes read from the data. must be a 1D list-like with
        values in 'bin_int', int', 'float', or 'obj'.
    _n_features_in : int
        The number of features in the data.

    Returns
    -------
    None

    """


    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    _allowed = ['bin_int', 'int', 'float', 'obj']

    _err_msg = (
        f"'_original_dtypes' must be a 1D vector of values in "
        f"{', '.join(_allowed)} \nand the number of entries must equal "
        f"the number of features in the data."
    )
    try:
        iter(_original_dtypes)
        if isinstance(_original_dtypes, (str, dict)):
            raise Exception
        if not len(np.array(list(_original_dtypes)).shape) == 1:
            raise Exception
        if not len(_original_dtypes) == _n_features_in:
            _addon = f""
            raise UnicodeError
        if not all(map(
            isinstance, _original_dtypes, (str for _ in _original_dtypes)
        )):
            raise Exception
        for i in _original_dtypes:
            if i not in _allowed:
                _addon = f" got '{i}'."
                raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg + _addon)
    except:
        raise TypeError(_err_msg)





