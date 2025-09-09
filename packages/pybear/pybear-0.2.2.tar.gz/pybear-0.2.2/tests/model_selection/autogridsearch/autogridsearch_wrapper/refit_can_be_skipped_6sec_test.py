# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Callable

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _refit_can_be_skipped import _refit_can_be_skipped

import pytest

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import (
    GridSearchCV as SklearnGridSearchCV,
    RandomizedSearchCV as SklearnRandomizedSearchCV,
    HalvingGridSearchCV,
    HalvingRandomSearchCV
)

from pybear.model_selection.GSTCV._GSTCV import GSTCV



class TestRefitCanBeSkipped:


    _parent_gscvs = (
        SklearnGridSearchCV, SklearnRandomizedSearchCV, HalvingGridSearchCV,
        HalvingRandomSearchCV
    )


    @pytest.mark.parametrize('_GridSearchParent', _parent_gscvs)
    @pytest.mark.parametrize('_scoring',
        [
            None,
            'balanced_accuracy',
            ['accuracy'],
            ['accuracy', 'balanced_accuracy'],
            lambda x: 1,
            {'accuracy': lambda x: 0, 'precision': lambda x: 1.0},
            False
        ]
    )
    @pytest.mark.parametrize('_total_passes', (1, 2, 3))
    def test_accuracy(self, _GridSearchParent, _scoring, _total_passes):

        # can only return True if:
        #   sklearn or pybear GSCV (must have refit param, these are guaranteed
        #   to have it)
        #   not multimetric
        #   total_passes > 1

        _allowed = (
            SklearnGridSearchCV, SklearnRandomizedSearchCV, GSTCV
        )

        # if parent GSCV doesnt have a scoring method (not likely to happen),
        # False is passed to _refit_can_be_skipped, and then we assume
        # multimetric so refit never turns off
        _is_not_multimetric = isinstance(_scoring, (type(None), str, Callable))

        _exp = all((
            _GridSearchParent in _allowed,
            _is_not_multimetric,
            _total_passes > 1
        ))

        out = _refit_can_be_skipped(_GridSearchParent, _scoring, _total_passes)


        assert out is _exp







