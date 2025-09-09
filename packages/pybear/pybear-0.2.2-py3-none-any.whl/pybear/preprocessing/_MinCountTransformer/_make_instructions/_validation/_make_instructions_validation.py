# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import (
    CountThresholdType,
    InternalHandleAsBoolType,
    InternalIgnoreColumnsType,
    OriginalDtypesType,
    TotalCountsByColumnType,
    FeatureNamesInType
)

from ..._validation._count_threshold import _val_count_threshold
from ..._validation._ignore_columns_handle_as_bool import \
    _val_ignore_columns_handle_as_bool
from ..._validation._original_dtypes import _val_original_dtypes
from ._total_counts_by_column import _val_total_counts_by_column
from ..._validation._feature_names_in import _val_feature_names_in

from ....__shared._validation._any_bool import _val_any_bool
from ....__shared._validation._any_integer import _val_any_integer



def _make_instructions_validation(
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
) -> None:
    """Validate all parameters taken in by `_make_instructions`.

    This is a centralized hub for validation, see the individual modules
    for more details.

    Parameters
    ----------
    _count_threshold : int | Sequence[int]
        Minimum frequency threshold.
    _ignore_float_columns : bool
        Whether to ignore float columns.
    _ignore_non_binary_integer_columns : bool
        Whehter to ignore non-binary integer columns.
    _ignore_columns : npt.NDArray[np.int32]
        The indices of columns to ignore.
    _ignore_nan : bool
        Whether to ignore nans.
    _handle_as_bool : npt.NDArray[np.int32]
        The indices of columns to handle as boolean.
    _delete_axis_0 : bool
        Whether to delete rows along the example axis for columns that
        are handled as boolean.
    _original_dtypes : OriginalDtypesType
        The internal dtypes to assigned to each feature by MCT.
    _n_features_in : int
        The numbers of features in the fitted data.
    _feature_names_in : FeatureNamesInType | None
        The feature names seen at first fit if the data was passed in a
        container that has a headers, such as pandas or polars dataframes.
    _total_counts_by_column : TotalCountsByColumnType
        A dictionary holding the uniques and their frequences for every
        column in the data.

    Return
    ------
    None

    """


    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    _val_feature_names_in(
        _feature_names_in,
        _n_features_in
    )

    _val_count_threshold(
        _count_threshold,
        ['int', 'Sequence[int]'],
        _n_features_in
    )

    _val_any_bool(_ignore_float_columns, 'ignore_float_columns', _can_be_None=False)

    _val_any_bool(
        _ignore_non_binary_integer_columns, 'ignore_non_binary_integer_columns',
        _can_be_None=False
    )

    _val_ignore_columns_handle_as_bool(
        _ignore_columns,
        'ignore_columns',
        ['Sequence[int]'],
        _n_features_in=_n_features_in,
        _feature_names_in=_feature_names_in
    )

    _val_any_bool(_ignore_nan, 'ignore_nan', _can_be_None=False)

    _val_original_dtypes(
        _original_dtypes,
        _n_features_in
    )

    _val_ignore_columns_handle_as_bool(
        _handle_as_bool,
        'handle_as_bool',
        ['Sequence[int]'],
        _n_features_in=_n_features_in,
        _feature_names_in=_feature_names_in
    )

    _val_any_bool(_delete_axis_0, 'delete_axis_0', _can_be_None=False)

    _val_total_counts_by_column(_total_counts_by_column)




