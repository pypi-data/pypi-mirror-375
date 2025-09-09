# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from .._type_aliases import (
    FeatureNameCombinerType,
    FeatureNamesInType,
    CombinationsType
)

import numpy as np



def _gfno_poly(
    _X_feature_names_in: FeatureNamesInType,
    _active_combos: CombinationsType,
    _feature_name_combiner: FeatureNameCombinerType
) -> FeatureNamesInType:
    """Get feature names for the polynomial expansion component of the
    final output.

    Construct the polynomial feature names based on `feature_name_combiner`.
    If `min_degree` is 1, the feature names of X are prepended to the
    polynomial feature names (the output of this module) outside of this
    module.

    `_poly_feature_names` (the output of this) must match the order of
    `_active_combos`.

    `_active_combos` must be sorted first on asc tuple len (degree),
    then asc on the idxs in each tuple.

    If `_active_combos` is sorted correctly, then this output is sorted
    correctly at construction.

    `_active_combos` being sorted correctly depends on self._combos
    being sorted correctly.

    self._combos is built directly from itertools.combinations or
    `itertools.combinations_with_replacement`, and is sorted coming out
    of :func:`_combination_builder` to ensure the correct sort, in case
    itertools built-ins ever change.

    Parameters
    ----------
    _X_feature_names_in : FeatureNamesInType
        The feature names of the original data.
    _active_combos : CombinationsType
        The tuples of column index combinations that will be in the
        outputted polynomial expansion.
    _feature_name_combiner : FeatureNameCombinerType, default='as_indices'
        Sets the naming convention for the created polynomial features.
        See the lengthy notes in the main SPF module.

    Returns
    -------
    _poly_feature_names: FeatureNamesInType
        The feature names for the polynomial expansion.

    Notes
    -----

    **Type Aliases**

    FeatureNamesInType:
        np.ndarray[object]

    CombinationsType:
        tuple[tuple[int, ...], ...]

    FeatureNameCombinerType:
        Callable[[Sequence[str], tuple[int, ...]], str]
        | Literal['as_feature_names', 'as_indices']

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _X_feature_names_in cannot be None! if X was passed without a header,
    # then _X_feature_names_in must be the boilerplate default feature names
    assert isinstance(_X_feature_names_in, np.ndarray)
    assert _X_feature_names_in.dtype == object
    assert len(_X_feature_names_in.shape) == 1
    assert all(map(
        isinstance, _X_feature_names_in, (str for _ in _X_feature_names_in)
    ))

    assert isinstance(_active_combos, tuple)
    for _tuple in _active_combos:
        # this is important! for a single tuple, it must come in here
        # (leave _get_active_combos) as ((value1, value2),) like ((0,1),)
        assert isinstance(_tuple, tuple)
        assert all(map(isinstance, _tuple, (int for _ in _tuple)))
        assert min(_tuple) >= 0
        assert max(_tuple) <= len(_X_feature_names_in) - 1
        # all X indices for each combo tuple must always be sorted asc!
        assert sorted(list(_tuple)) == list(_tuple)

    assert callable(_feature_name_combiner) or \
           _feature_name_combiner in ['as_feature_names', 'as_indices']

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    if _feature_name_combiner == "as_indices":
        _poly_feature_names = list(map(str, list(_active_combos)))

    elif _feature_name_combiner == "as_feature_names":
        _poly_feature_names = []
        for _combo in _active_combos:

            # scan over the combo, get the powers by counting the number
            # of occurrences of X column indices
            _idx_ct_dict = {_X_idx: 0 for _X_idx in _combo}  # only unique idxs
            for _X_idx in _combo:
                _idx_ct_dict[_X_idx] += 1

            _poly_feature_name = ''

            for _X_idx in sorted(list(_idx_ct_dict.keys())):
                _name = _X_feature_names_in[_X_idx]
                _power = _idx_ct_dict[_X_idx]
                if _power == 1:
                    _poly_feature_name += f"{_name}"
                elif _power > 1:
                    _poly_feature_name += f"{_name}^{_power}"
                else:
                    raise AssertionError(f"algorithm failure")

                _poly_feature_name += "_"

            # appended a "_" after the last term, so remove it
            _poly_feature_names.append(_poly_feature_name[:-1])

    elif callable(_feature_name_combiner):

        _poly_feature_names = []

        for _combo in _active_combos:

            _poly_feature_name = \
                _feature_name_combiner(_X_feature_names_in, _combo)

            if not isinstance(_poly_feature_name, str):
                raise TypeError(
                    f"When 'feature_name_combiner' is a callable, it should "
                    f"return a string. \nGot {type(_poly_feature_name)} "
                    f"instead."
                )

            if _poly_feature_name in _X_feature_names_in:
                raise ValueError(
                    "The 'feature_name_combiner' callable has returned a "
                    "polynomial feature name that already exists in the "
                    "original feature names. \nIt must return unique names "
                    "for each new polynomial feature."
                )

            if _poly_feature_name in _poly_feature_names:
                raise ValueError(
                    "The 'feature_name_combiner' callable has returned the "
                    "same feature name twice. \nIt must return unique names "
                    "for each new polynomial feature."
                )

            _poly_feature_names.append(_poly_feature_name)


    return np.array(_poly_feature_names, dtype=object)




