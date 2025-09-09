# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing import MinCountTransformer as MCT



class TestGetRowSupport:

    # keep these tests separate. no other preprocessing has get_support methods

    @staticmethod
    @pytest.fixture(scope='module')
    def _count_threshold(_shape):
        return _shape[0] // 10


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_np(_count_threshold, _shape, _kwargs):

        # rig an array so some known rows in one column will be deleted
        # on 1st RCR and more known rows will be deleted from a second
        # column on the 2nd RCR. make first rcr chop some of the rigged
        # values in the second column so that those values fall below
        # threshold going into 2nd RCR.

        _kwargs['count_threshold'] = _count_threshold
        _kwargs['ignore_non_binary_integer_columns'] = False

        _MCT = MCT(**_kwargs)

        __ = np.random.randint(0, 2, _shape)

        # put some new integers below threshold at the end of the first column
        __[-_count_threshold // 2:, 0] = 99
        # put the same new integer in the second column so some will be
        # deleted incidentally on the first rcr and those that are left
        # will be below threshold for 2nd rcr.
        __[-_count_threshold:, 1] = 99

        out1 = _MCT.fit_transform(__)
        assert out1.shape[0] == (_shape[0] - _count_threshold // 2)

        _MCT.reset()
        _MCT.set_params(max_recursions=2)

        out2 = _MCT.fit_transform(__)
        assert out2.shape[0] == (_shape[0] - _count_threshold)

        # we have a block of data where the first column will cause some
        # known rows to be removed on the first rcr and the 2nd column
        # will cause some more known rows last will be removed on the
        # 2nd rcr.

        return __

    # END fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('_indices', (True, False))
    def test_get_row_support(
        self, _X_np, _kwargs, _indices, _shape, _count_threshold
    ):

        assert _X_np.shape == _shape

        _kwargs['count_threshold']: _count_threshold
        _kwargs['ignore_float_columns']: True
        _kwargs['ignore_non_binary_integer_columns']: False
        _kwargs['delete_axis_0']: True  # <=== must be True, working with bin_ints
        _kwargs['max_recursions']: 1

        _MCT_1 = MCT(**_kwargs)
        _MCT_1.set_params(max_recursions=1)
        _MCT_2 = MCT(**_kwargs)
        _MCT_2.set_params(max_recursions=2)

        TRFM_X_1 = _MCT_1.fit_transform(_X_np)
        assert TRFM_X_1.shape[0] == (_shape[0] - _count_threshold // 2)
        TRFM_X_2 = _MCT_2.fit_transform(_X_np)
        assert TRFM_X_2.shape[0] == (_shape[0] - _count_threshold)


        for _indices in [True, False]:

            out1 = _MCT_1.get_row_support(_indices)
            out2 = _MCT_2.get_row_support(_indices)

            # must return ndarray -- -- -- -- -- -- -- -- -- -- -- -- --
            for _rcr, _out in enumerate([out1, out2], 1):
                assert isinstance(_out, np.ndarray), \
                    (f"{_rcr} recursion get_row_support() did not return "
                     f"numpy.ndarray")
            # END must return ndarray -- -- -- -- -- -- -- -- -- -- --

            if not _indices:
                # must be boolean -- -- -- -- -- -- -- -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert _out.dtype == bool, \
                        (f"{_rcr} recursion get_row_support with indices=False "
                         f"did not return a boolean array")
                # END must be boolean -- -- -- -- -- -- -- -- -- -- --

                # len(SUPPORT) MUST EQUAL NUMBER OF ROWS IN X -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert len(_out) == _X_np.shape[0], \
                        (f"{_rcr} recursion len(get_row_support({_indices})) "
                         f"!= X rows")
                # END len(SUPPORT) MUST EQUAL NUMBER OF ROWS IN X -- --

                # NUM ROWS KEPT MUST BE <= _n_rows_in -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert sum(_out) <= _X_np.shape[0], \
                        (f"impossibly, number of rows kept by {_rcr} "
                         f"recursion > number of rows in X")
                # END NUM ROWS KEPT MUST BE <= _n_rows_in -- -- -- -- --

                # INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR -- --
                assert np.all(out1[out2]), (f"Rows that are to be "
                         f"kept in 2 rcr were False in 1 rcr")
                # END INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR --

            elif _indices:
                # all integers -- -- -- -- -- -- -- -- -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert np.all(list(map(lambda x: int(x) == x, _out))), \
                        (f"{_rcr} rcr get_row_support with indices=True "
                         f"did not return an array of integers")
                # END all integers -- -- -- -- -- -- -- -- -- -- -- --

                # NUM ROWS KEPT MUST BE <= _n_rows_in -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert len(_out) <= _X_np.shape[0], \
                        (f"impossibly, number of rows kept by {_rcr} "
                         f"recursion > number of rows in X")
                # END NUM ROWS KEPT MUST BE <= _n_rows_in -- -- -- -- --

                # INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR -- --
                _bool1 = np.zeros(_X_np.shape[0]).astype(bool)
                _bool1[out1] = True
                _bool2 = np.zeros(_X_np.shape[0]).astype(bool)
                _bool2[out2] = True
                assert np.all(_bool1[_bool2]), (f"Rows that are to be "
                    f"kept by 2 rcr were not kept by 1 rcr")
                # END INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR --

        # last rows should have dropped on 1st rcr
        _ref_mask_1 = np.ones(_X_np.shape[0]).astype(bool)
        _ref_mask_1[-_count_threshold//2:] = False
        assert np.array_equal(_MCT_1.get_row_support(False), _ref_mask_1)

        # more rows from the bottom should have dropped on 2nd rcr
        _ref_mask_2 = np.ones(_X_np.shape[0]).astype(bool)
        _ref_mask_2[-_count_threshold:] = False
        assert np.array_equal(_MCT_2.get_row_support(False),_ref_mask_2)

        # as_bool should convert to the same thing as_indices
        assert np.array_equal(
            np.arange(_X_np.shape[0])[_MCT_1.get_row_support(False)],
            _MCT_1.get_row_support(True)
        )

        assert np.array_equal(
            np.arange(_X_np.shape[0])[_MCT_2.get_row_support(False)],
            _MCT_2.get_row_support(True)
        )

        del _MCT_1, _MCT_2, _out, out1, out2, _indices





