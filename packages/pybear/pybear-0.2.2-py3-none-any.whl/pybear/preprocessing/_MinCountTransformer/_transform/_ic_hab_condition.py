# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    IgnoreColumnsType,
    HandleAsBoolType,
    InternalIgnoreColumnsType,
    InternalHandleAsBoolType,
    OriginalDtypesType,
    CountThresholdType,
    FeatureNamesInType
)
from ...__shared._type_aliases import XContainer

import warnings
from copy import deepcopy

import numpy as np

from ....utilities._feature_name_mapper import feature_name_mapper

from .._validation._ign_cols_hab_callable import _val_ign_cols_hab_callable
from .._validation._ignore_columns_handle_as_bool import \
    _val_ignore_columns_handle_as_bool
from .._validation._original_dtypes import _val_original_dtypes
from .._validation._count_threshold import _val_count_threshold
from .._validation._feature_names_in import _val_feature_names_in

from ...__shared._validation._any_integer import _val_any_integer



def _ic_hab_condition(
    X: XContainer | None,  # can be None when called from print_instructions
    _ignore_columns: IgnoreColumnsType,
    _handle_as_bool: HandleAsBoolType,
    _ignore_float_columns: bool,
    _ignore_non_binary_integer_columns: bool,
    _original_dtypes: OriginalDtypesType,
    _threshold: CountThresholdType,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType | None,
    _raise: bool = False
) -> tuple[InternalIgnoreColumnsType, InternalHandleAsBoolType]:
    """Receive `ignore_columns` and `handle_as_bool` as callable(X),
    Sequence[str], Sequence[int], or None, and convert to Sequence[int]
    with all non-negative indices.

    Perform any validation that can be done against `n_features_in_` and
    `feature_names_in_`, if passed. This module is essentially a hub
    that centralizes calling any callables and validating, converting
    any None values to an empty ndarray, and converting any string
    values to indices.

    if `ignore_columns` and `handle_as_bool` were originally passed to
    MCT as Sequence[int] or Sequence[str], the dimensions of them or the
    feature names in them would have been validated in _validation >
    _val_ignore_columns_handle_as_bool. Here is where values passed as
    feature names are finally mapped to indices.

    Determine if there is any intersection between columns to be handled
    as bool and any of the ignored columns. There is a hierarchy of
    what takes precedence, ignored columns always supersede handling as
    boolean. If `handle_as_bool` is None or an empty list, bypass all of
    this.

    Validate that the columns to be handled as boolean are numeric
    columns (MCT internal dtypes 'bin_int', 'int', 'float'). MCT internal
    dtype 'obj' columns cannot be handled as boolean, and this module
    will raise if it finds this condition and `_raise` is True.
    If `_raise` is False, it will warn. If an 'obj' column that is in
    `_handle_as_bool` is also in `_ignore_columns`, `_ignore_columns`
    supercedes `_handle_as_bool` and the column is ignored.

    Parameters
    ----------
    X : XContainer | None, array-like of shape (n_samples, n_features)
        The data to undergo minimum frequency thresholding.
    _ignore_columns : IgnoreColumnsType
        The columns to be ignored during the transform process.
    _handle_as_bool : HandleAsBoolType
        The columns to be handled as boolean during the transform
        process. i.e., all zero values are handled as False and all
        non-zero values are handled as True. MCT internal datatype 'obj'
        columns cannot be handled as boolean.
    _ignore_float_columns : bool
        Whether to exclude float columns from the thresholding rules
        during the transform operation.
    _ignore_non_binary_integer_columns : bool
        Whether to exclude non-binary integer columns from the
        thresholding rules during the transform operation.
    _original_dtypes : OriginalDtypesType
        The datatypes for each column in the dataset as determined by
        MCT. Values can be 'bin_int', 'int', 'float', or 'obj'.
    _threshold : CountThresholdType
        The minimum frequency threshold(s) to be applied to the columns
        of the data. Setting a threshold to 1 is the same as ignoring a
        column.
    _n_features_in : int
        The number of features in the data.
    _feature_names_in : FeatureNamesInType | None
        If the data was passed in a container that had a valid header,
        then a list-like of the feature names. otherwise, None.
    _raise : bool
        If True, raise a ValueError if any handle-as-bool columns
        are 'obj' dtype; if False, emit a warning.

    Returns
    -------
    __ : tuple[InternalIgnoreColumnsType, InternalHandleAsBoolType]
        `ignore_columns` and `handle_as_bool` in Sequence[int] form. All
        indices are >= 0.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    _val_feature_names_in(_feature_names_in, _n_features_in)

    _val_ignore_columns_handle_as_bool(
        _ignore_columns,
        'ignore_columns',
        ['callable', 'Sequence[str]', 'Sequence[int]', 'None'],
        _n_features_in,
        _feature_names_in
    )

    _val_ignore_columns_handle_as_bool(
        _handle_as_bool,
        'handle_as_bool',
        ['callable', 'Sequence[str]', 'Sequence[int]', 'None'],
        _n_features_in,
        _feature_names_in
    )

    assert isinstance(_ignore_float_columns, bool)

    assert isinstance(_ignore_non_binary_integer_columns, bool)

    _val_original_dtypes(_original_dtypes, _n_features_in)

    _val_count_threshold(
        _threshold,
        ['int', 'Sequence[int]'],
        _n_features_in
    )

    if not isinstance(_raise, bool):
        raise TypeError("'_raise' must be boolean")

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # ignore_columns  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if callable(_ignore_columns):

        try:
            __ignore_columns = _ignore_columns(X)
        except Exception as e:
            raise Exception(
                f"ignore_columns callable excepted with {type(e)} error"
            ) from e

        _val_ign_cols_hab_callable(
            __ignore_columns,
            None,
            'ignore_columns',
            _n_features_in,
            _feature_names_in
        )
    elif _ignore_columns is None:
        __ignore_columns = np.array([], dtype=np.int32)
    else:
        __ignore_columns = deepcopy(_ignore_columns)

    # feature_name_mapper can only map indices to positive if it is passed
    # _feature_names_in. we still want to map indices to positive numbers.
    # so spoof _feature_names_in if it is None.
    __ignore_columns: InternalIgnoreColumnsType = \
        feature_name_mapper(
            __ignore_columns,
            _feature_names_in if _feature_names_in is not None \
                else [str(i) for i in range(_n_features_in)],
            positive=True
        )
    # END ignore_columns  -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # handle_as_bool  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if callable(_handle_as_bool):

        try:
            __handle_as_bool = _handle_as_bool(X)
        except Exception as e:
            raise Exception(
                f"handle_as_bool callable excepted with {type(e)} error"
            ) from e

        _val_ign_cols_hab_callable(
            __handle_as_bool,
            None,
            'handle_as_bool',
            _n_features_in,
            _feature_names_in
        )
    elif _handle_as_bool is None:
        __handle_as_bool = np.array([], dtype=np.int32)
    else:
        __handle_as_bool = deepcopy(_handle_as_bool)

    # feature_name_mapper can only map indices to positive if it is
    # passed _feature_names_in. we still want to map indices to positive
    # numbers. so spoof _feature_names_in if it is None.
    __handle_as_bool: InternalIgnoreColumnsType = \
        feature_name_mapper(
            __handle_as_bool,
            _feature_names_in if _feature_names_in is not None \
                else [str(i) for i in range(_n_features_in)],
            positive=True
        )
    # END handle_as_bool  -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # secondary validation ensure Sequence[int] ** * ** * ** * ** * ** *
    _val_ignore_columns_handle_as_bool(
        __ignore_columns,
        'ignore_columns',
        ['Sequence[int]'],
        _n_features_in=_n_features_in,
        _feature_names_in=None
    )

    _val_ignore_columns_handle_as_bool(
        __handle_as_bool,
        'handle_as_bool',
        ['Sequence[int]'],
        _n_features_in=_n_features_in,
        _feature_names_in=None
    )

    # END secondary validation ensure Sequence[int] ** * ** * ** * ** *


    if len(__handle_as_bool) == 0:
        return __ignore_columns, __handle_as_bool


    # if intersection between ignore_float_columns and ignore_columns,
    # doesnt matter, ignored either way

    # if intersection between ignore_non_binary_integer_columns and
    # ignore_columns, doesnt matter, ignored either way

    # so we need to address when handle_as_bool intersects ignore_columns,
    # ignore_float_columns, and ignore_non_binary_integer_columns.

    if _ignore_float_columns:
        _float_columns = \
            np.arange(_n_features_in)[np.array(_original_dtypes) == 'float']

        __ = list(map(str, set(__handle_as_bool).intersection(_float_columns)))
        if len(__):
            q = "index" if len(__) == 1 else "indices"
            z = "is" if len(__) == 1 else "are"
            warnings.warn(
                f"column {q} {', '.join(__)} {z} designated as handle as "
                f"bool but {z} float and float columns are ignored. "
                f"\nignore float columns supersedes and the column is "
                f"ignored. "
            )
            del q, z

        del _float_columns, __


    if _ignore_non_binary_integer_columns:
        _non_bin_int_columns = \
            np.arange(_n_features_in)[np.array(_original_dtypes) == 'int']

        __ = list(map(str, set(__handle_as_bool).intersection(_non_bin_int_columns)))
        if len(__):
            q = "index" if len(__) == 1 else "indices"
            z = "is" if len(__) == 1 else "are"
            warnings.warn(
                f"column {q} {', '.join(__)} {z} designated as handle as "
                f"bool but {z} non-binary integer and non-binary integer "
                f"columns are ignored. \nignore non-binary integer columns "
                f"supersedes and the column is ignored."
            )
            del q, z

        del _non_bin_int_columns, __


    # if _threshold passed as int, must be >= 2, and no columns are
    # 'ignored' in this way. but if passed as list, then some can be 1.
    if isinstance(_threshold, int):
        pass
    else:  # must be Sequence[int] because of validation
        _thresholds = np.array(_threshold)
        _unit_thresholds = np.arange(len(_thresholds))[(_thresholds == 1)]
        __ = list(map(str, set(__handle_as_bool).intersection(_unit_thresholds)))
        if len(__) > 0:
            q = "index" if len(__) == 1 else "indices"
            z = "is" if len(__) == 1 else "are"
            warnings.warn(
                f"column {q} {', '.join(__)} {z} designated as handle as "
                f"bool but the threshold(s) {z} set to 1, which ignores "
                f"the column(s). \nignore supersedes and the column is "
                f"ignored."
            )
            del q, z

        del _thresholds, _unit_thresholds, __


    if len(__ignore_columns):

        __ = list(map(str, set(__handle_as_bool).intersection(__ignore_columns)))
        if len(__):
            q = "index" if len(__) == 1 else "indices"
            z = "is" if len(__) == 1 else "are"
            warnings.warn(
                f"column {q} {', '.join(__)} {z} designated as handle as "
                f"bool but {z} is also in 'ignore_columns'. "
                f"\n'ignore_columns' supersedes and the column is ignored."
            )
            del q, z

        del __

    # 'ignore_columns' is the only place where you can say to ignore an
    # 'obj' column
    # need to find and any 'obj' columns are handle_as_bool and not
    # ignored.

    if len(__ignore_columns):
        _ic_hab_intersection = \
            set(list(__ignore_columns)).intersection(list(__handle_as_bool))
    else:
        _ic_hab_intersection = set()

    _hab_not_ignored = \
        list(set(list(__handle_as_bool)) - set(_ic_hab_intersection))
    # _hab_not_ignored gives the _handle_as_bool columns that arent ignored
    _hab_not_ignored_dtypes = np.array(list(_original_dtypes))[_hab_not_ignored]

    if 'obj' in _hab_not_ignored_dtypes:
        MASK = (_hab_not_ignored_dtypes == 'obj')
        IDXS = ', '.join(map(str, np.array(list(_hab_not_ignored))[MASK]))

        _base_msg = (
            f"cannot use handle_as_bool on str/object columns "
            f"--- column index(es) == {IDXS}. "
        )

        if _raise:
            raise ValueError(_base_msg)
        else:
            _addon = (
                f"\na warning is emitted and exception is not raised. "
                f"\nafter fitting, you may be able to use the set_params "
                f"method to correct this issue."
            )
            warnings.warn(_base_msg + _addon)
            del _base_msg, _addon

        del _ic_hab_intersection


    return __ignore_columns, __handle_as_bool





