# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




import itertools

from ._num_combinations import _val_num_combinations



def _combination_builder(
    n_features_in_:int,
    _min_degree:int,
    _max_degree:int,
    _intx_only:bool
) -> list[tuple[int, ...]]:
    """Create a list containing the tuples of the column indices to be
    multiplied together for the polynomial expansion.

    The size of the list is validated to ensure it is small enough to be
    indexed by the current operating system.

    Parameters
    ----------
    n_features_in_ : int
        The number of features in X.
    _min_degree : int
        The minimum polynomial degree of the generated features.
        Polynomial terms with degree below `_min_degree` are not
        included in the final output array.
    _max_degree : int
        The maximum polynomial degree of the generated features.
    _intx_only : bool
        If True, only interaction features are produced, that is,
        polynomial features that are products of 'degree' distinct input
        features. Terms with power of 2 or higher for any feature are
        excluded. If False, produce the full polynomial expansion.

    Returns
    -------
    _combinations : list[tuple[int, ...]]
        A list containing the tuples of column index combinations to be
        multiplied together for the polynomial expansion.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(n_features_in_, int)
    assert not isinstance(n_features_in_, bool)
    assert n_features_in_ >= 1

    assert isinstance(_min_degree, int)
    assert not isinstance(_min_degree, bool)
    assert _min_degree >= 1, \
        f"min_degree == 0 shouldnt be getting in here"

    assert isinstance(_max_degree, int)
    assert not isinstance(_max_degree, bool)
    assert _max_degree >= 2, \
        f"max_degree in [0,1] shouldnt be getting in here"

    assert _max_degree >= _min_degree

    assert isinstance(_intx_only, bool)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _min_degree = max(2, _min_degree)
    # if _min_degree == 1, then the first order component (the original
    # data) is handled directly in SPF.transform(). Only need to generate
    # any terms that are greater than first order.


    fxn = itertools.combinations if _intx_only else \
        itertools.combinations_with_replacement

    _combinations = []
    for _deg in range(_min_degree, _max_degree + 1):
        _combinations.extend(list(fxn(range(n_features_in_), _deg)))

    # this checks the number of features in the output polynomial
    # expansion for indexability based on the max value allowed by np.intp
    _val_num_combinations(
        n_features_in_,
        _n_poly_combos=len(_combinations),
        _min_degree=_min_degree,
        _max_degree=_max_degree,
        _intx_only=_intx_only
    )

    # _combinations MUST ALWAYS BE asc on degree (shortest combos to
    # longest combos), then sorted asc on combo idxs. the output should
    # be coming out of itertools like that, but ensure always sorted in
    # case itertools ever changes
    _combinations = sorted(_combinations, key = lambda x: (len(x), x))


    return _combinations





