# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.model_selection.GSTCV._GSTCVMixin._validation._scoring import \
    master_scorer_dict

from pybear.model_selection.GSTCV._GSTCVMixin._fit._cv_results._cv_results_rank_update \
    import _cv_results_rank_update



class TestCVResultsRankUpdateTest:

    # the tested module should look for a 'rank' column for each scorer,
    # then rank the 'mean score' column for that scorer and put it in the
    # correct 'rank' column.

    # need to fill _cv_results_template with full 'params', then put dummy
    # scores into each trial and calculate the mean


    @staticmethod
    @pytest.fixture
    def scorers():
        return ['accuracy', 'balanced_accuracy', 'recall', 'f1']


    @pytest.mark.parametrize(
        '_cv_results_template',
        [{
            '_n_splits': 3,
            '_n_rows': 6,
            '_scorer_names': ['accuracy', 'balanced_accuracy', 'recall', 'f1'],
            '_grids': [{'param_1':[1,2,3], 'param_2':[True, False]}],
            '_return_train_score': True,
            '_fill_param_columns': True
        }],
        indirect=True
    )
    def test_accuracy(self, _cv_results_template, scorers):

        # v v v test column accuracy v v v ##############################

        # generate dummy scores, means, and stddevs ** * ** * ** * ** * **
        for scorer_suffix in scorers:

            _COLUMNS = []
            for _split in range(3):   # _n_splits
                _column = f'split{_split}_test_{scorer_suffix}'
                _COLUMNS.append(_column)
                _n_rows = len(_cv_results_template[_column])
                assert _column in _cv_results_template
                _cv_results_template[_column] = np.random.uniform(0,1,_n_rows)
            del _split, _column, _n_rows

            # fudge a tie score to test ranking for that case
            for _split in range(3):   # _n_splits
                for _idx in range(2):
                    _column = f'split{_split}_test_{scorer_suffix}'
                    _cv_results_template[_column][_idx] = 1

            assert f'mean_test_{scorer_suffix}' in _cv_results_template
            assert f'std_test_{scorer_suffix}' in _cv_results_template

            # for easier handling when getting mean and std
            __ = pd.DataFrame(_cv_results_template)

            _cv_results_template[f'mean_test_{scorer_suffix}'] = \
                __.loc[:, _COLUMNS].mean(axis=1)

            _cv_results_template[f'std_test_{scorer_suffix}'] = \
                __.loc[:, _COLUMNS].std(axis=1)

        del __


        # END generate dummy scores, means, and stddevs ** * ** * ** * **

        out = _cv_results_rank_update(
            _scorer={k:v for k,v in master_scorer_dict.items() if k in scorers},
            _cv_results=_cv_results_template
        )

        assert isinstance(out, dict)

        assert np.array_equiv(list(out.keys()), list(_cv_results_template.keys()))

        for scorer_suffix in scorers:

            assert f'mean_test_{scorer_suffix}' in out

            assert f'std_test_{scorer_suffix}' in out

            assert f'rank_test_{scorer_suffix}' in out

        # ^ ^ ^ test column accuracy ^ ^ ^ ##############################

        # v v v test value accuracy v v v ##############################

            og_col = out[f'mean_test_{scorer_suffix}']
            _means, _counts = np.unique(og_col, return_counts=True)
            _means = np.flip(_means)
            _counts = np.flip(_counts)

            rank_dict = dict((zip(_means, np.arange(1, len(_means) + 1))))

            offset = 0
            for idx, _ct in enumerate(_counts[1:], 1):
                offset += (_counts[idx - 1] - 1)
                rank_dict[_means[idx]] += offset

            rank = np.ma.masked_array(
                np.fromiter(map(lambda x: rank_dict[x], og_col),
                            dtype=np.uint16)
            )

            assert np.array_equiv(out[f'rank_test_{scorer_suffix}'], rank)

        # ^ ^ ^ test value accuracy ^ ^ ^ ##############################






