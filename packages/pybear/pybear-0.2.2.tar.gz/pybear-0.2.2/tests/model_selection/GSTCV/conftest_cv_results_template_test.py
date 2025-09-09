# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from sklearn.model_selection import ParameterGrid



class TestCVResultsFixture:

    #     _n_splits = request.param['_n_splits']
    #     _n_rows = request.param['_n_rows']
    #     _scorer_names = request.param['_scorer_names']
    #     _grids = request.param['_grids']
    #     _return_train_score = request.param['_return_train_score']
    #     _fill_param_columns = request.param['_fill_param_columns']


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits':3,
            '_n_rows':200,
            '_scorer_names':['accuracy', 'balanced_accuracy'],
            '_grids': [{'param_1':[1,2,3], 'param_2':[True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': False
        }],
        indirect=True
    )
    def test_accuracy_1(self, _cv_results_template):

        # accuracy with 2 scorers, 1 param grid

        # 1) turn cv_results to dataframe
        out = pd.DataFrame(_cv_results_template)

        # 2) get rows
        assert out.shape[0] == 200

        # 3 get columns
        __ = out.columns

        # ** * ** *

        _col_ctr = 0

        assert 'mean_fit_time' in __
        assert 'std_fit_time' in __
        assert 'mean_score_time' in __
        assert 'std_score_time' in __
        assert 'param_param_1' in __
        assert 'param_param_2' in __
        assert 'params' in __

        _col_ctr += 7

        _scorer = ['accuracy', 'balanced_accuracy']


        for metric in _scorer:
            suffix = f'{metric}'

            assert f'best_threshold_{suffix}' in __

            _col_ctr += 1

            for split in range(3):
                assert f'split{split}_test_{suffix}' in __
                _col_ctr += 1

            assert f'mean_test_{suffix}' in __
            assert f'std_test_{suffix}' in __
            assert f'rank_test_{suffix}' in __

            _col_ctr += 3

            for split in range(3):
                assert f'split{split}_train_{suffix}' in __
                _col_ctr += 1

            assert f'mean_train_{suffix}' in __
            assert f'std_train_{suffix}' in __

            _col_ctr += 2

        # correct number of columns
        assert _col_ctr == out.shape[1] == len(__)
        # ** * ** *



    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 5,
            '_n_rows': 271,
            '_scorer_names': ['balanced_accuracy'],
            '_grids': [{'abc': [1, 2]}, {'xyz': ['a', 'b']}],
            '_return_train_score': False,
            '_fill_param_columns': False
        }],
        indirect = True
    )
    def test_accuracy_2(self, _cv_results_template):

        # accuracy with 1 scorer, 2 param grids

        # 1) turn cv_results to dataframe
        out = pd.DataFrame(_cv_results_template)

        # 2) get rows
        assert out.shape[0] == 271

        # 3) get columns
        __ = out.columns

        # ** * ** *

        _col_ctr = 0

        assert 'mean_fit_time' in __
        assert 'std_fit_time' in __
        assert 'mean_score_time' in __
        assert 'std_score_time' in __
        assert 'param_abc' in __
        assert 'param_xyz' in __
        assert 'params' in __

        _col_ctr += 7

        _scorer = ['balanced_accuracy']

        for metric in _scorer:
            suffix = 'score'

            assert f'best_threshold' in __

            _col_ctr += 1

            for split in range(5):
                assert f'split{split}_test_{suffix}' in __
                _col_ctr += 1

            assert f'mean_test_{suffix}' in __
            assert f'std_test_{suffix}' in __
            assert f'rank_test_{suffix}' in __

            _col_ctr += 3

        # correct number of columns
        assert _col_ctr == out.shape[1] == len(__)
        # ** * ** *



    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 5,
            '_n_rows': 8,
            '_scorer_names': ['balanced_accuracy'],
            '_grids': [
                {'abc': [1, 2], 'xyz': ['a', 'b']},
                {'abc': [3, 4], 'xyz': ['c', 'd']}
            ],
            '_return_train_score': False,
            '_fill_param_columns': True
        }],
        indirect = True
    )
    def test_accuracy_filled_param_columns(self, _cv_results_template):

        # accuracy filling 'params' and other 'param_{}' columns,
        # 1 scorer, 2 param grids

        out = _cv_results_template

        param_check = np.empty(0, dtype=object)

        GRIDS = [
            {'abc': [1, 2], 'xyz': ['a', 'b']},
            {'abc': [3, 4], 'xyz': ['c', 'd']}
        ]

        for _grid in reversed(GRIDS):

            param_check = np.hstack((
                np.fromiter(ParameterGrid(_grid), dtype=object),
                param_check
            ))


        param_1_check = np.ma.empty(len(param_check), dtype=np.uint8)
        param_2_check = np.ma.empty(len(param_check), dtype=object)
        for idx, _grid in enumerate(param_check):

            param_1_check[idx] = np.uint8(param_check[idx]['abc'])
            param_2_check[idx] = param_check[idx]['xyz']

        assert np.array_equiv(out['params'], param_check)
        assert np.array_equiv(out['param_abc'], param_1_check)
        assert np.array_equiv(out['param_xyz'], param_2_check)

        # ** * ** *





