# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.model_selection.GSTCV._GSTCVMixin._fit._cv_results._cv_results_builder \
    import _cv_results_builder



class TestCVResultsBuilderTest:

    @staticmethod
    @pytest.fixture
    def good_param_grid():
        # must be entered as a list (as it would be passing thru GSTCV internals)
        return [
            {'kernel': ['rbf'], 'gamma': [0.1, 0.2], 'test_param': [1, 2, 3]},
            {'kernel': ['poly'], 'degree': [2, 3], 'test_param': [1, 2, 3]},
            {}
        ]


    @staticmethod
    @pytest.fixture
    def correct_cv_results_len(good_param_grid):

        total_rows = 0
        for _grid in good_param_grid:

            if _grid == {}:
                total_rows += 1
            else:
                total_rows += np.prod(list(map(len, _grid.values())))

        return int(total_rows)

    # END fixtures
    # *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('_junk_param_grid',
        (-1, 0, 1, np.pi, True, False, 'trash', None, min,
        [0, 1], (0, 1), {0, 1}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_param_grid(self, _junk_param_grid, standard_WIP_scorer):
        with pytest.raises(TypeError):
            cv_results_output, _ = _cv_results_builder(
                _param_grid=_junk_param_grid,
                _n_splits=3,
                _scorer=standard_WIP_scorer,
                _return_train_score=True
            )


    @pytest.mark.parametrize('_junk_n_splits',
        (-1, 0, 1, np.pi, True, False, 'trash', None, min,
        [0, 1], (0, 1), {0, 1}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_n_splits(
        self, good_param_grid, _junk_n_splits, standard_WIP_scorer
    ):
        with pytest.raises((TypeError, ValueError)):
            cv_results_output, _ = _cv_results_builder(
                _param_grid=good_param_grid,
                _n_splits=_junk_n_splits,
                _scorer=standard_WIP_scorer,
                _return_train_score=True
            )


    @pytest.mark.parametrize('_junk_scorer',
        (-1, 0, 1, np.pi, True, False, 'trash', None, min,
        [0, 1], (0, 1), {0, 1}, lambda x: x)
    )
    def test_rejects_junk_scorer(self, good_param_grid, _junk_scorer):
        with pytest.raises(TypeError):
            cv_results_output, _ = _cv_results_builder(
                _param_grid=good_param_grid,
                _n_splits=3,
                _scorer=_junk_scorer,
                _return_train_score=True
            )


    @pytest.mark.parametrize('_junk_return_train_score',
         (-1, 0, 1, np.pi, 'trash', None, min,
          [0, 1], (0, 1), {0, 1}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_train_score(
        self, _junk_return_train_score, good_param_grid, standard_WIP_scorer
    ):
        with pytest.raises(TypeError):
            cv_results_output, _ = _cv_results_builder(
                _param_grid=good_param_grid,
                _n_splits=3,
                _scorer=standard_WIP_scorer,
                _return_train_score=_junk_return_train_score
            )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('_n_splits', (3, 4, 5))
    @pytest.mark.parametrize('_scoring',
        ({'accuracy': lambda y1, y2: 0.1231},
        {'precision': lambda y1, y2: 0.8987, 'recall': lambda y1, y2: 0.2342})
    )
    @pytest.mark.parametrize('return_train', (True, False))
    def test_cv_results_builder(
        self, _n_splits, _scoring, return_train, good_param_grid,
        correct_cv_results_len
    ):

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # BUILD VERIFICATION STUFF ** * ** * ** * ** * ** * ** * ** * ** * ** *
        COLUMN_CHECK = [
            'mean_fit_time',
            'std_fit_time',
            'mean_score_time',
            'std_score_time'
        ]

        # UNIQUE PARAMS
        # notice set!
        COLUMN_CHECK += list({'param_' + _ for __ in good_param_grid for _ in __})
        COLUMN_CHECK += ['params']
        for sub_scoring in _scoring:

            if len(_scoring) == 1:
                COLUMN_CHECK += ['best_threshold']
            else:
                COLUMN_CHECK += [f'best_threshold_{sub_scoring}']

            suffix = 'score' if len(_scoring) == 1 else sub_scoring
            for split in range(_n_splits):
                COLUMN_CHECK += [f'split{split}_test_{suffix}']
            COLUMN_CHECK += [f'mean_test_{suffix}']
            COLUMN_CHECK += [f'std_test_{suffix}']
            COLUMN_CHECK += [f'rank_test_{suffix}']
            if return_train:
                for split in range(_n_splits):
                    COLUMN_CHECK += [f'split{split}_train_{suffix}']
                COLUMN_CHECK += [f'mean_train_{suffix}']
                COLUMN_CHECK += [f'std_train_{suffix}']

        # END BUILD VERIFICATION STUFF ** * ** * ** * ** * ** * ** * ** * ** *
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # RUN cv_results_builder AND GET CHARACTERISTICS ######################
        cv_results_output, PARAM_GRID_KEY = _cv_results_builder(
            _param_grid=good_param_grid,
            _n_splits=_n_splits,
            _scorer=_scoring,
            _return_train_score=return_train
        )

        OUTPUT_COLUMNS = list(cv_results_output.keys())
        OUTPUT_LEN = len(cv_results_output['mean_fit_time'])
        # RUN cv_results_builder AND GET CHARACTERISTICS ######################

        # COMPARE OUTPUT TO CONTROLS ##########################################
        for out_col in OUTPUT_COLUMNS:
            assert out_col in COLUMN_CHECK, \
                (f"{out_col} is in OUTPUT_COLUMNS but not in COLUMN_CHECK")

        for check_col in COLUMN_CHECK:
            assert check_col in OUTPUT_COLUMNS, \
                (f"{check_col} is in COLUMN_CHECK but not in OUTPUT_COLUMNS")

        assert OUTPUT_LEN == correct_cv_results_len, \
            (f"output rows ({OUTPUT_LEN}) does not equal expected "
             f"rows ({correct_cv_results_len})")


        assert isinstance(PARAM_GRID_KEY, np.ndarray)
        assert all(
            map(isinstance, PARAM_GRID_KEY, (np.uint8 for _ in PARAM_GRID_KEY))
        )
        assert len(PARAM_GRID_KEY) == OUTPUT_LEN

        # COMPARE OUTPUT TO CONTROLS ##########################################


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits':3,
            '_n_rows':200,
            '_scorer_names':['precision', 'recall', 'accuracy', 'balanced_accuracy'],
            '_grids': [{'param_1':[1,2,3], 'param_2':[True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': False
        }],
        indirect=True
    )
    def test_builder_against_template_1(
        self, _cv_results_template, standard_WIP_scorer
    ):

        template_pd = pd.DataFrame(_cv_results_template)

        cv_results_output, _ = _cv_results_builder(
            _param_grid=[{'param_1':[1,2,3], 'param_2':[True, False]}],
            _n_splits=3,
            _scorer=standard_WIP_scorer,
            _return_train_score=True
        )

        del _

        cv_results_pd = pd.DataFrame(cv_results_output)

        assert len(cv_results_pd.columns)== len(template_pd.columns)

        assert np.array_equiv(
            sorted(cv_results_pd.columns), sorted(template_pd.columns)
        )


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 5,
            '_n_rows': 271,
            '_scorer_names': ['precision', 'recall', 'accuracy', 'balanced_accuracy'],
            '_grids': [{'abc': [1, 2]}, {'xyz': ['a', 'b']}],
            '_return_train_score': False,
            '_fill_param_columns': False
        }],
        indirect = True
    )
    def test_builder_against_template_2(
        self, _cv_results_template, standard_WIP_scorer
    ):

        template_pd = pd.DataFrame(_cv_results_template)

        cv_results_output, _ = _cv_results_builder(
            _param_grid=[{'abc': [1, 2]}, {'xyz': ['a', 'b']}],
            _n_splits=5,
            _scorer=standard_WIP_scorer,
            _return_train_score=False
        )

        del _

        cv_results_pd = pd.DataFrame(cv_results_output)

        assert len(cv_results_pd.columns)== len(template_pd.columns)

        assert np.array_equiv(
            sorted(cv_results_pd.columns), sorted(template_pd.columns)
        )





