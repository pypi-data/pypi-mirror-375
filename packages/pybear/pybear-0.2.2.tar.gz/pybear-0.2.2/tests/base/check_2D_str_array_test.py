# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import random

import numpy as np
import pandas as pd
import polars as pl

from pybear.base._check_2D_str_array import check_2D_str_array



class TestCheck2DNumArray:


    @pytest.mark.parametrize('junk_array',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [0,1], (1,), {1,2},
         {'a':1}, lambda x: x, ({'a':1}, {'b':2}),
         ['a', 'b', 1, 'd'])
    )
    def test_blocks_junk(self, junk_array):

        with pytest.raises(TypeError):

            check_2D_str_array(junk_array)


    def test_rejects_1D(self):

        _base_np = np.random.choice(list('abcd'), (5, ))

        with pytest.raises(TypeError):
            check_2D_str_array(list(_base_np))

        with pytest.raises(TypeError):
            check_2D_str_array(tuple(list(_base_np)))

        with pytest.raises(TypeError):
            check_2D_str_array(_base_np)

        with pytest.raises(TypeError):
            check_2D_str_array(pd.Series(_base_np))

        with pytest.raises(TypeError):
            check_2D_str_array(pl.Series(_base_np))


    @pytest.mark.parametrize('require_finite', (True, False))
    @pytest.mark.parametrize('has_non_finite', (True, False))
    @pytest.mark.parametrize('container',
        (list, tuple, np.array, pd.DataFrame, pl.DataFrame)
    )
    @pytest.mark.parametrize('is_ragged', (True, False))
    def test_accuracy(
        self, require_finite, has_non_finite, container, is_ragged
    ):

        if is_ragged:
            if hasattr(container, 'to_array'):
                pytest.skip(reason=f'cant make ragged')
            if container in (pd.DataFrame, pl.DataFrame):
                pytest.skip(reason=f'cant make ragged')

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _shape = (37, 13)

        _base_np = np.random.choice(
            list('abcdefghijklmnop'),
            _shape
        ).astype(object)

        if has_non_finite:
            _pool = ('nan', '-inf')
            for _ in range(np.prod(_shape)//20):
                _rand_r_idx = np.random.randint(0, _shape[0])
                _rand_c_idx = np.random.randint(0, _shape[1])
                _base_np[_rand_r_idx, _rand_c_idx] = np.random.choice(_pool)


        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if container in [list, tuple, np.array]:

            _X = _base_np.tolist()

            if is_ragged:
                # ragged-ize the array
                for r_idx in range(_shape[0]):
                    _X[r_idx] = _X[r_idx][:random.randint(_shape[1]//2,_shape[1])]

            if container is np.array:
                _X = np.array(list(map(container, _X)), dtype=object)
                assert isinstance(_X, np.ndarray)
                assert all(map(isinstance, _X, (np.ndarray for _ in _X)))
            else:
                _X = container(map(container, _X))
                assert isinstance(_X, container)
                assert all(map(isinstance, _X, (container for _ in _X)))

            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_2D_str_array(
                        _X,
                        require_all_finite=require_finite
                    )
            else:
                assert check_2D_str_array(
                    _X,
                    require_all_finite=require_finite
                ) is None

        elif container in [pd.DataFrame, pl.DataFrame]:

            _X = container(_base_np)

            if container is np.array:
                assert isinstance(_X, np.ndarray)
            else:
                assert isinstance(_X, container)

            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_2D_str_array(
                        _X,
                        require_all_finite=require_finite
                    )
            else:
                assert check_2D_str_array(
                    _X,
                    require_all_finite=require_finite
                ) is None

        else:
            raise Exception


