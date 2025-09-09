# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_1D_num_sequence import check_1D_num_sequence

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest



class TestCheck1DNumSequence:


    @pytest.mark.parametrize('junk_vector',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', list('ab'), tuple('abc'),
         set('xyz'), {'a':1}, lambda x: x)
    )
    def test_blocks_junk(self, junk_vector):

        with pytest.raises(TypeError):

            check_1D_num_sequence(junk_vector)


    def test_rejects_2D(self):

        _base_np = np.random.uniform(0, 1, (5,3))

        with pytest.raises(TypeError):
            check_1D_num_sequence(list(map(list, _base_np)))

        with pytest.raises(TypeError):
            check_1D_num_sequence(tuple(map(tuple, _base_np)))

        with pytest.raises(TypeError):
            check_1D_num_sequence(_base_np)

        with pytest.raises(TypeError):
            check_1D_num_sequence(pd.DataFrame(_base_np))

        with pytest.raises(TypeError):
            check_1D_num_sequence(pl.DataFrame(_base_np))

        with pytest.raises(TypeError):
            check_1D_num_sequence(ss.csc_matrix(_base_np))

        with pytest.raises(TypeError):
            check_1D_num_sequence(ss.csc_array(_base_np))


    @pytest.mark.parametrize('require_finite', (True, False))
    @pytest.mark.parametrize('has_non_finite', (True, False))
    @pytest.mark.parametrize('container',
        (list, tuple, set, np.array, pd.Series, pl.Series)
    )
    def test_accuracy(
        self, require_finite, has_non_finite, container
    ):

        _base_np = np.random.uniform(0, 1, (5,))
        if has_non_finite:
            _base_np[1] = np.nan
            _base_np[-2] = np.inf


        if container in [list, tuple, set]:
            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_1D_num_sequence(
                        container(_base_np.tolist()),
                        require_all_finite=require_finite
                    )
            else:
                assert check_1D_num_sequence(
                    container(_base_np.tolist()),
                    require_all_finite=require_finite
                ) is None

        elif container in [np.array, pd.Series, pl.Series]:

            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_1D_num_sequence(
                        container(_base_np),
                        require_all_finite=require_finite
                    )
            else:
                assert check_1D_num_sequence(
                    container(_base_np),
                    require_all_finite=require_finite
                ) is None


        else:
            raise Exception







