# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.GSTCV._GSTCV._fit._fold_splitter import _fold_splitter



class TestSKFoldSplitter:


    # def _fold_splitter(
    #     train_idxs: SKSlicerType,
    #     test_idxs: SKSlicerType,
    #     *data_objects: SKXType | SKYTypes
    # ) -> tuple[SKSplitType, ...]:


    # 25_05_14 no longer explicity blocking containers w/o shape attr
    # @pytest.mark.parametrize('bad_data_object',
    #     (1, 3.14, True, False, None, 'junk', min, [0,1], (0,1), {0,1},
    #     {'a':1}, lambda x: x)
    # )
    # def test_rejects_everything_without_shape_attr(self, bad_data_object):
    #
    #     with pytest.raises(AttributeError):
    #         _fold_splitter(
    #             [0,2,4],
    #             [1,3],
    #             bad_data_object
    #         )


    # 25_05_14 no longer explicitly enforcing 1D or 2D
    @pytest.mark.parametrize('bad_data_object',
        (
            np.random.randint(0, 10, (5, 5, 5)),
            np.random.randint(0, 10, (5, 5, 5, 5)),
        )
    )
    def test_rejects_bad_shape(self, bad_data_object):

        # with pytest.raises(AssertionError):
        _fold_splitter(
            [0,2,4],
            [1,3],
            bad_data_object
        )




    @pytest.mark.parametrize('_X1_format',
        ('np', 'pd', 'ss', 'pl', 'py_list', 'py_tup')
    )
    @pytest.mark.parametrize('_X1_dim', (1, 2))
    @pytest.mark.parametrize('_X2_format',
        ('np', 'pd', 'ss', 'pl', 'py_list', 'py_tup')
    )
    @pytest.mark.parametrize('_X2_dim', (1, 2))
    def test_accuracy(
        self, _rows, X_np, _format_helper, _X1_format, _X1_dim, _X2_format,
        _X2_dim
    ):

        if (_X1_dim == 1 and _X1_format == 'ss') \
                or (_X2_dim == 1 and _X2_format == 'ss'):
            pytest.skip(reason=f"cant have 1D scipy sparse")

        # END skip impossible -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _X1 = _format_helper(X_np, _X1_format, _X1_dim)
        _X2 = _format_helper(X_np, _X2_format, _X2_dim)


        _helper_mask = np.random.randint(0, 2, (_rows,)).astype(bool)
        mask_train = np.arange(_rows)[_helper_mask]
        mask_test = np.arange(_rows)[np.logical_not(_helper_mask)]
        del _helper_mask

        if _X1_dim == 1:
            _X1_ref_train = X_np[:, 0][mask_train]
            _X1_ref_test = X_np[:, 0][mask_test]
        elif _X1_dim == 2:
            _X1_ref_train = X_np[mask_train]
            _X1_ref_test = X_np[mask_test]
        else:
            raise Exception

        if _X2_dim == 1:
            _X2_ref_train = X_np[:, 0][mask_train]
            _X2_ref_test = X_np[:, 0][mask_test]
        elif _X2_dim == 2:
            _X2_ref_train = X_np[mask_train]
            _X2_ref_test = X_np[mask_test]
        else:
            raise Exception


        out = _fold_splitter(mask_train, mask_test, _X1, _X2)

        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for i in out)))


        assert type(out[0][0]) == type(_X1)
        if _X1_format == 'np':
            assert np.array_equiv(out[0][0], _X1_ref_train)
        elif _X1_format == 'pd':
            assert np.array_equiv(out[0][0].to_numpy(), _X1_ref_train)
        elif _X1_format == 'ss':
            assert np.array_equiv(out[0][0].toarray(), _X1_ref_train)
        elif _X1_format == 'pl':
            assert np.array_equiv(out[0][0].to_numpy(), _X1_ref_train)
        else:
            # py_list, py_tup
            assert np.array_equiv(out[0][0], _X1_ref_train)


        assert type(out[0][1]) == type(_X1)
        if _X1_format == 'np':
            assert np.array_equiv(out[0][1], _X1_ref_test)
        elif _X1_format == 'pd':
            assert np.array_equiv(out[0][1].to_numpy(), _X1_ref_test)
        elif _X1_format == 'ss':
            assert np.array_equiv(out[0][1].toarray(), _X1_ref_test)
        elif _X1_format == 'pl':
            assert np.array_equiv(out[0][1].to_numpy(), _X1_ref_test)
        else:
            # py_list, py_tup
            assert np.array_equiv(out[0][1], _X1_ref_test)


        assert type(out[1][0]) == type(_X2)
        if _X2_format == 'np':
            assert np.array_equiv(out[1][0], _X2_ref_train)
        elif _X2_format == 'pd':
            assert np.array_equiv(out[1][0].to_numpy(), _X2_ref_train)
        elif _X2_format == 'ss':
            assert np.array_equiv(out[1][0].toarray(), _X2_ref_train)
        elif _X2_format == 'pl':
            assert np.array_equiv(out[1][0].to_numpy(), _X2_ref_train)
        else:
            # py_list, py_tup
            assert np.array_equiv(out[1][0], _X2_ref_train)


        assert type(out[1][1]) == type(_X2)
        if _X2_format == 'np':
            assert np.array_equiv(out[1][1], _X2_ref_test)
        elif _X2_format == 'pd':
            assert np.array_equiv(out[1][1].to_numpy(), _X2_ref_test)
        elif _X2_format == 'ss':
            assert np.array_equiv(out[1][1].toarray(), _X2_ref_test)
        elif _X2_format == 'pl':
            assert np.array_equiv(out[1][1].to_numpy(), _X2_ref_test)
        else:
            # py_list, py_tup
            assert np.array_equiv(out[1][1], _X2_ref_test)




