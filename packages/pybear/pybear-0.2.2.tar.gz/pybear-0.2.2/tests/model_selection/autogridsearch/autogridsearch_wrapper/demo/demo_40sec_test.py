# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np



class TestDemo:

    # prove out it does correct passes wrt total_passes/shifts/tpih
    # tests RESULTS_ & GRIDS_
    # shift_ctr


    @pytest.mark.parametrize('_space, _gap',
        (
            ('linspace', 'na'),
            ('logspace', 1.0),
            ('logspace', 2.0),
        )
    )
    @pytest.mark.parametrize('_type', ('fixed', 'soft', 'hard'))
    @pytest.mark.parametrize('_univ_min_bound', (True, False))
    @pytest.mark.parametrize('_points', (3, 4))
    @pytest.mark.parametrize('_total_passes', (2, 5))
    @pytest.mark.parametrize('_shrink_pass', (2, 3, 1_000_000))
    @pytest.mark.parametrize('_max_shifts', (1, 3))
    @pytest.mark.parametrize(f'_tpih', (True, False))
    @pytest.mark.parametrize('_pass_best', (True, False))
    def test_sklearn(
        self, _space, _gap, _type, _univ_min_bound, _points, _total_passes,
        _shrink_pass, _max_shifts, _tpih, _pass_best, sk_estimator_2,
        SKAutoGridSearch
    ):

        _POINTS = [_points for _ in range(_total_passes)]
        _POINTS[_shrink_pass-1:] = [1 for _ in _POINTS[_shrink_pass-1:]]
        _BIN_POINTS = [2 for _ in range(_total_passes)]
        _BIN_POINTS[_shrink_pass - 1:] = [1 for _ in _BIN_POINTS[_shrink_pass - 1:]]

        # the empty grids are overwritten later
        _params = {
            'alpha': [[], _POINTS, _type + '_float'],
            'fit_intercept': [[True, False], _BIN_POINTS, 'fixed_bool'],
            'max_iter': [[], _POINTS, _type + '_integer'],
            'solver': [['lbfgs', 'saga'], _BIN_POINTS, 'fixed_string']
        }

        del _POINTS, _BIN_POINTS

        # build first grids ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # make lin univ min bound and log gap 1, then adjust as needed
        _alpha_lin_range = np.linspace(0, 10_000 * (_points - 1), _points)
        _alpha_log_range = np.linspace(0, _points - 1, _points)
        _max_iter_lin_range = np.linspace(1, 1_001 * (_points - 1), _points)
        _max_iter_log_range = np.linspace(0, _points - 1, _points)

        if _univ_min_bound:
            pass
        elif not _univ_min_bound:
            _alpha_lin_range += 10_000
            _max_iter_lin_range += 999
            _max_iter_log_range += 1

        if _gap == 2:
            _alpha_log_range *= 2
            _max_iter_log_range *= 2

        if _space == 'linspace':
            _alpha_grid = _alpha_lin_range
            _max_iter_grid = _max_iter_lin_range
        elif _space == 'logspace':
            _alpha_grid = np.power(10, _alpha_log_range)
            _max_iter_grid = np.power(10, _alpha_log_range)
        else:
            raise Exception

        _params['alpha'][0] = list(map(float, _alpha_grid))

        _params['max_iter'][0] = list(map(int, _max_iter_grid))

        # END build first grids ** * ** * ** * ** * ** * ** * ** * ** *


        test_cls = SKAutoGridSearch(
            sk_estimator_2,
            params=_params,
            total_passes=_total_passes,
            total_passes_is_hard=_tpih,
            max_shifts=_max_shifts
        )

        # build _true_best_params ** * ** * ** * ** * ** * ** * ** * **
        # arbitrary values in _true_best_params ** * ** * ** * ** * ** *
        __ = {}

        if _type == 'soft':
            __['alpha'] = 53_827
        elif _type == 'hard':
            x =  _params['alpha'][0]
            __['alpha'] = float(np.mean((x[-2], x[-1])))
            del x
        elif _type == 'fixed':
            __['alpha'] = _params['alpha'][0][-2]
        else:
            raise Exception

        __['fit_intercept'] = True

        if _type == 'soft':
            __['max_iter'] = 8_607
        elif _type == 'hard':
            x =  _params['max_iter'][0]
            __['max_iter'] = float(np.floor(np.mean((x[-2], x[-1]))))
            del x
        elif _type == 'fixed':
            __['max_iter'] = _params['max_iter'][0][-2]
        else:
            raise Exception

        __['solver'] = np.random.choice(_params['solver'][0], 1)[0]

        _true_best_params = __
        # END arbitrary values in _true_best_params ** * ** * ** * ** *

        _test_cls = test_cls.demo(
            true_best_params=_true_best_params if _pass_best else None,
            mock_gscv_pause_time=0
        )

        del test_cls

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # 'params'
        assert _test_cls.params.keys() == _params.keys()
        for _param in _params:
            assert _test_cls.params[_param][0] == _params[_param][0]
            if _params[_param][-1] in ['fixed_string', 'fixed_bool']:
                assert _test_cls.params[_param][2] == _params[_param][2]
            else:
                assert len(_test_cls.params[_param][0]) == \
                    _test_cls.params[_param][1][0]
                assert len(_test_cls.params[_param][1]) == _test_cls.total_passes

        del _param

        # 'total_passes'
        assert _test_cls.total_passes >= _total_passes

        # 'total_passes_is_hard'
        assert _test_cls.total_passes_is_hard == _tpih

        # 'max_shifts'
        assert _test_cls.max_shifts == _max_shifts

        # 'GRIDS_'
        assert list(_test_cls.GRIDS_.keys()) == list(range(_test_cls.total_passes))
        for _pass_ in _test_cls.GRIDS_:

            assert _test_cls.GRIDS_[_pass_].keys() == _params.keys()
            assert all(map(
                isinstance,
                _test_cls.GRIDS_[_pass_].values(),
                (list for _ in _test_cls.GRIDS_[_pass_])
            ))

            for _param_ in _params:
                __ = _test_cls.GRIDS_[_pass_][_param_]
                assert len(__) == _test_cls.params[_param_][1][_pass_]
            del _param_, __
        del _pass_

        # 'RESULTS_'
        assert list(_test_cls.RESULTS_.keys()) == list(range(_test_cls.total_passes))
        for _pass_ in _test_cls.RESULTS_:
            assert _test_cls.RESULTS_[_pass_].keys() == _params.keys()
            assert all(
                map(
                    isinstance,
                    _test_cls.RESULTS_[_pass_].values(),
                    ((int, float, bool, str) for _ in _test_cls.RESULTS_[_pass_])
                )
            )
        del _pass_

        _last_param_grid = _test_cls.GRIDS_[max(_test_cls.GRIDS_.keys())]
        _last_best = _test_cls.RESULTS_[max(_test_cls.RESULTS_.keys())]
        for _param in _params:
            _last_grid = _last_param_grid[_param]
            if 'fixed' in _params[_param][-1]:
                assert _last_best[_param] in _params[_param][0]
                assert _last_best[_param] in _last_grid
                # remember demo has 10% chance that these could be non-best
                # if _pass_best:
                #     assert _true_best_params[_param] in _last_grid
                #     assert _last_best[_param] == _true_best_params[_param]
            else:
                # when shifting these, both may not be true
                 assert _true_best_params[_param] >= min(_last_grid) or \
                            _true_best_params[_param] <= max(_last_grid)

        del _last_param_grid, _last_best, _param, _last_grid










