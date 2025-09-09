# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InstructionType,
    ConstantColumnsType,
    KeptColumnsType,
    RemovedColumnsType,
    ColumnMaskType
)

import numpy as np



def _set_attributes(
    constant_columns_: ConstantColumnsType,
    _instructions: InstructionType,
    _n_features_in: int
) -> tuple[KeptColumnsType, RemovedColumnsType, ColumnMaskType]:
    """Use the `constant_columns_` and `_instructions` attributes to
    build the `kept_columns_`, `removed_columns_`, and `column_mask_`
    attributes.

    Parameters
    ----------
    constant_columns_ : ConstantColumnsType
        Constant column indices and their values found in all partial
        fits.
    _instructions : InstructionType
        Instructions for keeping, deleting, or adding constant columns
        to be applied during transform.
    _n_features_in : int
        Number of features in the fitted data before transform.

    Returns
    -------
    _attributes : tuple[kept_columns_, removed_columns_, column_mask_]
        The populated attributes.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(constant_columns_, dict)
    assert all(map(isinstance, constant_columns_, (int for _ in constant_columns_)))
    assert np.all(np.fromiter(constant_columns_, dtype=int) >= 0)
    assert np.all(np.fromiter(constant_columns_, dtype=int) <= _n_features_in - 1)
    assert isinstance(_instructions, dict)
    assert len(_instructions) == 3
    assert all(_ in ('keep', 'delete', 'add') for _ in _instructions)
    assert isinstance(_instructions['keep'], (type(None), list))
    assert isinstance(_instructions['delete'], (type(None), list))
    _keep_idxs = set(_instructions['keep'] or [])
    _delete_idxs = set(_instructions['delete'] or [])
    assert len(_keep_idxs.intersection(_delete_idxs)) == 0, \
        f"column index in both 'keep' and 'delete'"
    del _keep_idxs, _delete_idxs
    assert isinstance(_instructions['add'], (type(None), dict))
    assert isinstance(_n_features_in, int)
    assert _n_features_in >= 0
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    kept_columns_: KeptColumnsType = {}
    removed_columns_: RemovedColumnsType = {}
    # set column_mask_ dtype to object to carry py bool, not np.bool_.
    # unfortunately, numpy will not allow py bools in an object array for
    # slicing! so live with the yucky np.True_ and np.False_ repr.
    column_mask_ = np.ones(_n_features_in).astype(bool)

    # all values in _instructions dict are None could only happen if there are
    # no constant columns, in which case this for loop wont be entered
    for col_idx, constant_value in constant_columns_.items():
        if col_idx in (_instructions['keep'] or []):
            kept_columns_[col_idx] = constant_value
        elif col_idx in (_instructions['delete'] or []):
            removed_columns_[col_idx] = constant_value
            column_mask_[col_idx] = False
        else:
            raise Exception(
                f"a constant column in constant_columns_ is unaccounted for "
                f"in _instructions."
                f"\n{constant_columns_=}"
                f"\n{_instructions['keep']=}"
                f"\n{_instructions['delete']=}"
                f"\n{_instructions['add']=}"
            )


    return kept_columns_, removed_columns_, column_mask_



