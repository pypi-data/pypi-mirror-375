# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    CountThresholdType,
    IgnoreColumnsType,
    HandleAsBoolType,
    FeatureNamesInType
)
from ...__shared._type_aliases import XContainer

import numbers

from ._feature_names_in import _val_feature_names_in
from ._count_threshold import _val_count_threshold
from ._ignore_columns_handle_as_bool import _val_ignore_columns_handle_as_bool

from ...__shared._validation._X import _val_X
from ...__shared._validation._any_bool import _val_any_bool
from ...__shared._validation._any_integer import _val_any_integer



def _validation(
    _X: XContainer,
    _count_threshold: CountThresholdType,
    _ignore_float_columns: bool,
    _ignore_non_binary_integer_columns: bool,
    _ignore_columns: IgnoreColumnsType,
    _ignore_nan: bool,
    _handle_as_bool: HandleAsBoolType,
    _delete_axis_0: bool,
    _reject_unseen_values: bool,
    _max_recursions: int,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType | None
) -> None:
    """Validate parameters for `MinCountTransformer`.

    This module is a centralized hub for parameter validation. See the
    individual modules for more details.

    Parameters
    ----------
    _X : XContainer
        The data.
    _count_threshold : CountThresholdType
        The minimum frequency threshold.
    _ignore_float_columns : bool
        Whether to ignore float columns.
    _ignore_non_binary_integer_columns : bool
        Whether to ignore non-binary integer columns.
    _ignore_columns : IgnoreColumnsType
        Columns to ignore.
    _ignore_nan : bool
        Whether to ignore nan values or treat them like any other
        discrete value.
    _handle_as_bool : HandleAsBoolType
        Columns to be handled as boolean.
    _delete_axis_0 : bool
        Whether to delete rows along the example axis for columns that
        are handled as boolean.
    _reject_unseen_values : bool
        Whether to reject values seen during transform that were not
        seen during fitting.
    _max_recursions : int
        The number of times to repeat the MCT algorithm on a single
        dataset.
    _n_features_in : int
        The number of features in the data.
    _feature_names_in : FeatureNamesInType | None
        The feature names seen at first fit if the data was passed in
        a container that has a header, like a pandas or polars dataframe.

    Returns
    -------
    None

    """


    _val_X(_X)

    _val_any_integer(_n_features_in, '_n_features_in', _min=1)
    if _n_features_in != _X.shape[1]:
        raise ValueError(f"n_features_in != _X.shape[1]")

    _val_feature_names_in(
        _feature_names_in,
        _n_features_in
    )

    _val_count_threshold(
        _count_threshold,
        ['int', 'Sequence[int]'],
        _n_features_in
    )

    _val_any_bool(
        _ignore_float_columns, 'ignore_float_columns', _can_be_None=False
    )

    _val_any_bool(
        _ignore_non_binary_integer_columns,
        'ignore_non_binary_integer_columns',
        _can_be_None=False
    )

    _val_ignore_columns_handle_as_bool(
        _ignore_columns,
        'ignore_columns',
        ['Sequence[str]', 'Sequence[int]', 'callable', 'None'],
        _n_features_in=_n_features_in,
        _feature_names_in=_feature_names_in
    )

    _val_any_bool(_ignore_nan, '_ignore_nan', _can_be_None=False)

    _val_any_bool(_delete_axis_0, '_delete_axis_0', _can_be_None=False)

    _val_ignore_columns_handle_as_bool(
        _handle_as_bool,
        'handle_as_bool',
        ['Sequence[str]', 'Sequence[int]', 'callable', 'None'],
        _n_features_in=_n_features_in,
        _feature_names_in=_feature_names_in
    )

    # dont validate the ignore_columns/hab callables here
    # we could validate
    # --returns list-like
    # --returns ints if no fni_
    # --returns ints or strs if fni_
    # --if str & fni_, has valid strs
    # --if int, is in range of columns
    # BUT WE CANT VALIDATE THE COLUMNS AGAINST original_dtypes
    # we can do all of them at once in partial_fit/transform once we know the dtypes

    _val_any_bool(
        _reject_unseen_values, '_reject_unseen_values', _can_be_None=False
    )

    # _val_any_integer allows lists
    if not isinstance(_max_recursions, numbers.Integral):
        raise TypeError(
            f"'max_recursions' must be an integer >= 1. Got {_max_recursions}."
        )
    _val_any_integer(_max_recursions, 'max_recursions', _min=1)




