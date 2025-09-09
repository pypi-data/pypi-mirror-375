# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.metrics import accuracy_score, balanced_accuracy_score

from sklearn.model_selection import ParameterGrid

from pybear.model_selection.GSTCV._GSTCVMixin._fit._cv_results._cv_results_update \
    import _cv_results_update



class TestCVResultsUpdate:

    # def _cv_results_update(
    #     _trial_idx: int,
    #     _THRESHOLDS: ThresholdsWIPType,
    #     _FOLD_FIT_TIMES_VECTOR: MaskedHolderType,
    #     _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME: MaskedHolderType,
    #     _TEST_BEST_THRESH_IDXS_BY_SCORER: MaskedHolderType,
    #     _TEST_FOLD_x_SCORER__SCORE: MaskedHolderType,
    #     _TRAIN_FOLD_x_SCORER__SCORE: MaskedHolderType,
    #     _scorer: ScorerWIPType,
    #     _cv_results: CVResultsType,
    #     _return_train_score: bool
    # ) -> CVResultsType:

    # test correct row of cv_results gets filled with thresholds,
    # scores, and times, but not ranks. (Ranks must be done after
    # cv_results is full.)

    # 'mean_fit_time'
    # 'std_fit_time'
    # 'mean_score_time'
    # 'std_score_time'
    # 'param_param_1'
    # 'param_param_2'
    # 'params'
    # 'best_threshold_accuracy'
    # 'split0_test_accuracy'
    # 'split1_test_accuracy'
    # 'mean_test_accuracy'
    # 'std_test_accuracy'
    # 'rank_test_accuracy'
    # 'split0_train_accuracy'
    # 'split1_train_accuracy'
    # 'mean_train_accuracy'
    # 'std_train_accuracy'
    # 'best_threshold_balanced_accuracy'
    # 'split0_test_balanced_accuracy'
    # 'split1_test_balanced_accuracy'
    # 'mean_test_balanced_accuracy'
    # 'std_test_balanced_accuracy'
    # 'rank_test_balanced_accuracy'
    # 'split0_train_balanced_accuracy'
    # 'split1_train_balanced_accuracy'
    # 'mean_train_balanced_accuracy'
    # 'std_train_balanced_accuracy'


    @staticmethod
    @pytest.fixture(scope='module')
    def _make_holder():
        """Helper for making random masked array holder objects."""
        return lambda low, high, shape: np.ma.masked_array(
            np.random.uniform(low, high, shape), dtype=np.float64
        )


    @pytest.mark.parametrize('_n_splits', (3,))
    @pytest.mark.parametrize('_trial_idx', (0,))
    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 3,
            '_n_rows': 6,
            '_scorer_names': ['accuracy', 'balanced_accuracy'],
            '_grids': [{'param_1': [1, 2, 3], 'param_2': [True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': True
        }],
        indirect=True
    )
    def test_accuracy_1(
        self, _cv_results_template, _trial_idx, _n_splits, _make_holder
    ):

        # 2 scorers, 1 param grid

        _thresholds = 11
        _n_scorers = 2

        _THRESHOLDS = np.linspace(0, 1, _thresholds).tolist()
        _FOLD_FIT_TIMES_VECTOR = _make_holder(5, 20, (_n_splits,))
        _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME = \
            _make_holder(0, 2, (_n_splits, _thresholds, _n_scorers))
        _TEST_BEST_THRESHOLD_IDXS_BY_SCORER = \
            np.ma.masked_array(
                np.random.randint(0, _thresholds, (_n_scorers,)),
                dtype=np.uint16
            )
        _TEST_FOLD_x_SCORER__SCORE = _make_holder(0, 1, (_n_splits, _n_scorers))
        _TRAIN_FOLD_x_SCORER__SCORE = _make_holder(0, 1, (_n_splits, _n_scorers))

        _scorers = {
            'accuracy': accuracy_score,
            'balanced_accuracy': balanced_accuracy_score
        }
        _return_train_score = True

        out = _cv_results_update(
            _trial_idx,
            _THRESHOLDS,
            _FOLD_FIT_TIMES_VECTOR,
            _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME,
            _TEST_BEST_THRESHOLD_IDXS_BY_SCORER,
            _TEST_FOLD_x_SCORER__SCORE,
            _TRAIN_FOLD_x_SCORER__SCORE,
            _scorers,
            _cv_results_template,
            _return_train_score
        )

        assert isinstance(out, dict)

        # check correct columns ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        _ct_columns = 0
        for _column in ['mean_fit_time', 'std_fit_time', 'mean_score_time',
                        'std_score_time', 'params']:
            assert _column in out

        _ct_columns += 5

        assert 'param_param_1' in out
        assert 'param_param_2' in out

        _ct_columns += 2

        for _scorer in _scorers:

            assert f'best_threshold_{_scorer}' in out
            _ct_columns += 1

            assert f'rank_test_{_scorer}' in out
            _ct_columns += 1

            for _type in ['train', 'test']:
                assert f'mean_{_type}_{_scorer}' in out
                assert f'std_{_type}_{_scorer}' in out
                _ct_columns += 2

                for _split in range(3):   # _n_splits
                    assert f'split{_split}_{_type}_{_scorer}' in out
                _ct_columns += 3

        assert len(out) == _ct_columns
        del _ct_columns
        # end check correct columns ** * ** * ** * ** * ** * ** * ** * ** * **


        # check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        ref_permuter = ParameterGrid(
            [{'param_1': [1, 2, 3], 'param_2': [True, False]}]
        )

        assert out['mean_fit_time'][_trial_idx] == np.mean(_FOLD_FIT_TIMES_VECTOR)
        assert out['std_fit_time'][_trial_idx] == np.std(_FOLD_FIT_TIMES_VECTOR)

        assert out['mean_score_time'][_trial_idx] == \
               np.mean(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)
        assert out['std_score_time'][_trial_idx] == \
               np.std(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)

        assert np.array_equiv(out['params'], ref_permuter)
        assert out['param_param_1'][_trial_idx] == \
               [ref_permuter[_trial_idx]['param_1']]
        assert out['param_param_2'][_trial_idx] == \
               [ref_permuter[_trial_idx]['param_2']]

        for _s_idx, _scorer in enumerate(_scorers):

            assert out[f'best_threshold_{_scorer}'][_trial_idx] == \
                _THRESHOLDS[int(_TEST_BEST_THRESHOLD_IDXS_BY_SCORER[_s_idx])]

            # _TEST_FOLD_x_SCORER__SCORE,
            # _TRAIN_FOLD_x_SCORER__SCORE,
            assert out[f'mean_test_{_scorer}'][_trial_idx] == \
                   np.mean(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_test_{_scorer}'][_trial_idx] == \
                   np.std(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'mean_train_{_scorer}'][_trial_idx] == \
                   np.mean(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_train_{_scorer}'][_trial_idx] == \
                   np.std(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])

            for _split in range(3):   # _n_splits
                assert out[f'split{_split}_test_{_scorer}'][_trial_idx] == \
                   _TEST_FOLD_x_SCORER__SCORE[_split, _s_idx]

            for _split in range(3):   # _n_splits
                assert out[f'split{_split}_train_{_scorer}'][_trial_idx] == \
                   _TRAIN_FOLD_x_SCORER__SCORE[_split, _s_idx]


        # cant test rank!

        # end check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('_n_splits', (5,))
    @pytest.mark.parametrize('_trial_idx', (5,))
    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 5,
            '_n_rows': 6,
            '_scorer_names': ['balanced_accuracy'],
            '_grids': [{'param_1': [1, 2, 3]}, {'param_1': [4, 5, 6]}],
            '_return_train_score': True,
            '_fill_param_columns': True
        }],
        indirect=True
    )
    def test_accuracy_2(
        self, _cv_results_template, _trial_idx, _n_splits, _make_holder
    ):

        # 1 scorer, 2 param grids

        _thresholds = 21
        _n_scorers = 1

        _THRESHOLDS = np.linspace(0, 1, _thresholds)
        _FOLD_FIT_TIMES_VECTOR = _make_holder(50, 90, (_n_splits,))
        _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME = \
            _make_holder(1, 2, (_n_splits, _thresholds, _n_scorers))
        _TEST_BEST_THRESHOLD_IDXS_BY_SCORER = \
            np.ma.masked_array(
                np.random.randint(0, _thresholds, (_n_scorers,)),
                dtype=np.uint16
            )
        _TEST_FOLD_x_SCORER__SCORE = \
            _make_holder(0, 1, (_n_splits, _n_scorers))
        _TRAIN_FOLD_x_SCORER__SCORE = \
            _make_holder(0, 1, (_n_splits, _n_scorers))

        _scorers = {'balanced_accuracy': balanced_accuracy_score}
        _return_train_score = True

        out = _cv_results_update(
            _trial_idx,
            _THRESHOLDS,
            _FOLD_FIT_TIMES_VECTOR,
            _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME,
            _TEST_BEST_THRESHOLD_IDXS_BY_SCORER,
            _TEST_FOLD_x_SCORER__SCORE,
            _TRAIN_FOLD_x_SCORER__SCORE,
            _scorers,
            _cv_results_template,
            _return_train_score
        )

        assert isinstance(out, dict)

        # check correct columns ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        _ct_columns = 0
        for _column in ['mean_fit_time', 'std_fit_time', 'mean_score_time',
                        'std_score_time', 'params']:
            assert _column in out

        _ct_columns += 5

        assert 'param_param_1' in out

        _ct_columns += 1

        for _scorer in _scorers:

            if len(_scorers) == 1:
                _scorer = 'score'

            assert f'best_threshold' in out
            _ct_columns += 1

            assert f'rank_test_{_scorer}' in out
            _ct_columns += 1

            for _type in ['train', 'test']:
                assert f'mean_{_type}_{_scorer}' in out
                assert f'std_{_type}_{_scorer}' in out
                _ct_columns += 2

                for _split in range(5):   # _n_splits
                    assert f'split{_split}_{_type}_{_scorer}' in out
                _ct_columns += 5

        assert len(out) == _ct_columns
        del _ct_columns
        # end check correct columns ** * ** * ** * ** * ** * ** * ** * ** * **


        # check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        ref_permuter = ParameterGrid(
            [{'param_1': [1, 2, 3]}, {'param_1': [4, 5, 6]}]
        )

        assert out['mean_fit_time'][_trial_idx] == np.mean(_FOLD_FIT_TIMES_VECTOR)
        assert out['std_fit_time'][_trial_idx] == np.std(_FOLD_FIT_TIMES_VECTOR)

        assert out['mean_score_time'][_trial_idx] == \
               np.mean(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)
        assert out['std_score_time'][_trial_idx] == \
               np.std(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)

        assert np.array_equiv(out['params'], ref_permuter)
        assert out['param_param_1'][_trial_idx] == \
               [ref_permuter[_trial_idx]['param_1']]

        for _s_idx, _scorer in enumerate(_scorers):

            if len(_scorers) == 1:
                _scorer = 'score'

            assert out[f'best_threshold'][_trial_idx] == \
                _THRESHOLDS[int(_TEST_BEST_THRESHOLD_IDXS_BY_SCORER[_s_idx])]

            assert out[f'mean_test_{_scorer}'][_trial_idx] == \
                   np.mean(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_test_{_scorer}'][_trial_idx] == \
                   np.std(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'mean_train_{_scorer}'][_trial_idx] == \
                   np.mean(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_train_{_scorer}'][_trial_idx] == \
                   np.std(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])

            for _split in range(5):   # _n_splits
                assert out[f'split{_split}_test_{_scorer}'][_trial_idx] == \
                   _TEST_FOLD_x_SCORER__SCORE[_split, _s_idx]

            for _split in range(5):   # _n_splits
                assert out[f'split{_split}_train_{_scorer}'][_trial_idx] == \
                   _TRAIN_FOLD_x_SCORER__SCORE[_split, _s_idx]


        # cant test rank!

        # end check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('_n_splits', (3,))
    @pytest.mark.parametrize('_trial_idx', (0,))
    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 3,
            '_n_rows': 6,
            '_scorer_names': ['accuracy', 'balanced_accuracy'],
            '_grids': [{'param_1': [1, 2, 3], 'param_2': [True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': True
        }],
        indirect=True
    )
    def test_accuracy_partial_mask(
            self, _cv_results_template, _trial_idx, _n_splits, _make_holder
    ):

        # 2 scorers, 1 param grid

        _thresholds = 11
        _n_scorers = 2

        _THRESHOLDS = np.ma.masked_array(np.linspace(0, 1, _thresholds))
        _THRESHOLDS[1] = np.ma.masked
        _FOLD_FIT_TIMES_VECTOR = _make_holder(5, 15, (_n_splits,))
        _FOLD_FIT_TIMES_VECTOR[1] = np.ma.masked
        _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME = \
            _make_holder(0, 2, (_n_splits, _thresholds, _n_scorers))
        _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME[1, :, :] = np.ma.masked
        # best threshold idx cannot be 1, 1 is masked to mock except during fit
        while True:
            _TEST_BEST_THRESHOLD_IDXS_BY_SCORER = \
                np.ma.masked_array(
                    np.random.randint(0, _thresholds, (_n_scorers,)),
                    dtype=np.uint16
                )
            if 1 not in _TEST_BEST_THRESHOLD_IDXS_BY_SCORER:
                break
        _TEST_FOLD_x_SCORER__SCORE = \
            _make_holder(0, 1, (_n_splits, _n_scorers))
        _TEST_FOLD_x_SCORER__SCORE[1, :] = np.ma.masked
        _TRAIN_FOLD_x_SCORER__SCORE = \
            _make_holder(0, 1, (_n_splits, _n_scorers))
        _TRAIN_FOLD_x_SCORER__SCORE[1, :] = np.ma.masked

        _scorers = {
            'accuracy': accuracy_score,
            'balanced_accuracy': balanced_accuracy_score
        }
        _return_train_score = True

        out = _cv_results_update(
            _trial_idx,
            _THRESHOLDS,
            _FOLD_FIT_TIMES_VECTOR,
            _TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME,
            _TEST_BEST_THRESHOLD_IDXS_BY_SCORER,
            _TEST_FOLD_x_SCORER__SCORE,
            _TRAIN_FOLD_x_SCORER__SCORE,
            _scorers,
            _cv_results_template,
            _return_train_score
        )

        assert isinstance(out, dict)

        # check correct columns ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        _ct_columns = 0
        for _column in ['mean_fit_time', 'std_fit_time', 'mean_score_time',
                        'std_score_time', 'params']:
            assert _column in out

        _ct_columns += 5

        assert 'param_param_1' in out
        assert 'param_param_2' in out

        _ct_columns += 2

        for _scorer in _scorers:

            assert f'best_threshold_{_scorer}' in out
            _ct_columns += 1

            assert f'rank_test_{_scorer}' in out
            _ct_columns += 1

            for _type in ['train', 'test']:
                assert f'mean_{_type}_{_scorer}' in out
                assert f'std_{_type}_{_scorer}' in out
                _ct_columns += 2

                for _split in range(3):   # _n_splits
                    assert f'split{_split}_{_type}_{_scorer}' in out
                _ct_columns += 3

        assert len(out) == _ct_columns
        del _ct_columns
        # end check correct columns ** * ** * ** * ** * ** * ** * ** * ** * **


        # check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        ref_permuter = ParameterGrid(
            [{'param_1': [1, 2, 3], 'param_2': [True, False]}]
        )

        assert out['mean_fit_time'][_trial_idx] == np.mean(_FOLD_FIT_TIMES_VECTOR)
        assert out['std_fit_time'][_trial_idx] == np.std(_FOLD_FIT_TIMES_VECTOR)

        assert out['mean_score_time'][_trial_idx] == \
               np.mean(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)
        assert out['std_score_time'][_trial_idx] == \
               np.std(_TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME)

        assert np.array_equiv(out['params'], ref_permuter)
        assert out['param_param_1'][_trial_idx] == \
               [ref_permuter[_trial_idx]['param_1']]
        assert out['param_param_2'][_trial_idx] == \
               [ref_permuter[_trial_idx]['param_2']]

        for _s_idx, _scorer in enumerate(_scorers):

            assert out[f'best_threshold_{_scorer}'][_trial_idx] == \
                _THRESHOLDS[int(_TEST_BEST_THRESHOLD_IDXS_BY_SCORER[_s_idx])]

            # _TEST_FOLD_x_SCORER__SCORE,
            # _TRAIN_FOLD_x_SCORER__SCORE,
            assert out[f'mean_test_{_scorer}'][_trial_idx] == \
                   np.mean(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_test_{_scorer}'][_trial_idx] == \
                   np.std(_TEST_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'mean_train_{_scorer}'][_trial_idx] == \
                   np.mean(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])
            assert out[f'std_train_{_scorer}'][_trial_idx] == \
                   np.std(_TRAIN_FOLD_x_SCORER__SCORE[:, _s_idx])

            for _split in [0,2]:   # _n_splits, but idx 1 is masked
                assert out[f'split{_split}_test_{_scorer}'][_trial_idx] == \
                   _TEST_FOLD_x_SCORER__SCORE[_split, _s_idx]

            for _split in [0,2]:   # _n_splits, but idx 1 is masked
                assert out[f'split{_split}_train_{_scorer}'][_trial_idx] == \
                   _TRAIN_FOLD_x_SCORER__SCORE[_split, _s_idx]


        # cant test rank!

        # end check accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



