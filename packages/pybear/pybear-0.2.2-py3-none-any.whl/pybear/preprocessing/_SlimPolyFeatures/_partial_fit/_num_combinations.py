# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np


def _val_num_combinations(
    n_features_in_: int,
    _n_poly_combos: int,
    _min_degree: int,
    _max_degree: int,
    _intx_only: bool
) -> None:
    """Calculate the maximum number of features expected in the polynomial
    expansion and compare against computer system capabilities.

    Parameters
    ----------
    n_features_in_ : int
        Number of features in the fitted data, i.e., number of features
        before expansion.
    _n_poly_combos : int
        The number of column index tuples in self._combos (the total
        number of polynomial features that are candidates for the
        polynomial portion of the expansion.)
    _min_degree : int
        The minimum polynomial degree of the generated features.
        Polynomial terms with degree below 'min_degree' are not included
        in the final output array.
    _max_degree : int
        The maximum polynomial degree of the generated features.
    _intx_only : bool
        If True, only interaction features are produced, that is,
        polynomial features that are products of 'degree' distinct input
        features. Terms with power of 2 or higher for any feature are
        excluded. If False, produce the full polynomial expansion.

    Returns
    -------
    None

    """


    for _ in (n_features_in_, _n_poly_combos, _min_degree, _max_degree):
        assert isinstance(_, int)
        assert not isinstance(_, bool)

    assert n_features_in_ >= 1
    assert _n_poly_combos >= 1
    assert _min_degree >= 1, f"min_degree == 0 shouldnt be getting in here"
    assert _max_degree >= 2, f"max_degree in [0,1] shouldnt be getting in here"
    assert _max_degree >= _min_degree

    assert isinstance(_intx_only, bool)

    if _min_degree == 1:
        _n_output_features = n_features_in_ + _n_poly_combos
    else:
        _n_output_features = _n_poly_combos


    # this is taken almost verbatim from
    # sklearn.preprocessing._polynomial.PolynomialFeatures.fit()
    if _n_output_features > np.iinfo(np.intp).max:

        msg = (
            "The output that would result from the current configuration "
            f" would have {_n_output_features} features which is too "
            f" large to be indexed by {np.intp().dtype.name}. Please "
            f" change some or all of the following:\n- The number of "
            f" features in the input, currently {n_features_in_=}"
            f" \n- The range of degrees to calculate, currently"
            f" [{_min_degree}, {_max_degree}]\n- Whether to output only"
            f" interaction terms, currently {_intx_only}."
        )

        if np.intp == np.int32 and _n_output_features <= np.iinfo(np.int64).max:
            msg += (
            "\nNote that the current Python runtime has a limited 32 bit "
            "address space and that this configuration would have been "
            "admissible if run on a 64 bit Python runtime."
            )

        raise ValueError(msg)





