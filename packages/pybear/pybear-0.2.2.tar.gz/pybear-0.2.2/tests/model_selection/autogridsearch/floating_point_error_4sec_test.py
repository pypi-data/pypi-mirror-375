# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest



class TestFloatingPointError:


    def test_floating_point_error(
        self, SKAutoGridSearch, sk_estimator_2, X_np, y_np
    ):

        _params = {
            'alpha': [[1e-300, 1e-299, 1e-298], 3, 'soft_float'],
            'fit_intercept': [[True, False], [2, 1, 1], 'fixed_bool']
        }

        with pytest.raises(ValueError):
            SKAutoGridSearch(
                estimator=sk_estimator_2, params=_params, total_passes=3
            ).fit(X_np, y_np)







