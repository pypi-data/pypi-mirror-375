# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
)
from .._type_aliases import KeepType
from ...__shared._type_aliases import XContainer

import warnings



def _val_keep_and_columns(
    _keep: KeepType,
    _columns: Sequence[str] | None,
    _X: XContainer
) -> None:
    """Validate `keep` and `columns`.

    Validate `columns`:
        must be None or Sequence[str] with len==X.shape[1]

    Validate `keep`:
        must be any of:
            Literal['first', 'last', 'random', 'none'],
            dict[str, Any],
            int (column index),
            str (feature name),
            callable(X) that returns an integer (column index)

        `keep` dict:
            must be len==1
            key is str
            warns if key already in columns
            value cannot be list-like or callable
        `keep` callable:
            must return non-bool integer in range of num features
        `keep` as column index:
            must be non-bool integer, in range of num features
        `keep` str literal:
            must be lower case
            cannot conflict with a feature name
        `keep` feature str:
            columns must be passed
            must be in columns

    Parameters
    ----------
    _keep : KeepType
        The strategy for handling the constant columns. See 'The keep
        Parameter' section for a lengthy explanation of the `keep`
        parameter.
    _columns : NDArray[str] | None of shape (n_features,)
        Exposed if `X` was passed in a container that has a header,
        otherwise None.
    _X : XContainer of shape (n_samples, n_features)
        The data to be searched for constant columns.

    Returns
    -------
    None

    """


    # validate types, shapes, of _columns ** * ** * ** * ** * ** * ** *

    if _columns is None:
        pass
    else:
        try:
            iter(_columns)
            if isinstance(_columns, (str, dict)):
                raise Exception
            assert len(_columns) == _X.shape[1]
            assert all(map(isinstance, _columns, (str for _ in _columns)))
        except Exception as e:
            raise ValueError(
                f"If passed, '_columns' must be a vector of strings whose "
                f"length is equal to the number of features in the data."
            )

    # END validate types, shapes, of _columns ** * ** * ** * ** * ** *



    _err_msg = (
        f"\n'keep' must be one of: "
        f"\nLiteral['first', 'last', 'random', 'none'], "
        f"\ndict[str, any], "
        f"\nint (column index), "
        f"\nstr (column header, if X was passed in a container with a header), "
        f"\ncallable on X, returning an integer indicating a valid column index."
        f"\ngot {type(_keep)}"
    )

    # validate keep as dict ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if isinstance(_keep, dict):
        _name = list(_keep.keys())[0]
        # must be one entry and key must be str
        if len(_keep) != 1 or not isinstance(_name, str):
            raise ValueError(_err_msg)
        # if keep conflicts with existing column name....
        if _columns is not None and _name in _columns:

            # the keep dict append for df is done in _transform()
            # this is the (pseudo) code that is used to do it.
            # _dtype = np.float64 if float(_value) else object
            # _X[_key] = np.full((_X.shape[0],), _value).astype(_dtype)
            warnings.warn(
                f"\n'keep' dictionary column name '{_name}' is already "
                f"in the data. "
                f"\nThere are two possible outcomes:"
                f"\n1) the original is not constant: the new constant "
                f"values will \noverwrite in the old column (generally "
                f"an undesirable outcome), or \n2) the original is "
                f"constant: the original column will be \nremoved, a new "
                f"column with the same name will be appended \nwith the "
                f"new constant values."
            )

        _base_msg = (
            "\nThe only allowed constant values are integers, floats, "
            "strings, and booleans."
        )

        try:
            # if is callable, except
            if callable(_keep[_name]):
                raise BrokenPipeError
            iter(_keep[_name])
            if isinstance(_keep[_name], str):
                raise Exception
            # if is any sequence beside string, except
            raise UnicodeError
        except BrokenPipeError:
            raise ValueError(
                f"The 'keep' dictionary value is a callable, which IM "
                f"does not allow. " + _base_msg
            )
        except UnicodeError:
            raise ValueError(
                f"The 'keep' dictionary value is a non-string sequence, "
                f"which IM does not allow. " + _base_msg
            )
        except Exception as e:
            # accept anything that is string or not a sequence
            pass

        del _name, _base_msg

        return # <====================================================

    # END validate keep as dict ** * ** * ** * ** * ** * ** * ** * ** *

    # validate keep as callable ** * ** * ** * ** * ** * ** * ** * ** *
    # returns an integer in range of num X features
    if callable(_keep):
        # this checks if callable(X) is int and in range of X.shape[1]
        _test_keep = _keep(_X)
        try:
            float(_test_keep)
            if _test_keep != int(_test_keep):
                raise Exception
            if isinstance(_test_keep, bool):
                raise Exception
            _test_keep = int(_test_keep)
            if _test_keep not in range(_X.shape[1]):
                raise Exception
            del _test_keep
            return  # <=================================================
        except Exception as e:
            raise ValueError(_err_msg)

    # END validate keep as callable ** * ** * ** * ** * ** * ** * ** *

    # validate keep as str ** * ** * ** * ** * ** * ** * ** * ** * ** *
    if isinstance(_keep, str):
        # could be one of the literals or a column header
        if _keep in ('first', 'last', 'random', 'none'):
            # this is when it is bad for 'keep' to be in _columns
            if _columns is not None and _keep in _columns:
                # if a feature name is one of the literals
                raise ValueError(
                    f"\nThere is a conflict with one of the feature names "
                    f"and the literals for :param: keep. \nColumn '{_keep}' "
                    f"conflicts with a keep literal. \nAllowed keep literals "
                    f"(case sensitive): 'first', 'last', 'random', 'none'. "
                    f"\nPlease change the column name or use a different "
                    f"keep literal.\n"
                )
        else:
            # is str, but is not one of the literals, then must be a column name
            _base_msg = f"\n:param: keep ('{_keep}') is "

            if _keep.lower() in ('first', 'last', 'random', 'none'):
                _addon = (f"\nIf you are trying use :param: keep literals "
                    f"('first', 'last', 'random', 'none'), \nonly enter "
                    f"these as lower-case."
                )
            else:
                _addon = ""


            if _columns is None:
                raise ValueError(
                    _base_msg + f"string but header was not passed. " + _addon
                )
            elif _keep not in _columns:
                raise ValueError(
                    _base_msg + f"not one of the seen features. " + _addon
                )
            elif _keep in _columns:
                # this is what we want to happen
                pass

            del _base_msg, _addon

        return  # <====================================================
    # END validate keep as str ** * ** * ** * ** * ** * ** * ** * ** *

    # validate keep as int ** * ** * ** * ** * ** * ** * ** * ** * ** *
    try:
        # float(_keep) is taking str like '3840' and converting to float!
        # the fix was to move 'validate keep as int' after 'validate keep
        # as str'
        float(_keep)
        if _keep != int(_keep):
            raise UnicodeError
        if isinstance(_keep, bool):
            raise UnicodeError
        if _keep not in range(_X.shape[1]):
            raise MemoryError
        return # <====================================================
    except UnicodeError:
        raise TypeError(_err_msg)
    except MemoryError:
        raise ValueError(_err_msg)
    except Exception as e:
        pass
    # END validate keep as int ** * ** * ** * ** * ** * ** * ** * ** *


    # the returns in the if blocks should prevent getting here.
    # if something is passed for :param: keep that dodges all the if
    # blocks, then raise.
    raise TypeError(_err_msg)





