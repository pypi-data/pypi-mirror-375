# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._param_grid \
    import _cond_param_grid



class TestCondParamGrid:

    # def _cond_param_grid(
    #     _param_grid: ParamGridInputType | ParamGridsInputType,
    #     _thresholds: ThresholdsInputType    # this is init self.thresholds
    # ) -> ParamGridsWIPType:


    @staticmethod
    @pytest.fixture
    def good_param_grid():
        return [
            {'thresholds': np.linspace(0,1,11), 'solver':['saga', 'lbfgs']},
            {'solver': ['saga', 'lbfgs'], 'C': np.logspace(-5,5,11)},
            {'thresholds': [0.25], 'solver': ['saga', 'lbfgs'], 'C': [100, 1000]}
        ]



    # param_grid ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    def test_accepts_good_param_grids(self, good_param_grid, standard_thresholds):

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _og_gpg = deepcopy(good_param_grid)
        _og_threshes = deepcopy(standard_thresholds)
        out = _cond_param_grid(good_param_grid, standard_thresholds)
        assert isinstance(out, list)
        assert len(out) == len(good_param_grid)
        assert all(map(isinstance, out, (dict for i in out)))
        for idx in range(len(_og_gpg)):
            for key in _og_gpg[idx]:
                assert np.array_equal(good_param_grid[idx][key], _og_gpg[idx][key])
        assert np.array_equal(standard_thresholds, _og_threshes)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _gpg = [good_param_grid[0]]
        _og_gpg = deepcopy(_gpg)
        _og_threshes = deepcopy(standard_thresholds)
        out = _cond_param_grid(_gpg, standard_thresholds)
        assert isinstance(out, list)
        assert len(out) == 1
        # verify thresholds passed via param grid supersede thresholds passed
        # via kwarg
        assert np.array_equiv(
            out[0]['thresholds'],
            # the thresholds in good_param_grid[0]
            list(map(float, np.linspace(0,1,11)))
        )
        for key in _gpg[0]:
            assert np.array_equal(_gpg[0][key], _og_gpg[0][key])
        assert np.array_equal(standard_thresholds, _og_threshes)
        # that means the param_grid threshs were not overwritten by init threshs

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _gpg = [good_param_grid[0], good_param_grid[1]]
        _og_gpg = deepcopy(_gpg)
        _og_threshes = deepcopy(standard_thresholds)
        out = _cond_param_grid(_gpg, standard_thresholds)
        assert isinstance(out, list)
        assert all(map(isinstance, out, (dict for i in out)))
        # verify thresholds passed via param grid supersede thresholds passed
        # via kwarg (which would land in the first position in the function)
        assert np.array_equiv(
            _gpg[0]['thresholds'],
            # the thresholds in good_param_grid[0]
            list(map(float, np.linspace(0,1,11)))
        )
        # grid #2 doesnt have thresholds passed, so should be the default
        assert np.array_equiv(
            out[1]['thresholds'],
            standard_thresholds
        )
        for idx in range(len(_og_gpg)):
            for key in _og_gpg[idx]:
                assert np.array_equal(_gpg[idx][key], _og_gpg[idx][key])
        assert np.array_equal(standard_thresholds, _og_threshes)
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('valid_empties', ({}, [], [{}], [{}, {}]))
    def test_accepts_valid_empties(self, valid_empties):

        _og_valid_empties = deepcopy(valid_empties)
        _thresholds = {0, 0.25, 0.5, 0.75, 1}
        _og_thresholds = deepcopy(_thresholds)
        out = _cond_param_grid(valid_empties, _thresholds)
        assert isinstance(out, list)
        # remember validation always returns a list of dicts
        for _grid in out:
            assert len(_grid) == 1
            assert 'thresholds' in _grid
            assert isinstance(_grid['thresholds'], list)
            assert np.array_equiv(
                _grid['thresholds'],
                sorted(list(_thresholds))
            )
        assert valid_empties == _og_valid_empties
        assert _thresholds == _og_thresholds
    # END param_grid ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



    # _thresholds ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('_good_thresh',
        (0, 0.5, 1, [0, 0.1, 0.2], (0.8, 0.9, 1.0), None)
    )
    def test_accepts_good_thresh(self, good_param_grid, _good_thresh):

        _gpg = good_param_grid
        _og_gpg = deepcopy(_gpg)
        _og_good_thresh = deepcopy(_good_thresh)

        out = _cond_param_grid(_gpg, _good_thresh)
        assert isinstance(out, list)
        assert all(map(isinstance, _gpg, (dict for i in _gpg)))

        for idx in range(len(_og_gpg)):
            for key in _og_gpg[idx]:
                assert np.array_equal(good_param_grid[idx][key], _og_gpg[idx][key])
        assert np.array_equal(_good_thresh, _og_good_thresh)

    # END _thresholds ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # if param_grid had valid thresholds in it, it comes out the same as
    # it went in, regardless of what is passed to threshold kwarg (dicts 1 & 3)

    # if param_grid was not passed, but thresholds was, should be a param
    # grid with only the thresholds in it

    # if both param_grid and thresholds were not passed, should be one
    # param grid with default thresholds

    # if param_grid was passed and did not have thresholds, should be the
    # same except have init thresholds in it. If thresholds was not
    # passed, GSTCV default thresholds should be in it. (dict 2)

    # * * * *


    # conditionals between param_grid and thresholds ** * ** * ** * ** *

    def test_accuracy_1(self, good_param_grid, standard_thresholds):

        # if param_grid had valid thresholds in it, it comes out the same as
        # it went in, regardless of what is passed to threshold kwarg
        # (dicts 1 & 3)

        _gpg = good_param_grid[0]
        _og_gpg = deepcopy(_gpg)
        _threshes = np.linspace(0,1,5)
        _og_threshes = deepcopy(_threshes)

        out = _cond_param_grid(_gpg, _threshes)

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], dict)
        assert np.array_equiv(out[0].keys(), good_param_grid[0].keys())
        for k, v in out[0].items():
            assert np.array_equiv(out[0][k], good_param_grid[0][k])
        # thresholds passed via param grid supersede those passed via kwarg
        assert np.array_equiv(out[0]['thresholds'], np.linspace(0,1,11))
        for key in _og_gpg:
            assert np.array_equal(_gpg[key], _og_gpg[key])
        assert np.array_equal(_threshes, _og_threshes)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _gpg = good_param_grid[2]
        _og_gpg = deepcopy(_gpg)
        _threshes = standard_thresholds
        _og_threshes = deepcopy(_threshes)

        out = _cond_param_grid(_gpg, _threshes)

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], dict)
        assert np.array_equiv(out[0].keys(), good_param_grid[2].keys())
        for k, v in out[0].items():
            assert np.array_equiv(out[0][k], good_param_grid[2][k])
        assert np.array_equiv(out[0]['thresholds'], [0.25])
        assert _gpg == _og_gpg
        assert np.array_equal(_threshes, _og_threshes)


    def test_accuracy_2(self):

        # if param_grid was not passed, but thresholds was, should be a param
        # grid with only the thresholds in it

        # notice testing pass as set
        _gpg = []
        _og_gpg = deepcopy(_gpg)
        _threshes = {0, 0.25, 0.5, 0.75, 1}
        _og_threshes = deepcopy(_threshes)
        out = _cond_param_grid(_gpg, _threshes)

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], dict)
        assert np.array_equiv(list(out[0].keys()), ['thresholds'])
        assert np.array_equiv(out[0]['thresholds'], np.linspace(0,1,5))
        assert _gpg == _og_gpg
        assert _threshes == _og_threshes

        # notice testing pass as list
        _gpg = {}
        _og_gpg = deepcopy(_gpg)
        _threshes = [0, 0.25, 0.5, 0.75, 1]
        _og_threshes = deepcopy(_threshes)
        out = _cond_param_grid(_gpg, _threshes)

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], dict)
        assert np.array_equiv(list(out[0].keys()), ['thresholds'])
        assert np.array_equiv(out[0]['thresholds'], np.linspace(0,1,5))
        assert _gpg == _og_gpg
        assert _threshes == _og_threshes


    def test_accuracy_3(self, standard_thresholds):

        # if both param_grid and thresholds were not passed, should be one
        # param grid with default thresholds

        _gpg = []
        _og_gpg = deepcopy(_gpg)
        _threshes = None
        _og_threshes = deepcopy(_threshes)

        out = _cond_param_grid(_gpg, _threshes)

        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], dict)
        assert np.array_equiv(list(out[0].keys()), ['thresholds'])
        assert np.array_equiv(out[0]['thresholds'], np.linspace(0, 1, 21))
        assert _gpg == _og_gpg
        assert _threshes == _og_threshes


    def test_accuracy_4(self, good_param_grid, standard_thresholds):

        # if param_grid was passed and did not have thresholds, should be the
        # same except have given thresholds in it. If thresholds was not
        # passed, default thresholds should be in it. (dict 2)

        _og_gpg = deepcopy(good_param_grid)
        # notice testing pass as set
        _threshes = {0, 0.25, 0.5, 0.75, 1}
        _og_threshes = deepcopy(_threshes)
        out = _cond_param_grid(good_param_grid, _threshes)

        assert isinstance(out, list)
        assert len(out) == 3
        for _idx, _param_grid in enumerate(out):
            assert isinstance(out[_idx], dict)
            if _idx == 1:
                assert np.array_equiv(
                    list(out[_idx].keys()),
                    list(good_param_grid[_idx].keys()) + ['thresholds']
                )
                for k,v in out[_idx].items():
                    if k == 'thresholds':
                        assert np.array_equiv(out[_idx][k], np.linspace(0,1,5))
                    else:
                        assert np.array_equiv(v, good_param_grid[1][k])
            else:
                assert np.array_equiv(
                    list(out[_idx].keys()),
                    list(good_param_grid[_idx].keys())
                )
                for k,v in out[_idx].items():
                    assert np.array_equiv(v, good_param_grid[_idx][k])

        for idx in range(len(_og_gpg)):
            for key in _og_gpg[idx]:
                assert np.array_equal(good_param_grid[idx][key], _og_gpg[idx][key])
        assert np.array_equal(_threshes, _og_threshes)

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        _og_gpg = deepcopy(good_param_grid)
        _threshes = None
        _og_threshes = deepcopy(_threshes)

        out = _cond_param_grid(good_param_grid, _threshes)

        assert isinstance(out, list)
        assert len(out) == 3
        for _idx, _param_grid in enumerate(out):
            assert isinstance(out[_idx], dict)
            if _idx == 1:
                assert np.array_equiv(
                    list(out[_idx].keys()),
                    list(good_param_grid[_idx].keys()) + ['thresholds']
                )
                for k,v in out[_idx].items():
                    if k == 'thresholds':
                        assert np.array_equiv(out[_idx][k], np.linspace(0, 1, 21))
                    else:
                        assert np.array_equiv(v, good_param_grid[_idx][k])
            else:
                assert np.array_equiv(
                    list(out[_idx].keys()),
                    list(good_param_grid[_idx].keys())
                )
                for k,v in out[_idx].items():
                    assert np.array_equiv(v, good_param_grid[_idx][k])

        for idx in range(len(_og_gpg)):
            for key in _og_gpg[idx]:
                assert np.array_equal(good_param_grid[idx][key], _og_gpg[idx][key])
        assert _threshes == _og_threshes






