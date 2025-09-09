# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import itertools

from pybear.preprocessing._SlimPolyFeatures._partial_fit. \
    _get_dupls_for_combo_in_X_and_poly import _get_dupls_for_combo_in_X_and_poly



class TestJoblib:


    # need to have >= _n_cols number of columns to engage joblib
    # just do minor checks for accuracy


    def test_it_works(self, _X_factory):

        # _job_size is set to 10 below
        _shape = (123, 23)


        _X = _X_factory(
            _dupl=None,
            _has_nan=False,
            _format='np',
            _dtype='flt',
            _columns=None,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )


        out = _get_dupls_for_combo_in_X_and_poly(
            _X=_X,
            _poly_combos=list(itertools.combinations_with_replacement(range(_X.shape[1]), 2)),
            _min_degree=1,
            _equal_nan=True,
            _rtol=1e-5,
            _atol=1e-8,
            _n_jobs=2,
            _job_size=10
        )

        # returns a list of tuples
        assert isinstance(out, list)




