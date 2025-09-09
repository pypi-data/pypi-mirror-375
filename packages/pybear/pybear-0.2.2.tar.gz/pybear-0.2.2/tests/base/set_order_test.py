# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._set_order import set_order

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest




class TestSetOrder:

    # def set_order(
    #     X: npt.NDArray,
    #     *,
    #     order: Literal['C', 'F']="C",
    #     copy_X: bool=True
    # ) -> npt.NDArray:

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('non_ndarray', ('pd', 'pl', 'csr', 'csc'))
    def test_rejects_non_ndarray(self, non_ndarray):

        _shape = (20, 5)

        _base_X = np.random.randint(0, 10, _shape)

        if non_ndarray == 'pd':
            bad_X = pd.DataFrame(data=_base_X)
        elif non_ndarray == 'pl':
            bad_X = pl.from_numpy(_base_X)
        elif non_ndarray == 'csr':
            bad_X = ss.csr_array(_base_X)
        elif non_ndarray == 'csc':
            bad_X = ss.csc_array(_base_X)
        else:
            raise Exception

        with pytest.raises(TypeError):
            set_order(
                bad_X,
                order=np.random.choice(['C', 'F'])
            )


    def test_accepts_ndarray(self):

        out = set_order(
            np.random.randint(0, 10, (20, 5)),
            order=np.random.choice(['C', 'F'])
        )

        assert isinstance(out, np.ndarray)


    @pytest.mark.parametrize('junk_order',
        (-2.7, -1, 0, 1, 2.7, True, False, None, [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_rejects_junk_order(self, junk_order):

        with pytest.raises(TypeError):
            set_order(
                np.random.randint(0, 10, (20, 5)),
                order=junk_order
            )


    @pytest.mark.parametrize('bad_order',
        ('junk', 'trash', 'q', 'z', 'garbage', 'p')
    )
    def test_rejects_bad_order(self, bad_order):

        with pytest.raises(ValueError):
            set_order(
                np.random.randint(0, 10, (20, 5)),
                order=bad_order
            )


    @pytest.mark.parametrize('good_order', ('c', 'C', 'f', 'F'))
    def test_accepts_good_order(self, good_order):

        out = set_order(
            np.random.randint(0, 10, (20, 5)),
            order=good_order
        )

        assert isinstance(out, np.ndarray)


    @pytest.mark.parametrize('non_bool_copy_X',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_rejects_non_bool_copy_X(self, non_bool_copy_X):

        with pytest.raises(TypeError):
            set_order(
                np.random.randint(0, 10, (20, 5)),
                order="F",
                copy_X=non_bool_copy_X
            )


    @pytest.mark.parametrize('bool_copy_X', (True, False))
    def test_rejects_non_bool_copy_X(self, bool_copy_X):

        out = set_order(
            np.random.randint(0, 10, (20, 5)),
            order="F",
            copy_X=bool_copy_X
        )

        assert isinstance(out, np.ndarray)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('shape', ((10, 5), (5, 10), (10, ), (10, 1), (1, 20)))
    @pytest.mark.parametrize('order', ('C', 'F'))
    def test_accuracy(self, shape, order):

        # make in 'C' order
        X = np.random.randint(0, 10, shape)

        # set the order via set_order()
        X = set_order(X, order=order)


        # Check memory layout
        # see the notes in the base._set_order() module. 1D vectors and
        # trivial 2D vectors (10, 1), (1, 10) satisfy both C_CONTIGUOUS
        # and F_CONTIGUOUS.
        if order == 'C':
            assert X.flags['C_CONTIGUOUS'] is True
        if order == 'F':
            assert X.flags['F_CONTIGUOUS'] is True







