# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.preprocessing._InterceptManager._type_aliases import (
    KeepType,
    InstructionType,
    ConstantColumnsType
)

from pybear.preprocessing._InterceptManager._validation._instructions import (
    _val_instructions
)



def _make_instructions(
    _keep: KeepType,
    constant_columns_: ConstantColumnsType,
    _n_features_in: int
) -> InstructionType:
    """Based on the `keep` instructions provided, and the constant
    columns found during fitting, build a dictionary that gives explicit
    instructions about what constant columns to keep, delete, or add.
    `keep` must have been conditioned into dict[str, Any], int, or
    Literal['none'] before this module in :func:`_manage_keep`.


    The form of the dictionary is:
    {
        'keep': None | list[constant column indices to keep],
        'delete': None | list[constant column indices to delete],
        'add': None | dict['{new column name}', fill value]
    }

    if `keep` == 'none', keep none, add none, delete all.
    if `keep` == a dict, keep none, delete all, append fill value to data.
    if `keep` == int, keep that idx, delete the remaining constant columns.

    `keep` callable, str feature name, and the other str literals besides
    'none' should not get in here, should have been converted to int
    in :func:`_manage_keep`.

    The column that is to be built by 'add' is not added to `keep`.

    Parameters
    ----------
    _keep : int | Literal['none'] | dict[str, Any]]
        The strategy for handling the constant columns. See 'The keep
        Parameter' section for a lengthy explanation of the `keep`
        parameter.
    constant_columns_ : ConstantColumnsType
        Constant column indices and their values found in all partial
        fits.
    _n_features_in : int
        Number of features in the fitted data before transform.

    Returns
    -------
    _instructions : InstructionType
        Instructions for keeping, deleting, or adding constant columns
        to be applied during transform.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    err_msg = f"'_keep' must be Literal['none'], dict[str, Any], or int"
    try:
        iter(_keep)
        if not isinstance(_keep, (str, dict)):
            raise UnicodeError
        if isinstance(_keep, dict) and not isinstance(list(_keep)[0], str):
            raise UnicodeError
        if isinstance(_keep, str) and _keep != 'none':
            raise UnicodeError
    except UnicodeError:
        raise AssertionError(err_msg)
    except:
        try:
            float(_keep)
            if isinstance(_keep, bool):
                raise Exception
            if int(_keep) != _keep:
                raise Exception
            _keep = int(_keep)
        except Exception as e:
            raise AssertionError(err_msg)

    assert isinstance(_n_features_in, int)

    assert isinstance(constant_columns_, dict)
    if len(constant_columns_):
        assert all(map(
            isinstance, constant_columns_, (int for _ in constant_columns_)
        ))
        assert min(constant_columns_) >= 0
        assert max(constant_columns_) <= _n_features_in - 1
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _sorted_constant_column_idxs = sorted(list(constant_columns_))

    _instructions: InstructionType = {
        # dont really need 'keep' for operating on X, just makes it easy
        # to make the kept_columns_ instance attr later on.
        'keep': None,
        'delete': None,
        'add': None
    }


    # all of these operations in this if block are conditional on there
    # being at least one constant column
    if len(_sorted_constant_column_idxs) == 0:
        # if there are no constant columns, skip everything except keep
        # dict
        pass
    elif isinstance(_keep, int):
        _instructions['keep'] = [_keep]
        _sorted_constant_column_idxs.remove(_keep)
        _instructions['delete'] = _sorted_constant_column_idxs
    elif isinstance(_keep, str) and _keep != 'none':
        raise AssertionError(f"str 'keep' not 'none' has gotten into "
            f"_make_instructions but should already be an int")
    elif callable(_keep):
        raise AssertionError(f"callable 'keep' has gotten into "
            f"_make_instructions but should already be an int")
    elif _keep == 'none':
        # if keep == 'none', keep none, add none, delete all
        _instructions['delete'] = _sorted_constant_column_idxs

    # this must be separate from the above if block
    # this operation takes place whether or not there are constant columns
    if isinstance(_keep, dict):
        # if keep == a dict, keep none, delete all, add value in last
        # position
        if len(_sorted_constant_column_idxs):
            _instructions['delete'] = _sorted_constant_column_idxs
        # else:
        #     _instructions['delete'] stays None

        _instructions['add'] = _keep


    _val_instructions(_instructions, _n_features_in)

    return _instructions




