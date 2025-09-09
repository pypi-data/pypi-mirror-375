# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.base._check_1D_str_sequence import check_1D_str_sequence



class TestCheck1DStrSequence:


    @pytest.mark.parametrize('junk_vector',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [1,2], (1,2), {1,2},
         {'a':1}, lambda x: x, [[1,2], 'what'])
    )
    def test_blocks_junk(self, junk_vector):

        with pytest.raises(TypeError):

            check_1D_str_sequence(junk_vector)


    def test_rejects_2D(self):

        # ss cant take str

        _base_np = np.random.choice(list('abcde'), (5,3))

        with pytest.raises(TypeError):
            check_1D_str_sequence(list(map(list, _base_np)))

        with pytest.raises(TypeError):
            check_1D_str_sequence(tuple(map(tuple, _base_np)))

        with pytest.raises(TypeError):
            check_1D_str_sequence(_base_np)

        with pytest.raises(TypeError):
            check_1D_str_sequence(pd.DataFrame(_base_np))

        with pytest.raises(TypeError):
            check_1D_str_sequence(pl.DataFrame(_base_np))


    @pytest.mark.parametrize('require_finite', (True, False))
    @pytest.mark.parametrize('has_non_finite', (True, False))
    @pytest.mark.parametrize('container',
        (list, tuple, set, np.array, pd.Series, pl.Series)
    )
    def test_accepts_good_and_require_finite(
        self, require_finite, has_non_finite, container
    ):

        # astype('<U3') is important so it doesnt truncate
        _base_np = np.random.choice(list('qrstuvwxyz'), (5,)).astype('<U3')
        if has_non_finite:
            _base_np[0] = 'pd.NA'
            _base_np[1] = 'np.nan'
            _base_np[3] = '-inf'
            _base_np[4] = 'inf'


        if container in [list, tuple, set]:
            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_1D_str_sequence(
                        container(_base_np.tolist()),
                        require_all_finite=require_finite
                    )
            else:
                assert check_1D_str_sequence(
                    container(_base_np.tolist()),
                    require_all_finite=require_finite
                ) is None

        elif container in [np.array, pd.Series, pl.Series]:

            if require_finite and has_non_finite:
                with pytest.raises(ValueError):
                    check_1D_str_sequence(
                        container(_base_np),
                        require_all_finite=require_finite
                    )
            else:
                assert check_1D_str_sequence(
                    container(_base_np),
                    require_all_finite=require_finite
                ) is None


        else:
            raise Exception







