# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import FeatureNamesInType

from ...__shared._validation._any_integer import _val_any_integer



def _val_feature_names_in(
    _feature_names_in: FeatureNamesInType | None,
    _n_features_in: int | None = None
) -> None:
    """Validate `feature_names_in` is None or 1D list-like of strings.

    If `_n_features_in` is provided and `_feature_names_in` is not None,
    the length of `_feature_names_in` must equal `_n_features_in`.

    Parameters
    ----------
    _feature_names_in : FeatureNamesInType
        If MCT was fit on a data container that had a header (e.g.
        pandas or polars dataframe) then this is a list-like of those
        feature names. Otherwise, is None.
    _n_features_in : int | None, default=None
        The number of features in the data that was fit.

    Returns
    -------
    None

    """


    _val_any_integer(
        _n_features_in, '_n_features_in', _min=1, _can_be_None=True
    )


    err_msg = (
        f"'_feature_names_in' must be None or a 1D list-like of strings "
        f"indicating the feature names of a data-bearing object. \nIf "
        f"list-like and '_n_features_in' is provided, the length must "
        f"equal '_n_features_in'."
    )

    try:
        if _feature_names_in is None:
            raise UnicodeError
        iter(_feature_names_in)
        if isinstance(_feature_names_in, (str, dict)):
            raise Exception
        if not all(map(
            isinstance, _feature_names_in, (str for _ in _feature_names_in)
        )):
            raise MemoryError
    except UnicodeError:
        pass
    except MemoryError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg

    if _feature_names_in is not None and _n_features_in is not None:
        if len(_feature_names_in) != _n_features_in:
            raise ValueError(
                f"len(_feature_names_in) ({len(_feature_names_in)}) must "
                f"equal _n_features_in ({_n_features_in})"
            )



