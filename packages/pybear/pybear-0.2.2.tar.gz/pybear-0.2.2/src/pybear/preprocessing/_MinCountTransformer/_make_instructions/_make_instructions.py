# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CountThresholdType,
    InternalIgnoreColumnsType,
    InternalHandleAsBoolType,
    TotalCountsByColumnType,
    OriginalDtypesType,
    InstructionsType,
    FeatureNamesInType
)

from ._validation._make_instructions_validation import _make_instructions_validation
from ._validation._delete_instr import _val_delete_instr

from ._threshold_listifier import _threshold_listifier
from ._one_unique import _one_unique
from ._two_uniques_hab import _two_uniques_hab
from ._two_uniques_not_hab import _two_uniques_not_hab
from ._three_or_more_uniques_hab import _three_or_more_uniques_hab
from ._three_or_more_uniques_not_hab import _three_or_more_uniques_not_hab


# _make_instructions()
#   CALLED in MCT BY get_support(), print_instructions(), AND transform()
# get_support()
#   CALLED in MCT BY get_feature_names() AND transform()



def _make_instructions(
    _count_threshold: CountThresholdType,
    _ignore_float_columns: bool,
    _ignore_non_binary_integer_columns: bool,
    _ignore_columns: InternalIgnoreColumnsType,
    _ignore_nan: bool,
    _handle_as_bool: InternalHandleAsBoolType,
    _delete_axis_0: bool,
    _original_dtypes: OriginalDtypesType,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType | None,
    _total_counts_by_column: TotalCountsByColumnType
) -> InstructionsType:
    """
    Convert compiled uniques and frequencies in `_total_counts_by_column`
    that were found by MCT during fit into instructions for transforming
    data based on given parameters.

    `_delete_instr` is a dictionary that is keyed by column index
    and the values are lists. Within each list is information about
    operations to perform with respect to the values in the corresponding
    column. The following items may be in the list:

    -- 'INACTIVE' - Ignore the column and carry it through for all other
        operations
    -- Individual values (in raw datatype format, not converted to
        string) - Indicates to delete the rows on axis 0 that contain
        that value in that column, including nan-like values
    -- 'DELETE ALL' - Delete all values in the column along the 0 axis.
        This text string is substituted in if MCT finds that all unique
        values in the column are to be deleted. This saves memory over
        filling the instruction list with all the unique values,
        especially for float columns. This instruction in and of itself
        does not indicate to delete the entire column from axis 1.
    -- 'DELETE COLUMN' - perform any individual row deletions that need
        to take place while the column is still in the data, then delete
        the column from the data along axis 1.

    `_total_counts_by_column` is a dictionary that is keyed by column
    index and the values are dictionaries. Each inner dictionary is
    keyed by the uniques in that column and the values are the respective
    counts in that column. 'nan' are documented in these dictionaries,
    which complicates assessing if columns have 1, 2, or 3+ unique
    values. If `_ignore_nan`, nans and their counts are removed from the
    dictionaries and set aside while the remaining non-nan values are
    processed by `_make_instructions`.

    Instructions are made based on the counts found in all the training
    data seen up to the point of calling `_make_instructions`. Counts
    can be accreted incrementally, as with `partial_fit`, and then
    finally `_make_instructions` is run to create instructions based on
    the total counts. Because the instructions are agnostic to the
    origins of the data they were created from, the instructions can be
    applied to any data that matches the schema of the training data.
    This allows for transformation of unseen data.

    A) if col_idx is inactive, skip.
    column is 'INACTIVE' if:
       - col_idx in `_ignore_columns`
       - the minimum frequency threshold for the column is 1
       - _total_counts_by_column[col_idx] is empty
       - `_ignore_float_columns` and is float column
       - `_ignore_non_binary_integer_columns`, is 'int', and num unqs >= 3

    B) MANAGE nan
    Get nan information if nan is in _total_counts_by_column[col_idx]

        1) Create holder objects to hold the nan value and the count.
            - if ignoring nan, holder objects hold False
            - if not ignoring nan:
              -- 'nan' not in column, holder objects hold False
              -- 'nan' in column, holder objects hold the nan value and ct

        2) Temporarily remove nan from `_total_counts_by_column`, if
        ignoring or not

    C) Assess the remaining values and counts and create instructions.
    Now that nan is out of `_total_counts_by_column`, look at the number
    of items in uniques and direct based on if is 1, 2, or 3+, and if
    handling as boolean.

    There are 5 modules called by this module. All cases where there is
    only one unique in a feature are handled the same, by one module.
    Otherwise, the algorithms for handling as boolean and not handling
    as boolean are separate for the cases of 2 uniques or 3+ uniques.

    See the individual modules for detailed explanation of the logic.

    Parameters
    ----------
    _count_threshold : CountThresholdType
        The threshold that determines whether a value is removed from
        the data (frequency is below threshold) or retained (frequency
        is greater than or equal to threshold.)
    _ignore_float_columns : bool
        If True, values and frequencies within float features are ignored
        and instructions are not made for this feature. If False, the
        feature's unique values are subject to count threshold rules
        and possible removal.
    _ignore_non_binary_integer_columns : bool
        If True, values and frequencies within non-binary integer
        features are ignored and instructions are not made for this
        feature. If False, the feature's unique values are subject to
        count threshold rules and possible removal.
    _ignore_columns : InternalIgnoreColumnsType
        A one-dimensional vector of integer index positions. Excludes
        the indicated features when making instructions.
    _ignore_nan : bool
        If True, nan is ignored in all features and passes through the
        transform operation; it can only be removed collaterally by
        removal of examples for causes dictated by other features. If
        False, frequency for nan-like values are calculated and assessed
        against `count_threshold`.
    _handle_as_bool : InternalHandleAsBoolType
        A one-dimensional vector of integer index positions. For the
        indicated features, non-zero values within the feature are
        treated as if they are the same value.
    _delete_axis_0 : bool
        Only applies to binary integer features such as those generated
        by OneHotEncoder or features indicated in `handle_as_bool`.
        Under normal operation of MCT for datatypes other than binary
        integer, when the frequency of one of the values in the feature
        is below `count_threshold`, the respective examples are removed
        (the entire row is deleted from the data). However, MCT does not
        handle binary integers like this in that the rows with deficient
        frequency are not removed, only the entire column is removed.
        `delete_axis_0` overrides this behavior. When `delete_axis_0`
        is False under the above conditions, MCT does the default
        behavior for binary integers, the feature is removed without
        deleting examples, preserving the data in the other features. If
        `delete_axis_0` is True, however, the default behavior for other
        datatypes is used and the rows associated with the minority
        value are deleted from the data and the feature is then also
        removed for having only one value.
    _original_dtypes : OriginalDtypesType
        The original datatypes for each column in the dataset as
        determined by MCT. Values can be 'bin_int', 'int', 'float', or
        'obj'.
    _n_features_in : int
        The number of features (columns) in the dataset.
    _feature_names_in : FeatureNamesInType | None
        If the data container passed to the first fit had features names
        this is an ndarray of those feature names. Otherwise, this is
        None.
    _total_counts_by_column : dict[int, dict[DataType, int]]
        A zero-indexed dictionary that holds dictionaries containing the
        counts of the uniques in each column.

    Returns
    -------
    _delete_instr : InstructionsType
        A dictionary that is keyed by column index and the values are
        lists. Within the lists is information about operations to
        perform with respect to values in each column.

    """


    _make_instructions_validation(
        _count_threshold,
        _ignore_float_columns,
        _ignore_non_binary_integer_columns,
        _ignore_columns,
        _ignore_nan,
        _handle_as_bool,
        _delete_axis_0,
        _original_dtypes,
        _n_features_in,
        _feature_names_in,
        _total_counts_by_column,
    )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _threshold: list[int] = _threshold_listifier(
        _n_features_in,
        _count_threshold
    )


    _delete_instr = {}
    for col_idx, COLUMN_UNQ_CT_DICT in _total_counts_by_column.items():
        # _total_counts_by_column GIVES A DICT OF UNQ & CTS FOR COLUMN;
        # IF _ignore_nan, nans & THEIR CTS ARE TAKEN OUT BELOW. IF nan
        # IS IN, THIS COMPLICATES ASSESSMENT OF COLUMN HAS 1 VALUE, IS
        # BINARY, ETC.

        # find inactive columns
        # need to put something on every pass to keep asc order of keys
        if _threshold[col_idx] == 1:
            _delete_instr[col_idx] = ['INACTIVE']
        elif col_idx in _ignore_columns:
            _delete_instr[col_idx] = ['INACTIVE']
        elif COLUMN_UNQ_CT_DICT == {}:
            _delete_instr[col_idx] = ['INACTIVE']
        elif (_ignore_float_columns and _original_dtypes[col_idx] == 'float'):
            _delete_instr[col_idx] = ['INACTIVE']
        elif _ignore_non_binary_integer_columns and \
                _original_dtypes[col_idx] == 'int':
            _delete_instr[col_idx] = ['INACTIVE']
        elif _original_dtypes[col_idx] == 'obj' and col_idx in _handle_as_bool:
            raise ValueError(f"handle_as_bool on obj column")
        else:
            _delete_instr[col_idx] = []

        if _delete_instr[col_idx] == ['INACTIVE']:
            continue

        # vvv MANAGE nan ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # GET OUT nan INFORMATION IF nan IS IN
        if _ignore_nan:
            _nan_key = False
            _nan_ct = False
        else:
            _nan_dict = {k: v for k, v in COLUMN_UNQ_CT_DICT.items()
                         if str(k).lower() == 'nan'}
            if len(_nan_dict) == 0:
                _nan_key = False
                _nan_ct = False
            elif len(_nan_dict) == 1:
                _nan_key = list(_nan_dict.keys())[0]
                _nan_ct = list(_nan_dict.values())[0]
            else:
                raise AssertionError(f">=2 nans found in COLUMN_UNQ_CT_DICT")

            del _nan_dict

        # TEMPORARILY REMOVE nan FROM COLUMN_UNQ_CT_DICT, WHETHER IGNORING OR NOT
        COLUMN_UNQ_CT_DICT = {unq: ct for unq, ct in COLUMN_UNQ_CT_DICT.items()
                              if str(unq).lower() != 'nan'}
        # ^^^ END MANAGE nan ** * ** * ** * ** * ** * ** * ** * ** * **

        # populate _delete_instr

        if len(COLUMN_UNQ_CT_DICT) == 0:
            # if COLUMN_UNQ_CT_DICT is empty here, it is because it was
            # a column of all nans. just delete the column without
            # deleting rows, it is a column of constants, and that is
            # what _one_unique does.
            _delete_instr[col_idx] = ['DELETE COLUMN']

        elif len(COLUMN_UNQ_CT_DICT) == 1:
            # SAME VALUE IN THE WHOLE COLUMN, MAYBE WITH SOME nans

            _delete_instr[col_idx] = _one_unique(
                _threshold[col_idx],
                _nan_key,
                _nan_ct,
                COLUMN_UNQ_CT_DICT
            )

        elif len(COLUMN_UNQ_CT_DICT) == 2:

            if col_idx in _handle_as_bool or _original_dtypes[col_idx] == 'bin_int':
                # _two_uniques_hab blocks str
                # when a solid block of non-zero ints/floats, column is deleted
                _delete_instr[col_idx] = _two_uniques_hab(
                    _threshold[col_idx],
                    _nan_key,
                    _nan_ct,
                    COLUMN_UNQ_CT_DICT,
                    _delete_axis_0
                )
            else:
                _delete_instr[col_idx] = _two_uniques_not_hab(
                    _threshold[col_idx],
                    _nan_key,
                    _nan_ct,
                    COLUMN_UNQ_CT_DICT
                )

        else:  # 3+ UNIQUES NOT INCLUDING nan

            if col_idx in _handle_as_bool:
                # when a solid block of non-zero ints/floats, column is deleted
                _delete_instr[col_idx] = _three_or_more_uniques_hab(
                    _threshold[col_idx],
                    _nan_key,
                    _nan_ct,
                    COLUMN_UNQ_CT_DICT,
                    _delete_axis_0
                )
            else:
                _delete_instr[col_idx] = _three_or_more_uniques_not_hab(
                    _threshold[col_idx],
                    _nan_key,
                    _nan_ct,
                    COLUMN_UNQ_CT_DICT
                )

    del _threshold, col_idx, COLUMN_UNQ_CT_DICT
    try:
        del _nan_key, _nan_ct, _nan_dict
    except:
        pass

    _val_delete_instr(_delete_instr, _n_features_in)


    return _delete_instr




