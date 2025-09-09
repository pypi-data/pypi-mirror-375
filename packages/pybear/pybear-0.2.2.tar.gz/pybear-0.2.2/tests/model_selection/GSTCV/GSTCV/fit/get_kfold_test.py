# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import inspect

import numpy as np

from pybear.model_selection.GSTCV._GSTCV._fit._get_kfold import _get_kfold



class TestSKGetKFold:

    # def _get_kfold(
    #     _X: SKXType,
    #     _y: SKYType,
    #     _n_splits: int,
    #     _verbose: int
    # ) -> Iterator[SKKFoldType]:

    # *** IMPORTANT!!!
    # This function can be called multiple times within a single param
    # grid permutation, first to fit, again to get test score, then again
    # if return_train_score. Therefore, it must return the same indices
    # for each call. The only things that should cause indices to be
    # different are n_splits and the number of rows in X.
    # Since this is stratified KFold and examples are pulled based on the
    # distribution of y, set random_state state to a constant.


    @pytest.mark.parametrize('_junk_X',
        (-2.7, -1, 0, 1, 2.7, None, 'str', lambda x:x)
    )
    @pytest.mark.parametrize('_junk_y',
        (-2.7, -1, 0, 1, 2.7, None, 'str', lambda x:x)
    )
    def test_X_y_rejects_junk(self, _junk_X, _junk_y):

        # this is raised by sklearn StratifiedKFold let it raise whatever
        with pytest.raises(Exception):
            list(_get_kfold(
                _junk_X,
                _junk_y,
                _n_splits=3,
                _verbose=0
            ))


    @pytest.mark.parametrize(f'junk_n_splits',
        (-1, 0, 1, 3.14, True, min, 'junk', [0, 1], (0, 1), {0, 1},
         {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_n_splits(self, X_np, y_np, junk_n_splits):
        with pytest.raises(AssertionError):
            _get_kfold(
                X_np,
                y_np,
                _n_splits=junk_n_splits,
                _verbose=0
            )


    @pytest.mark.parametrize(f'junk_verbose',
        (-1, min, 'junk', [0, 1], (0, 1), {0, 1}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_verbose(self, X_np, y_np, junk_verbose):
        with pytest.raises(AssertionError):
            _get_kfold(
                X_np,
                y_np,
                _n_splits=3,
                _verbose=junk_verbose
            )

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_X_dim', (1, 2))
    @pytest.mark.parametrize('_X_format',
        ('py_list', 'py_tup', 'py_set', 'np', 'pd', 'ss', 'pl')
    )
    @pytest.mark.parametrize('_y_dim', (1, 2))
    @pytest.mark.parametrize('_y_format',
        ('py_list', 'py_tup', 'py_set', 'np', 'pd', 'pl')   # no ss!
    )
    def test_np_returns_gen_of_nps(
        self, X_np, y_np, _format_helper, _X_format, _y_format,
        _X_dim, _y_dim
    ):

        if _X_dim == 2 and _X_format == 'py_set':
            pytest.skip(reason=f"cant have 2D set")
        if _y_dim == 2 and _y_format == 'py_set':
            pytest.skip(reason=f"cant have 2D set")
        if _X_dim == 1 and _X_format == 'ss':
            pytest.skip(reason=f"cant have 1D scipy sparse")
        if _X_format == 'py_set':
            pytest.skip(reason=f"sklearn.StratifedKFold cant take set for X")
        if _y_format == 'py_set':
            pytest.skip(reason=f"sklearn.StratifedKFold cant take set for y")
        # END skip impossible conditions ** * ** * ** * ** * ** * ** *

        _X = _format_helper(X_np, _X_format, _X_dim)
        _y = _format_helper(y_np, _y_format, _y_dim)


        out1 = _get_kfold(
            _X,
            _y,
            _n_splits=3,
            _verbose=0,
        )

        assert inspect.isgenerator(out1)

        out1_list = list(out1)

        for (train_idxs, test_idxs) in out1:

            assert isinstance(train_idxs, np.ndarray)
            assert isinstance(test_idxs, np.ndarray)

            assert train_idxs.min() >= 0
            assert train_idxs.max() < X_np.shape[0]

            assert test_idxs.min() >= 0
            assert test_idxs.max() < X_np.shape[0]


        # and second call returns same as the first
        out2 = _get_kfold(
            _X,
            _y,
            _n_splits=3,
            _verbose=0
        )


        for idx, (train_idxs2, test_idxs2) in enumerate(out2):

            assert isinstance(train_idxs2, np.ndarray)
            assert isinstance(test_idxs2, np.ndarray)

            assert train_idxs2.min() >= 0
            assert train_idxs2.max() < X_np.shape[0]

            assert test_idxs2.min() >= 0
            assert test_idxs2.max() < X_np.shape[0]

            assert np.array_equiv(out1_list[idx][0], train_idxs2)
            assert np.array_equiv(out1_list[idx][1], test_idxs2)




