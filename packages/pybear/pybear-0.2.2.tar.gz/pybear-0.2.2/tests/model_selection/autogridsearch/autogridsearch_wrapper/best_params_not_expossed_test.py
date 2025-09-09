# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest



class TestBestParamsNotExposed:


    # this should raise ValueError for not exposing best_params_
    def test_best_params_not_exposed(
        self, SKAutoGridSearch, sk_estimator_1, X_np, y_np
    ):

        _agscv = SKAutoGridSearch(
            estimator=sk_estimator_1,
            params={},
            refit=False,
            scoring=['accuracy', 'balanced_accuracy']
        )

        with pytest.raises(ValueError):
            _agscv.fit(X_np, y_np)






