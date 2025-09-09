# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing import MinCountTransformer as MCT



class TestGetSupport:

    # keep these tests separate. no other preprocessing has get_support methods

    # this needs to stay, dont use conftest shape
    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        return (100, 4)


    @staticmethod
    @pytest.fixture(scope='module')
    def _count_threshold(_shape):
        return _shape[0] // 10


    @staticmethod
    @pytest.fixture(scope='function')
    def _X_np(_count_threshold, _shape, _kwargs):

        # rig an array so at least one column will be deleted on 1st RCR
        # and another will be deleted on the 2nd RCR

        _kwargs['count_threshold'] = _count_threshold
        _kwargs['ignore_float_columns'] = True

        _MCT = MCT(**_kwargs)

        _exc = Exception(f"failed to make a good X test fixture after 200 tries")

        ctr = 0
        while True:

            ctr += 1

            np.random.seed(np.random.choice([0, 1, 2]))

            # columns that wont be removed
            __ = np.random.randint(
                0, (_shape[0] // (2 * _count_threshold)), _shape
            )
            # a column to be removed on the second rcr
            _dum_column = np.zeros((_shape[0],))
            _dum_column[-_count_threshold:] = 99
            __ = np.hstack((__, _dum_column.reshape((-1, 1))))
            del _dum_column
            # spike a column that wont be removed with a single value
            # so that it strategically deletes a row
            __[-1, 0] = 98
            # a column of constants to be removed on the first rcr
            __ = np.hstack((__, np.ones((_shape[0], 1))))


            try:
                out1 = _MCT.fit_transform(__)
                if out1.shape[1] != (_shape[1] + 2 - 1):
                    raise Exception
            except:
                if ctr == 200:
                    raise _exc
                continue

            _MCT.reset()
            _MCT.set_params(max_recursions=2)
            try:
                # under try in case all columns or rows are deleted
                out2 = _MCT.fit_transform(__)
                if out2.shape[1] != (_shape[1] + 2 - 2):
                    raise Exception
                break
            except:
                if ctr == 200:
                    raise _exc

        # we have a block of data with _shape[1]+2 columns where the
        # last column will be removed on the first rcr and the 2nd to
        # last will be removed on the 2nd rcr.

        return __

    # END fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('_indices', (True, False))
    def test_get_support(
        self, _X_np, _kwargs, _indices, _shape, _count_threshold
    ):

        assert _X_np.shape == (_shape[0], _shape[1] + 2)

        _kwargs['count_threshold'] = _count_threshold
        _kwargs['ignore_float_columns'] = True

        _MCT_1 = MCT(**_kwargs)
        _MCT_1.set_params(max_recursions=1)
        _MCT_2 = MCT(**_kwargs)
        _MCT_2.set_params(max_recursions=2)

        TRFM_X_1 = _MCT_1.fit_transform(_X_np)
        assert TRFM_X_1.shape[1] == (_X_np.shape[1] - 1)
        TRFM_X_2 = _MCT_2.fit_transform(_X_np)
        assert TRFM_X_2.shape[1] == (_X_np.shape[1] - 2)


        for _indices in [True, False]:

            out1 = _MCT_1.get_support(_indices)
            out2 = _MCT_2.get_support(_indices)

            # must return ndarray -- -- -- -- -- -- -- -- -- -- -- -- --
            for _rcr, _out in enumerate([out1, out2], 1):
                assert isinstance(_out, np.ndarray), \
                    (f"{_rcr} recursion get_support() did not return "
                     f"numpy.ndarray")
            # END must return ndarray -- -- -- -- -- -- -- -- -- -- --

            if not _indices:
                # must be boolean -- -- -- -- -- -- -- -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert _out.dtype == bool, \
                        (f"{_rcr} recursion get_support with indices=False "
                         f"did not return a boolean array")
                # END must be boolean -- -- -- -- -- -- -- -- -- -- --

                # len(SUPPORT) MUST EQUAL NUMBER OF COLUMNS IN X -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert len(_out) == _X_np.shape[1], \
                        (f"{_rcr} recursion len(get_support({_indices})) != X "
                         f"columns")
                # END len(SUPPORT) MUST EQUAL NUMBER OF COLUMNS IN X --

                # NUM COLUMNS KEPT MUST BE <= n_features_in_ -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert sum(_out) <= _X_np.shape[1], \
                        (f"impossibly, number of columns kept by {_rcr} "
                         f"recursion > number of columns in X")
                # END NUM COLUMNS KEPT MUST BE <= n_features_in_ -- --

                # INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR -- --
                assert np.all(out1[out2]), (f"Columns that are to be "
                         f"kept in 2 rcr were False in 1 rcr")
                # END INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR --

            elif _indices:
                # all integers -- -- -- -- -- -- -- -- -- -- -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert np.all(list(map(lambda x: int(x) == x, _out))), \
                        (f"{_rcr} rcr get_support with indices=True did not "
                         f"return an array of integers")
                # END all integers -- -- -- -- -- -- -- -- -- -- -- --

                # NUM COLUMNS KEPT MUST BE <= n_features_in_ -- -- -- --
                for _rcr, _out in enumerate([out1, out2], 1):
                    assert len(_out) <= _X_np.shape[1], \
                        (f"impossibly, number of columns kept by {_rcr} "
                         f"recursion > number of columns in X")
                # END NUM COLUMNS KEPT MUST BE <= n_features_in_ -- --

                # INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR -- --
                _bool1 = np.zeros(_X_np.shape[1]).astype(bool)
                _bool1[out1] = True
                _bool2 = np.zeros(_X_np.shape[1]).astype(bool)
                _bool2[out2] = True
                assert np.all(_bool1[_bool2]), (f"Columns that are to be "
                    f"kept by 2 rcr were not kept by 1 rcr")
                # END INDICES IN TWO RECUR MUST ALSO BE IN ONE RECUR --

        # last column should have dropped on 1st rcr
        _ref_mask_1 = np.ones(_X_np.shape[1]).astype(bool)
        _ref_mask_1[-1] = False
        assert np.array_equal(_MCT_1.get_support(False), _ref_mask_1)

        # 2nd to last column should have dropped on 2nd rcr
        _ref_mask_2 = np.ones(_X_np.shape[1]).astype(bool)
        _ref_mask_2[-2:] = False
        assert np.array_equal(_MCT_2.get_support(False), _ref_mask_2)

        # as_bool should convert to the same thing as_indices
        assert np.array_equal(
            np.arange(_X_np.shape[1])[_MCT_1.get_support(False)],
            _MCT_1.get_support(True)
        )

        assert np.array_equal(
            np.arange(_X_np.shape[1])[_MCT_2.get_support(False)],
            _MCT_2.get_support(True)
        )

        del _MCT_1, _MCT_2, _out, out1, out2, _indices





