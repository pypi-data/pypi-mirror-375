# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import OriginalDtypesType

import numpy as np

from .._validation._original_dtypes import _val_original_dtypes

from ...__shared._validation._any_integer import _val_any_integer



def _original_dtypes_merger(
    _col_dtypes: OriginalDtypesType,
    _previous_col_dtypes: OriginalDtypesType | None,
    _n_features_in: int
) -> OriginalDtypesType:
    """Merge the datatypes found for the current partial fit with the
    datatypes seen in previous partial fits.

    Prior to the existence of this module, MCT would raise if datatypes
    in the current partial fit did not match those from previous partial
    fits.

    If `_previous_col_dtypes` is not None, check its dtypes against the
    dtypes in the currently passed data, use the hierarchy to set the
    merged dtype.

    --'obj' trumps everything, anything that was not 'obj' but is now
    'obj' becomes 'obj'

    --'float' trumps 'bin_int' and 'int'

    --'int' trumps 'bin_int'

    --anything that matches stays the same

    Parameters
    ----------
    _col_dtypes : OriginalDtypesType
        The datatypes found by MCT in the data for the current partial
        fit.
    _previous_col_dtypes : OriginalDtypesType | None
        The datatypes found by MCT in data seen in previous partial fits.
    _n_features_in : int
        The number of features in the data.

    Returns
    -------
    _merged_col_dtypes : OriginalDtypesType
        The datatypes merged based on the hierarchy.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    if _previous_col_dtypes is not None:
        _val_original_dtypes(_previous_col_dtypes, _n_features_in)

    _val_original_dtypes(_col_dtypes, _n_features_in)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if _previous_col_dtypes is None:
        return np.array(list(_col_dtypes))


    # if partial_fit has already seen data previously...

    _new_dtypes = []
    for _idx in range(len(_col_dtypes)):

        _current_dtype = _col_dtypes[_idx].lower()
        _old_dtype = _previous_col_dtypes[_idx].lower()

        if _current_dtype == 'obj' or _old_dtype == 'obj':
            _new = 'obj'
        elif _current_dtype == 'float' or _old_dtype == 'float':
            _new = 'float'
        elif _current_dtype == 'int' or _old_dtype == 'int':
            _new = 'int'
        else:
            _new = 'bin_int'

        _new_dtypes.append(_new)

    del _current_dtype, _old_dtype, _new


    return np.array(_new_dtypes)




