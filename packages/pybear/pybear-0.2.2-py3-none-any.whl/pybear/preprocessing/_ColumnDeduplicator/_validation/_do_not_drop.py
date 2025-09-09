# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    DoNotDropType,
    FeatureNamesInType
)



def _val_do_not_drop(
    _do_not_drop: DoNotDropType,
    _n_features_in: int,
    _columns: FeatureNamesInType | None
) -> None:
    """Validate `do_not_drop`.

    May be None, a sequence of integers indicating column indices, or,
    if fitting is done on a container with a header, a sequence of
    strings that match any combination of the feature names in the data
    header.

    Parameters
    ----------
    _do_not_drop : DoNotDropType
        A list of columns not to be dropped. If fitting is done on a
        container that has a header, a list of feature names may be
        provided. Otherwise, a list of column indices must be provided.
        If a conflict arises, such as two columns specified in
        `do_not_drop` are duplicates of each other, the behavior is
        managed by `conflict`.
    _n_features_in : int
        The number of features in the data seen at first fit.
    _columns : FeatureNamesInType | None of shape (n_features,)
        If fitting is done on a container that has a header, this is a
        ndarray of strings, otherwise is None.

    Returns
    -------
    None

    """


    try:
        # if is None, just skip out
        if _do_not_drop is None:
            raise UnicodeError
        iter(_do_not_drop)
        try:
            _do_not_drop.ravel()
        except:
            pass
        if isinstance(_do_not_drop, (str, dict)):
            raise Exception
    except UnicodeError:
        pass
    except Exception as e:
        raise TypeError(
            f"if passed, 'do_not_drop' must be a list-like of"
            f" strings or integers, and cannot be empty"
        )

    _dnd_int = True
    try:
        if not all(map(lambda x: int(x) == x, _do_not_drop)):
            _dnd_int = False
    except:
        _dnd_int = False

    _dnd_str = True
    try:
        if not all(map(isinstance, _do_not_drop, (str for _ in _do_not_drop))):
            _dnd_str = False
    except:
        _dnd_str  = False

    if _dnd_int + _dnd_str + (_do_not_drop is None) != 1:
        raise TypeError(
            f"if passed, 'do_not_drop' must be a list-like of"
            f" strings or integers, and cannot be empty"
        )


    if _columns is not None:
        _base_err_msg = (f"when passing 'do_not_drop' with column names, "
            f"all entries must exactly match columns of the data. ")
        _err_msg = lambda x: f"column '{x}' is not in the original columns"
        if _dnd_str:
            for _col in _do_not_drop:
                if _col not in _columns:
                    raise ValueError(_base_err_msg + _err_msg(_col))
        del _base_err_msg, _err_msg

    else:
        if _dnd_str:
            raise TypeError(
                f"when a header is not passed with the data, 'do_not_drop' "
                f"can only contain integers"
            )


    if _dnd_int:
        _err_msg = lambda _: f"'do_not_drop' index {_} out of range"
        if min(_do_not_drop) < 0:
            raise ValueError(_err_msg(min(_do_not_drop)))
        if max(_do_not_drop) >= _n_features_in:
            raise ValueError(_err_msg(max(_do_not_drop)))
        del _err_msg






