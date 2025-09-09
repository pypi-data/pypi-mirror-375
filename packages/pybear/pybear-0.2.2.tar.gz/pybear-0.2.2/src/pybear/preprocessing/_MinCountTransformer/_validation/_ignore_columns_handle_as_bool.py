# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence,
    TypeAlias
)
from .._type_aliases import (
    IgnoreColumnsType,
    HandleAsBoolType,
    FeatureNamesInType
)

import numbers

import numpy as np

from .._validation._feature_names_in import _val_feature_names_in

from ...__shared._validation._any_integer import _val_any_integer

from ....utilities._nan_masking import nan_mask_numerical



AllowedType: TypeAlias = Sequence[Literal[
    'callable', 'Sequence[str]', 'Sequence[int]', 'None'
]]



def _val_ignore_columns_handle_as_bool(
    _value: IgnoreColumnsType | HandleAsBoolType,
    _name: Literal['ignore_columns', 'handle_as_bool'],
    _allowed: AllowedType,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType | None = None
) -> None:
    """Validate `ignore_columns` or `handle_as_bool`.

    Subject to the allowed states indicated in `_allowed`.

    Validate:

    - passed value is Sequence[str], Sequence[int], Callable, or None,
        subject to those allowed by `_allowed`.

    - if sequence, contains valid integers or strings

    Parameters
    ----------
    _value : Sequence[str] | Sequence[int] | callable | None
        The value passed for the `ignore_columns` or `handle_as_bool`
        parameter to the `MinCountTransformer` instance.
    _name : Literal['ignore_columns', 'handle_as_bool']
        The name of the parameter being validated.
    _allowed : AllowedType
        The datatype which `_value` is allowed to be.
    _n_features_in : int
        The number of features in the data.
    _feature_names_in : FeatureNamesInType | None, default=None
        If the MCT instance was fitted on a data-bearing object that had
        a header (like a pandas or polars dataframe) then this is a 1D
        list-like of strings. Otherwise, is None.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    AllowedType:
        Sequence[Literal[
            'callable', 'Sequence[str]', 'Sequence[int]', 'None'
        ]]

    """


    # other validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # name -- -- -- -- -- -- -- -- --
    assert isinstance(_name, str)
    _name = _name.lower()
    assert _name in ['ignore_columns', 'handle_as_bool']
    # END name -- -- -- -- -- -- -- --

    # allowed -- -- -- -- -- -- -- --
    _allowed_allowed = ['callable', 'Sequence[str]', 'Sequence[int]', 'None']
    _err_msg = lambda x: (
        f"'_allowed' must be a 1D list-like with values in "
        f"{', '.join(_allowed_allowed)}, case sensitive. cannot be empty. "
        f"got {x}."
    )

    try:
        _addon = f"type {type(_allowed)}"
        iter(_allowed)
        if isinstance(_allowed, (str, dict)):
            raise Exception
        if len(np.array(list(_allowed)).shape) != 1:
            _addon = f"{len(np.array(list(_allowed)).shape)}D"
            raise UnicodeError
        if len(_allowed) == 0:
            _addon = f"empty"
            raise UnicodeError
        if not all(map(isinstance, _allowed, (str for _ in _allowed))):
            _addon = f"non-string entries"
            raise Exception
        if not all(map(lambda x: x in _allowed_allowed, _allowed)):
            _bad = [x for x in _allowed if x not in _allowed_allowed]
            _addon = f"bad entries: {', '.join(_bad)}"
            del _bad
            raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg(_addon))
    except Exception as e:
        raise TypeError(_err_msg(_addon))

    _allowed = list(map(str, _allowed))

    del _allowed_allowed, _err_msg, _addon
    # END allowed -- -- -- -- -- -- -- --

    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    _val_feature_names_in(_feature_names_in, _n_features_in)
    # END other validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # ESCAPE VALIDATION IF _value IS CALLABLE OR None

    if _value is None:
        if 'None' in _allowed:
            return
        else:
            raise ValueError(
                f"'{_name}' must be in {', '.join(_allowed)}. got None."
            )

    elif callable(_value):
        if 'callable' in _allowed:
            return
        else:
            raise ValueError(
                f"'_value' must be in {', '.join(_allowed)}. got a callable."
            )


    # dealt with None & callable, must be Sequence[str] or Sequence[int]
    _err_msg = lambda x: (f"'{_name}' must be None, a list-like, or a callable "
               f"that returns a list-like. got {x}.")

    try:
        _addon = f"type {type(_value)}"
        iter(_value)
        if isinstance(_value, (str, dict)):
            raise Exception
        if len(np.array(list(_value)).shape) != 1:
            _addon = f"{len(np.array(list(_value)).shape)}D"
            raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg(_addon))
    except Exception as e:
        raise TypeError(_err_msg(_addon))

    del _err_msg, _addon


    if 'Sequence[str]' not in _allowed and 'Sequence[int]' not in _allowed:
        raise ValueError(
            f"'_value' is list-like but no list-likes are allowed"
        )


    # if list-like, validate contents are all str or all int ** * ** *

    err_msg = (
        f"if '{_name}' is passed as a list-like, it must contain all "
        f"integers indicating column indices or all strings indicating "
        f"column names"
    )

    # do not use .astype(np.float64) to check if is num/str!
    # ['0787', '5927', '4060', '2473'] will pass and be treated as
    # column indices when they are actually column headers.
    if len(_value) == 0:
        is_int, is_str, is_empty = False, False, True
    elif all(map(isinstance, _value, (str for _ in _value))):
        is_int, is_str, is_empty = False, True, False
    elif all(map(isinstance, _value, (numbers.Real for _ in _value))):
        # ensure all are integers
        if any(map(isinstance, _value, (bool for _ in _value))):
            raise TypeError(err_msg)
        if np.any(nan_mask_numerical(np.array(list(_value), dtype=object))):
            raise TypeError(err_msg)
        if not all(map(lambda x: int(x)==x, _value)):
            raise TypeError(err_msg)
        _value = sorted(list(map(int, _value)))
        is_int, is_str, is_empty = True, False, False
    else:
        raise TypeError(err_msg)
    # END if list-like validate contents are all str or all int ** * **

    if len(set(_value)) != len(_value):
        raise ValueError(f"there are duplicate values in {_name}")

    # validate list-like against characteristics of X ** ** ** ** ** **

    # _feature_names_in is not necessarily available, could be None

    if is_empty:
        # it might be Sequence[str] or Sequence[int] but is empty
        pass
    elif is_int:

        if 'Sequence[int]' not in _allowed:
            raise ValueError(
                f"'_value' is Sequence[int] but Sequence[int] is not "
                f"allowed"
            )

        if min(_value) < -_n_features_in:
            raise ValueError(
                f"'{_name}' index {min(_value)} is out of bounds for "
                f"data with {_n_features_in} features"
            )

        if max(_value) >= _n_features_in:
            raise ValueError(
                f"'{_name}' index {max(_value)} is out of bounds for "
                f"data with {_n_features_in} features"
            )
    elif is_str:

        if 'Sequence[str]' not in _allowed:
            raise ValueError(
                f"'_value' is Sequence[str] but Sequence[str] is not "
                f"allowed"
            )

        if _feature_names_in is not None:

            for _column in _value:
                if _column not in _feature_names_in:
                    raise ValueError(
                        f"'{_name}' entry column '{_column}', is not in "
                        f"the passed column names"
                    )
        else: # feature_names_in_ is None
            raise ValueError(
                f"when the data is passed without column names '{_name}' "
                f"as list-like can only contain indices"
            )
    else:
        raise Exception

    del is_int, is_str, is_empty

    # END validate list-like against characteristics of X ** ** ** ** **




