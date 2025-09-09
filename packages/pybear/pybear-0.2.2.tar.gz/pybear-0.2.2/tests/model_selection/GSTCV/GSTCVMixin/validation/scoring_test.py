# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

from pybear.model_selection.GSTCV._GSTCVMixin._validation._scoring import \
    _val_scoring



class TestValScoring:


    @pytest.mark.parametrize('junk_scoring',
        (0, 1, True, False, None, np.nan)
    )
    def test_rejects_anything_not_str_callable_dict_iterable(self, junk_scoring):

        with pytest.raises(TypeError):
            _val_scoring(junk_scoring, _must_be_dict=False)


    @pytest.mark.parametrize('junk_scoring',
        ('junk', 'garbage', 'trash', 'rubbish', 'waste', 'refuse')
    )
    def test_rejects_bad_strs(self, junk_scoring):

        with pytest.raises(ValueError):
            _val_scoring(junk_scoring, _must_be_dict=False)


    @pytest.mark.parametrize('good_scoring',
        ('accuracy', 'balanced_accuracy', 'precision', 'recall')
    )
    def test_accepts_good_strs(self, good_scoring):

        assert _val_scoring(good_scoring, _must_be_dict=False) is None


    @pytest.mark.parametrize('junk_scoring',
        (lambda x: 'junk', lambda x: [0,1], lambda x,y: min, lambda x,y: x)
    )
    def test_rejects_non_num_callables(self, junk_scoring):

        with pytest.raises(ValueError):
            _val_scoring(junk_scoring, _must_be_dict=False)


    def test_accepts_good_callable(self):

        good_callable = lambda y1, y2: np.sum(np.array(y2)-np.array(y1))

        out = _val_scoring(good_callable, _must_be_dict=False) is None


    @pytest.mark.parametrize('junk_scoring', ([], (), {}))
    def test_rejects_empty(self, junk_scoring):

        with pytest.raises(ValueError):
            _val_scoring(junk_scoring, _must_be_dict=False)


    @pytest.mark.parametrize('junk_lists',
        ([1,2,3], ('a','b','c'), {0,1,2}, ['trash', 'garbage', 'junk'])
    )
    def test_rejects_junk_lists(self, junk_lists):

        with pytest.raises((TypeError, ValueError)):
            _val_scoring(junk_lists, _must_be_dict=False)


    @pytest.mark.parametrize('good_lists',
        (['precision', 'recall'], ('accuracy','balanced_accuracy'),
         {'f1', 'balanced_accuracy', 'recall', 'precision'})
    )
    def test_accepts_good_list_likes(self, good_lists):
        assert _val_scoring(good_lists, _must_be_dict=False) is None


    @pytest.mark.parametrize('junk_dicts',
        ({'a':1, 'b':2}, {0:1, 1:2}, {0:[1,2,3], 1:[2,3,4]},
         {'metric1': lambda y1, y2: 'trash', 'metric2': lambda x: 1})
    )
    def test_rejects_junk_dicts(self, junk_dicts):

        with pytest.raises(ValueError):
            _val_scoring(junk_dicts, _must_be_dict=False)


    @pytest.mark.parametrize('good_dict',
        ({'accuracy': accuracy_score, 'f1': f1_score, 'recall': recall_score},
         {'metric1': precision_score, 'metric2': recall_score})
    )
    def test_accepts_good_dicts(self, good_dict):

        assert _val_scoring(good_dict, _must_be_dict=False) is None


    @pytest.mark.parametrize('_scoring',
        ('str', 'list_str', 'callable', 'dict_callable')
    )
    @pytest.mark.parametrize('_must_be_dict', (True, False))
    def test_must_be_dict_works(self, _scoring, _must_be_dict):

        _will_raise = False
        if _must_be_dict and _scoring != 'dict_callable':
            _will_raise = True


        if _scoring == 'str':
            _scoring = 'accuracy'
        elif _scoring == 'list_str':
            _scoring = ['precision', 'recall']
        elif _scoring == 'callable':
            _scoring = lambda y1, y2: 0.5
        elif _scoring == 'dict_callable':
            _scoring = {'scorer1': lambda y1, y2: 0, 'scorer2': lambda y1, y2: 1}
        else:
            raise Exception







