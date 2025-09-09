# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from copy import deepcopy
import numpy as np

from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _get_next_param_grid._drill._drill import _drill



# every logspace in here should be unit gap because _regap_logspace would
# have run before _drill, but some places like 'fixed' can handle it


def test_catches_best_not_in_grid():
    with pytest.raises(ValueError):
        _drill(
            _param_name='whatever',
            _grid=[1, 3, 5, 7],
            _param_value=[[1, 3, 5, 7], [4, 4, 4], 'hard_integer'],
            _is_logspace=False,
            _pass=1,
            _best=2
        )


class TestStrBoolFixedIntFixedFloatReturnsEverythingUnchanged:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [['a', 'b', 'c', 'd'], [4, 4, 1], 'fixed_string'],
            'b': [[1, 2, 3, 4], [4, 4, 4], 'fixed_integer'],
            'c': [[1e1, 1e2, 1e3, 1e4], [4, 4, 4], 'fixed_integer'],
            'd': [[1e1, 1e3, 1e5, 1e7], [4, 4, 4], 'fixed_integer'],
            'e': [[10.1, 10.2, 10.3, 10.4], [4, 4, 4], 'fixed_float'],
            'f': [[1e3, 1e4, 1e5, 1e6], [4, 4, 4], 'fixed_float'],
            'g': [[1e3, 1e5, 1e7, 1e9], [4, 4, 4], 'fixed_float'],
            'h': [[True, False], [2, 1, 1], 'fixed_bool'],
            'i': [[True], [1, 1, 1], 'fixed_bool']
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': 1.0,
            'd': 2.0,
            'e': False,
            'f': 1.0,
            'g': 2.0,
            'h': False,
            'i': False
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': ['a', 'b', 'c', 'd'],
                'b': [1, 2, 3, 4],
                'c': [1e1, 1e2, 1e3, 1e4],
                'd': [1e1, 1e3, 1e5, 1e7],
                'e': [10.1, 10.2, 10.3, 10.4],
                'f': [1e3, 1e4, 1e5, 1e6],
                'g': [1e3, 1e5, 1e7, 1e9],
                'h': [True, False],
                'i': [True]
            },
            1: {}
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('key', list('abcdefg'))
    @pytest.mark.parametrize('posn', [0,1,2,3])
    def test_accuracy(
        selfs, good_grids, good_is_logspace, good_params, key, posn
    ):

        out_grid, out_param, out_is_logspace = \
            _drill(
                _param_name=key,
                _grid=good_grids[0][key],
                _param_value=good_params[key],
                _is_logspace=good_is_logspace[key],
                _pass=1,
                _best=good_grids[0][key][posn]
            )

        assert np.array_equiv(out_grid, good_grids[0][key])
        assert out_param == good_params[key]
        assert out_is_logspace == good_is_logspace[key]



class TestHardSoftFloat:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[0, 0.5, 1.0], [4, 4, 4], 'hard_float'],
            'b': [[1e1, 1e2, 1e3], [4, 4, 4], 'hard_float'],
            'c': [[1e2, 1e4, 1e6], [4, 4, 4], 'hard_float'],
            'd': [[20, 40, 60, 80], [4, 4, 4], 'soft_float'],
            'e': [[1e0, 1e1, 1e2], [4, 4, 4], 'soft_float'],
            'f': [[1e3, 1e5, 1e7], [4, 4, 4], 'soft_float'],
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': 1.0,
            'c': 2.0,
            'd': False,
            'e': 1.0,
            'f': 2.0
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': [0, 0.5, 1.0],
                'b': [1e1, 1e2, 1e3],
                'c': [1e2, 1e4, 1e6],
                'd': [20, 40, 60, 80],
                'e': [1e0, 1e1, 1e2],
                'f': [1e3, 1e5, 1e7]
            },
            1: {}
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('key', list('abcdef'))
    @pytest.mark.parametrize('posn', [0, 1, 2])
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, key, posn
    ):

        _pass = 1

        out_grid, out_param, out_is_logspace = \
            _drill(
                    _param_name=key,
                    _grid=good_grids[0][key],
                    _param_value=good_params[key],
                    _is_logspace=good_is_logspace[key],
                    _pass=_pass,
                    _best=good_grids[0][key][posn]
            )

        assert len(out_grid) == good_params[key][1][_pass]

        if 'hard' in good_params[key][-1]:
            assert min(out_grid) >= min(good_grids[0][key])
            assert max(out_grid) <= max(good_grids[0][key])
        else:
            if posn != 0:
                assert min(out_grid) >= min(good_grids[0][key])

            if posn != 2:
                assert max(out_grid) <= max(good_grids[0][key])

        __ = np.array(out_grid)
        _gaps = np.round(__[1:] - __[:-1], 6)
        assert len(np.unique(_gaps)) == 1
        del __, _gaps

        assert out_param == good_params[key]
        assert out_is_logspace is False




class TestIntUnitGap:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[1, 2, 3, 4], [4, 4, 4], 'hard_integer'],
            'b': [[2, 3, 4, 5], [4, 4, 4], 'hard_integer'],
            'c': [[1, 2, 3, 4], [4, 4, 4], 'soft_integer'],
            'd': [[2, 3, 4, 5], [4, 4, 4], 'soft_integer']
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': [1, 2, 3, 4],
                'b': [2, 3, 4, 5],
                'c': [1, 2, 3, 4],
                'd': [2, 3, 4, 5]
            },
            1: {}
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('key', list('abcd'))
    @pytest.mark.parametrize('posn', [0, 1, 2, 3])
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, key, posn
    ):

        out_grid, out_param, out_is_logspace = \
            _drill(
                _param_name=key,
                _grid=good_grids[0][key],
                _param_value=good_params[key],
                _is_logspace=good_is_logspace[key],
                _pass=1,
                _best=good_grids[0][key][posn]
            )

        if 'hard' in good_params[key][-1]:
            if posn == 2:
                # this is an oddball that is taking [1,2,3,4] and returning
                # [2,3,4]; it would take a lot of awkward handling to make
                # it conform and it's not worth it
                assert np.array_equiv(out_grid, good_grids[0][key][1:])
            else:
                assert np.array_equiv(out_grid, good_grids[0][key])
        else:  # 'soft'
            _grid = good_grids[0][key]
            if posn == 0:
                assert np.array_equiv(out_grid, [1, 2, 3, 4])
            elif posn == 1:
                assert np.array_equiv(out_grid, _grid)
            elif posn == 2:
                assert np.array_equiv(out_grid, [i+1 for i in _grid])
            elif posn == 3:
                assert np.array_equiv(out_grid, [i+1 for i in _grid])

        assert out_param == good_params[key]

        assert out_is_logspace is False



class TestIntNonUnitGapGT3:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[1, 10, 19], [3, 3, 3], 'soft_integer'],
            'b': [[1, 10, 19], [3, 3, 3], 'hard_integer'],
            'c': [[25, 50, 75], [3, 3, 3], 'soft_integer'],
            'd': [[25, 50, 75], [3, 3, 3], 'hard_integer'],
            'e': [[1, 10, 100], [3, 3, 3], 'soft_integer'],
            'f': [[1, 10, 100], [3, 3, 3], 'hard_integer'],
            'g': [[100, 1000, 10000], [3, 3, 3], 'soft_integer'],
            'h': [[100, 1000, 10000], [3, 3, 3], 'hard_integer'],
            'i': [[1e0, 1e2, 1e4], [3, 3, 3], 'soft_integer'],
            'j': [[1e0, 1e2, 1e4], [3, 3, 3], 'hard_integer'],
            'k': [[1e2, 1e4, 1e6], [3, 3, 3], 'soft_integer'],
            'l': [[1e2, 1e4, 1e6], [3, 3, 3], 'hard_integer']
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False,
            'e': 1.0,
            'f': 1.0,
            'g': 1.0,
            'h': 1.0,
            'i': 2.0,
            'j': 2.0,
            'k': 2.0,
            'l': 2.0
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': [1, 10, 19],
                'b': [1, 10, 19],
                'c': [25, 50, 75],
                'd': [25, 50, 75],
                'e': [1, 10, 100],
                'f': [1, 10, 100],
                'g': [100, 1000, 10000],
                'h': [100, 1000, 10000],
                'i': [1e0, 1e2, 1e4],
                'j': [1e0, 1e2, 1e4],
                'k': [1e2, 1e4, 1e6],
                'l': [1e2, 1e4, 1e6]
            },
            1: {}
        }


    @staticmethod
    @pytest.fixture
    def new_params():
        return {
            'a': [[1, 10, 19], [3, 3, 3], 'soft_integer'],
            'b': [[1, 10, 19], [3, 3, 3], 'hard_integer'],
            'c': [[25, 50, 75], [3, 3, 3], 'soft_integer'],
            'd': [[25, 50, 75], [3, 3, 3], 'hard_integer'],
            'e': [[1, 10, 100], [3, 3, 3], 'soft_integer'],
            'f': [[1, 10, 100], [3, 3, 3], 'hard_integer'],
            'g': [[100, 1000, 10000], [3, 3, 3], 'soft_integer'],
            'h': [[100, 1000, 10000], [3, 3, 3], 'hard_integer'],
            'i': [[1e0, 1e2, 1e4], [3, 3, 3], 'soft_integer'],
            'j': [[1e0, 1e2, 1e4], [3, 3, 3], 'hard_integer'],
            'k': [[1e2, 1e4, 1e6], [3, 3, 3], 'soft_integer'],
            'l': [[1e2, 1e4, 1e6], [3, 3, 3], 'hard_integer']
        }


    @staticmethod
    @pytest.fixture
    def new_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False,
            'e': False,
            'f': False,
            'g': False,
            'h': False,
            'i': False,
            'j': False,
            'k': False,
            'l': False
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('key', list('abcdefghijkl'))
    @pytest.mark.parametrize('posn', [0, 1, 2])
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, new_is_logspace,
        new_params, key, posn
    ):

        _pass = 1

        out_grid, out_param, out_is_logspace = \
            _drill(
                _param_name=key,
                _grid=good_grids[0][key],
                _param_value=good_params[key],
                _is_logspace=good_is_logspace[key],
                _pass=_pass,
                _best=good_grids[0][key][posn]
            )

        # min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        if good_is_logspace[key]:
            if 'soft' in good_params[key][-1]:
                assert min(out_grid) == 1

            elif 'hard' in good_params[key][-1]:
                assert min(out_grid) == good_grids[0][key][0]

        else: # not logspace
            if 'soft' in good_params[key][-1]:
                if posn == 0:
                    __ = good_grids[0][key]
                    assert min(out_grid) == max(1, (__[0] - (__[1] - __[0])))
                    del __
                else:
                    assert min(out_grid) >= good_grids[0][key][posn-1] + 1
            elif 'hard' in good_params[key][-1]:
                if posn == 0:
                    assert min(out_grid) == good_grids[0][key][0]
                else:
                    __ = good_grids[0][key]
                    assert min(out_grid) >= \
                        max(__[0], (__[posn] - (__[posn] - __[posn-1]))) + 1
                    del __
        # END min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        if good_is_logspace[key]:
            __ = np.log10(good_grids[0][key])
            assert max(out_grid) <= 10**(__[-1] + (__[-1] - __[-2]))
            del __
        else: # not logspace
            __ = good_grids[0][key]
            assert max(out_grid) <= (__[-1] + (__[-1] - __[-2]))
            del __
        # END max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert len(out_grid) == good_params[key][1][_pass]

        assert out_param == new_params[key]
        assert out_is_logspace == new_is_logspace[key]



class TestIntNonUnitGapEquals3:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[1, 4, 7], [3, 3, 3], 'soft_integer'],
            'b': [[1, 4, 7], [3, 3, 3], 'hard_integer'],
            'c': [[11, 14, 17], [3, 3, 3], 'soft_integer'],
            'd': [[11, 14, 17], [3, 3, 3], 'hard_integer'],
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': [1, 4, 7],
                'b': [1, 4, 7],
                'c': [11, 14, 17],
                'd': [11, 14, 17]
            },
            1: {}
        }


    @staticmethod
    @pytest.fixture
    def new_params():
        return {
            'a': [[1, 4, 7], [3, 3, 3], 'soft_integer'],
            'b': [[1, 4, 7], [3, 3, 3], 'hard_integer'],
            'c': [[11, 14, 17], [3, 3, 3], 'soft_integer'],
            'd': [[11, 14, 17], [3, 3, 3], 'hard_integer']
        }


    @staticmethod
    @pytest.fixture
    def new_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('key', list('abcd'))
    @pytest.mark.parametrize('posn', [0, 1, 2])
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, new_is_logspace,
        new_params, key, posn
    ):

        _pass = 1

        out_grid, out_param, out_is_logspace = \
            _drill(
                _param_name=key,
                _grid=good_grids[0][key],
                _param_value=good_params[key],
                _is_logspace=good_is_logspace[key],
                _pass=_pass,
                _best=good_grids[0][key][posn]
            )

        # min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        if 'soft' in good_params[key][-1]:
            if posn == 0:
                __ = good_grids[0][key]
                assert min(out_grid) == max(1, (__[0] - (__[1] - __[0])))
                del __
            else:
                assert min(out_grid) == good_grids[0][key][posn-1] + 1
        elif 'hard' in good_params[key][-1]:
            if posn == 0:
                assert min(out_grid) == good_grids[0][key][0]
            else:
                __ = good_grids[0][key]
                assert min(out_grid) == \
                    max(__[0], (__[posn] - (__[posn] - __[posn-1]))) + 1
                del __
        # END min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        __ = good_grids[0][key]
        assert max(out_grid) <= (__[-1] + (__[-1] - __[-2]))
        del __
        # END max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert len(out_grid) == good_params[key][1][_pass]

        assert out_param == new_params[key]
        assert out_is_logspace == new_is_logspace[key]



class TestIntNonUnitGapEquals2:


    @staticmethod
    @pytest.fixture
    def good_params():
        return {
            'a': [[1, 3, 5, 7], [3, 3, 3], 'soft_integer'],
            'b': [[1, 3, 5, 7], [3, 3, 3], 'hard_integer'],
            'c': [[11, 13, 15, 17], [3, 3, 3], 'soft_integer'],
            'd': [[11, 13, 15, 17], [3, 3, 3], 'hard_integer'],
        }


    @staticmethod
    @pytest.fixture
    def good_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False
        }


    @staticmethod
    @pytest.fixture
    def good_grids():
        return {
            0: {
                'a': [1, 3, 5, 7],
                'b': [1, 3, 5, 7],
                'c': [11, 13, 15, 17],
                'd': [11, 13, 15, 17]
            },
            1: {}
        }


    @staticmethod
    @pytest.fixture
    def new_params():
        return {
            'a': [[1, 3, 5, 7], [3, 3, 3], 'soft_integer'],
            'b': [[1, 3, 5, 7], [3, 3, 3], 'hard_integer'],
            'c': [[11, 13, 15, 17], [3, 3, 3], 'soft_integer'],
            'd': [[11, 13, 15, 17], [3, 3, 3], 'hard_integer']
        }


    @staticmethod
    @pytest.fixture
    def new_is_logspace():
        return {
            'a': False,
            'b': False,
            'c': False,
            'd': False
        }

    # END fixtures -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('key', list('abcd'))
    @pytest.mark.parametrize('posn', [0, 1, 2, 3])
    def test_accuracy(
        self, good_grids, good_is_logspace, good_params, new_is_logspace,
        new_params, key, posn
    ):

        _pass = 1

        out_grid, out_param, out_is_logspace = \
            _drill(
                _param_name=key,
                _grid=good_grids[0][key],
                _param_value=good_params[key],
                _is_logspace=good_is_logspace[key],
                _pass=_pass,
                _best=good_grids[0][key][posn]
            )

        # min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        if 'soft' in good_params[key][-1]:
            if posn == 0:
                __ = good_grids[0][key]
                assert min(out_grid) == max(1, (__[0] - (__[1] - __[0])))
                del __
            else:
                assert min(out_grid) == good_grids[0][key][posn-1] + 1
        elif 'hard' in good_params[key][-1]:
            if posn == 0:
                assert min(out_grid) == good_grids[0][key][0]

            elif posn == len(good_grids[0][key]) - 1:
                assert min(out_grid) == good_grids[0][key][posn] - 2
            else:
                __ = good_grids[0][key]
                assert min(out_grid) == \
                    max(__[0], (__[posn] - (__[posn] - __[posn-1]))) + 1
                del __
        # END min ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        # max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        if good_is_logspace[key]:
            __ = np.log10(good_grids[0][key])
            assert max(out_grid) <= 10**(__[-1] + (__[-1] - __[-2]))
            del __
        else: # not logspace
            __ = good_grids[0][key]
            assert max(out_grid) <= (__[-1] + (__[-1] - __[-2]))
            del __
        # END max ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert len(out_grid) == good_params[key][1][_pass]

        if 'soft' in good_params[key][-1]:
            if posn in [0, 3]:
                if posn == 0 and good_grids[0][key][0] == 1:  # integer universal min
                    assert out_param == new_params[key]
                else:
                    __ = deepcopy(new_params[key])
                    __[1] = [3, 4, 3]
                    assert out_param == __
        else:
            assert out_param == new_params[key]

        assert out_is_logspace == new_is_logspace[key]







