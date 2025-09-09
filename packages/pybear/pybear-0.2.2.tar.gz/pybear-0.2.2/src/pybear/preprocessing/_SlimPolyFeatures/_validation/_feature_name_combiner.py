# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import FeatureNameCombinerType



def _val_feature_name_combiner(
    _feature_name_combiner: FeatureNameCombinerType,
) -> None:
    """Validate `_feature_name_combiner`.

    Must be:

    1) Literal 'as_feature_names'
    2) Literal 'as_indices
    3) a callable that takes as input:
        A) a 1D vector of strings (the feature names of X)
        B) a variable-length tuple of integers (the polynomial column
            indices combination tuple for a single poly feature),
        and always returns a string.

    The output of `_feature_name_combiner` is tested directly for the
    actual kept combos at the point of poly feature name generation
    in :func:`_gfno_poly`. The tested characteristics:

    1) returns a string
    2) the returned string is not already in the original feature names
    3) the returned string is not already in the new poly feature names

    Parameters
    ----------
    _feature_name_combiner : FeatureNameCombinerType, default='as_indices'
        Sets the naming convention for the created polynomial features.

        See the lengthy notes in the main SPF module.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    FeatureNameCombinerType:
        Callable[[Sequence[str], tuple[int, ...]], str]
        | Literal['as_feature_names', 'as_indices']

    """


    try:
        if callable(_feature_name_combiner):
            raise UnicodeError
        elif _feature_name_combiner in ['as_feature_names', 'as_indices']:
            raise UnicodeError
        raise Exception
    except UnicodeError:
        pass
    except Exception as exc:
        raise ValueError(
            f"\ninvalid :param: feature_name_combiner. must be: "
            f"\n1) Literal 'as_feature_names', "
            f"\n2) Literal 'as_indices', "
            f"\n- or -"
            f"\n3) a callable that takes as input:"
            f"\n   A) a 1D vector of strings (the feature names of X) "
            f"\n   B) a variable-length tuple of integers (the polynomial "
            f"\n      column indices combination for a single poly feature), "
            f"\nand always returns a string."
        )






