# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._fit._cv_results. \
    _cv_results_score_updater import _cv_results_score_updater

from pybear.model_selection.GSTCV._GSTCVMixin._validation._scoring import \
    master_scorer_dict



class TestCVResultsScoreUpdater:


    # def _cv_results_score_updater(
    #     _FOLD_x_SCORER__SCORE: MaskedHolderType,
    #     _type: Literal['train', 'test'],
    #     _trial_idx: int,
    #     _scorer: ScorerWIPType,
    #     _cv_results: CVResultsType
    # ) -> CVResultsType:

    # _FOLD_x_SCORER__SCORE must have shape (_n_splits, _n_scorers)

    # _trial_idx must be in range(len(cv_results_))  ... total permutations
    # _trial_idx dictates row of cv_results_ to fill

    # TEST PLAN:
    # build a rigged grid of scores. use _cv_results_score_updater to fill
    # cv_results_.  Verify correct columns are filled with correct values.
    # Using rigged grid for both test scores and train scores.


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 3,
            '_n_rows': 6,
            '_scorer_names':['accuracy', 'balanced_accuracy'],
            '_grids': [{'param_1':[1,2,3], 'param_2':[True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': False
        }],
        indirect=True
    )
    @pytest.mark.parametrize('_trial_idx', (0, 2, 5))
    @pytest.mark.parametrize('_type', ('test', 'train'))
    def test_accuracy_1(self, _cv_results_template, _type, _trial_idx):

        # 2 scorers, 1 param grid

        rigged_score_matrix_1 = \
            np.ma.masked_array(
                data=np.random.uniform(0, 1, (3, 2)), mask=False
            )

        _scorers = ['accuracy', 'balanced_accuracy']

        out_cv_results = _cv_results_score_updater(
            _FOLD_x_SCORER__SCORE = rigged_score_matrix_1,
            _type=_type,
            _trial_idx=_trial_idx,
            _scorer={k:v for k,v in master_scorer_dict.items() if k in _scorers},
            _cv_results=_cv_results_template
        )


        for _scorer_idx, _scorer in enumerate(_scorers):

            # ** * ** *
            _header = f'mean_{_type}_{_scorer}'
            assert _header in out_cv_results

            assert out_cv_results[_header][_trial_idx] == \
                np.mean(rigged_score_matrix_1[:, _scorer_idx])
            # ** * ** *

            # ** * ** *
            _header = f'std_{_type}_{_scorer}'
            assert _header in out_cv_results

            assert out_cv_results[_header][_trial_idx] == \
                np.std(rigged_score_matrix_1[:, _scorer_idx])
            # ** * ** *

            # ** * ** *
            for _split in range(3):
                _header = f'split{_split}_{_type}_{_scorer}'
                assert _header in out_cv_results

                assert out_cv_results[_header][_trial_idx] == \
                       rigged_score_matrix_1[_split, _scorer_idx]
            # ** * ** *


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 5,
            '_n_rows': 6,
            '_scorer_names':['balanced_accuracy'],
            '_grids': [{'abc':[1,2,3]}, {'abc':[8,9,10]}],
            '_return_train_score': False,
            '_fill_param_columns': False
        }],
        indirect=True
    )
    @pytest.mark.parametrize('_trial_idx', (1, 3, 4))
    @pytest.mark.parametrize('_type', ('test', ))
    def test_accuracy_2(self, _cv_results_template, _type, _trial_idx):

        # 1 scorer, 2 param grids

        rigged_score_matrix_2 = \
            np.ma.masked_array(
                data=np.random.uniform(0, 1, (5, 1)), mask=False
            )

        _scorers = ['balanced_accuracy']

        out_cv_results = _cv_results_score_updater(
            _FOLD_x_SCORER__SCORE = rigged_score_matrix_2,
            _type=_type,
            _trial_idx=_trial_idx,
            _scorer={k:v for k,v in master_scorer_dict.items() if k in _scorers},
            _cv_results=_cv_results_template
        )

        for _scorer_idx, _scorer in enumerate(_scorers):

            # ** * ** *
            _header = f'mean_{_type}_score'  # <------- diff from test 1
            assert _header in out_cv_results

            assert out_cv_results[_header][_trial_idx] == \
                np.mean(rigged_score_matrix_2[:, _scorer_idx])
            # ** * ** *

            # ** * ** *
            _header = f'std_{_type}_score'   # <------- diff from test 1
            assert _header in out_cv_results

            assert out_cv_results[_header][_trial_idx] == \
                np.std(rigged_score_matrix_2[:, _scorer_idx])
            # ** * ** *

            # ** * ** *
            for _split in range(3):
                _header = f'split{_split}_{_type}_score'   # <------- diff from test 1
                assert _header in out_cv_results

                assert out_cv_results[_header][_trial_idx] == \
                       rigged_score_matrix_2[_split, _scorer_idx]
            # ** * ** *






