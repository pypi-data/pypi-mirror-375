# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import numbers

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._scoring \
    import _cond_scoring



class TestCondScoring:


    @pytest.mark.parametrize('good_scoring',
        ('accuracy', 'balanced_accuracy', 'precision', 'recall')
    )
    def test_accepts_good_strs(self, good_scoring):

        # because len(out)==1, actual scorer name is changed to 'score'

        _og_good_scoring = deepcopy(good_scoring)
        out = _cond_scoring(good_scoring)
        assert isinstance(out, dict)
        assert len(out) == 1
        assert 'score' in out
        assert callable(out['score'])
        assert isinstance(out['score']([1, 0, 1, 1], [1, 0, 0, 1]), float)
        assert good_scoring == _og_good_scoring


    def test_accepts_good_callable(self):

        good_callable = lambda y1, y2: np.sum(np.array(y2)-np.array(y1))
        _og_good_callable = deepcopy(good_callable)

        out = _cond_scoring(good_callable)
        assert isinstance(out, dict)
        assert len(out) == 1
        assert 'score' in out
        assert callable(out['score'])
        assert isinstance(out['score']([1, 0, 1, 1], [1, 0, 0, 1]), numbers.Real)
        assert good_callable == _og_good_callable


    @pytest.mark.parametrize('good_lists',
        (['precision', 'recall'], ('accuracy','balanced_accuracy'),
         {'f1', 'balanced_accuracy', 'recall', 'precision'})
    )
    def test_accepts_good_lists(self, good_lists):

        _og_good_lists = deepcopy(good_lists)

        out = _cond_scoring(good_lists)
        assert isinstance(out, dict)
        assert len(out) == len(good_lists)
        for metric in good_lists:
            assert metric in out
            assert callable(out[metric])
            assert isinstance(out[metric]([1,0,1,1], [1,0,0,1]), float)

        assert good_lists == _og_good_lists


    @pytest.mark.parametrize('good_dict',
        ({'accuracy': accuracy_score, 'f1': f1_score, 'recall': recall_score},
         {'metric1': precision_score, 'metric2': recall_score})
    )
    def test_accepts_good_dicts(self, good_dict):

        _og_good_dict = deepcopy(good_dict)

        out = _cond_scoring(good_dict)
        assert isinstance(out, dict)
        assert len(out) == len(good_dict)
        for metric in good_dict:
            assert metric in out
            assert callable(out[metric])
            assert isinstance(out[metric]([0,1,0,1],[1,0,0,1]), float)

        assert good_dict == _og_good_dict



