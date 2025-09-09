# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.utilities._nan_masking import nan_mask

from pybear.preprocessing._MinCountTransformer._transform. \
    _parallelized_row_masks import _parallelized_row_masks



class TestParallelizedRowMasks:


    # def _parallelized_row_masks(
    #     _X_CHUNK: npt.NDArray,
    #     _UNQ_CT_DICT: TotalCountsByColumnType,  (a sub-chunk of the full)
    #     _instr: InstructionsType,   (a sub-chunk of the full)
    #     _reject_unseen_values: bool
    # ) -> npt.NDArray[np.uint32]:


    # fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    @staticmethod
    @pytest.fixture(scope='module')
    def _pool_size(_shape):
        return _shape[0] // 20    # dont make this ratio > 26 because of alphas


    @staticmethod
    @pytest.fixture(scope='module')
    def _thresh(_shape, _pool_size):
        return _shape[0] // _pool_size


    @staticmethod
    @pytest.fixture(scope='module')
    def good_unq_ct_dict():

        def foo(any_chunk):

            _unq_ct_dict = {}
            for _c_idx in range(any_chunk.shape[1]):

                _column = any_chunk[:, _c_idx]

                try:  # excepts on np int dtype
                    _column[nan_mask(_column)] = str(np.nan)
                except:
                    pass
                __ = dict((zip(*np.unique(_column, return_counts=True))))
                # can only have one nan in it
                _nan_ct = 0
                _new_dict = {}
                for _unq, _ct in __.items():
                    if str(_unq) == 'nan':
                        _nan_ct += int(_ct)
                    else:
                        _new_dict[_unq] = int(_ct)

                if _nan_ct > 0:
                    _new_dict[np.nan] = int(_nan_ct)

                _unq_ct_dict[_c_idx] = _new_dict

            return _unq_ct_dict

        return foo


    @staticmethod
    @pytest.fixture(scope='module')
    def good_instr():

        def foo(any_unq_ct_dict, _thresh):

            _INSTR = {}
            for _c_idx, v in any_unq_ct_dict.items():

                COL_INSTR = []
                for unq, ct in any_unq_ct_dict[_c_idx].items():
                    if ct < _thresh:
                        COL_INSTR.append(unq)

                if len(COL_INSTR) >= len(any_unq_ct_dict[_c_idx]) - 1:
                    COL_INSTR.append('DELETE COLUMN')

                _INSTR[_c_idx] = COL_INSTR

            return _INSTR

        return foo


    # END fixtures v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_accuracy_making_delete_masks(
        self, _X_factory, good_instr, good_unq_ct_dict, _thresh, _shape,
        _dtype, _has_nan
    ):

        if _dtype == 'int' and _has_nan is True:
            pytest.skip(reason=f"impossible condition, nans in int np")
        if _dtype == 'hybrid' and _has_nan is True:
            pytest.skip(reason=f"good_unq_ct_dict cant handle it")
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _X_wip = _X_factory(
            _format='np',
            _has_nan=_has_nan,
            _dtype=_dtype,
            _zeros=None,
            _shape=_shape
        )

        UNQ_CT_DICT = good_unq_ct_dict(_X_wip)
        GOOD_INSTR = good_instr(UNQ_CT_DICT, _thresh)
        for _c_idx in UNQ_CT_DICT:
            assert len(GOOD_INSTR[_c_idx]) > 0, \
                f"if this excepts, it wants to keep all unqs"

        # get actual ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        out = _parallelized_row_masks(
            _X_wip,
            UNQ_CT_DICT,
            GOOD_INSTR,
            _reject_unseen_values=False
        )
        # END get actual ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        chunk_exp = np.zeros((_shape[0], ))
        for _c_idx in range(_X_wip.shape[1]):
            _c_exp = _X_wip[:, _c_idx]
            # convert UNQ_CT_DICT keys to str for easy comparisons
            UNQ_CT_DICT[_c_idx] = dict((
                zip(map(str, UNQ_CT_DICT[_c_idx].keys()), UNQ_CT_DICT[_c_idx].values())
            ))
            for idx, value in enumerate(_c_exp):
                if UNQ_CT_DICT[_c_idx][str(value)] < _thresh:
                    _c_exp[idx] = 1  # overwriting takes dtype of _c_exp...
                else:
                    _c_exp[idx] = 0  # overwriting takes dtype of _c_exp...

            # ... so convert to uint8
            _c_exp = _c_exp.astype(np.uint8)

            chunk_exp += _c_exp

        # chunk_exp is a delete mask

        assert np.array_equiv(out, chunk_exp)


    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_accuracy_reject_unseen(
        self, _X_factory, good_instr, good_unq_ct_dict, _thresh, _dtype,
        _has_nan, _shape
    ):

        if _dtype == 'int' and _has_nan is True:
            pytest.skip(reason=f"impossible condition, nans in int np")
        if _dtype == 'hybrid' and _has_nan is True:
            pytest.skip(reason=f"good_unq_ct_dict cant handle it")
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _X_wip = _X_factory(
            _has_nan=_has_nan,
            _dtype=_dtype,
            _zeros=None,
            _shape=_shape
        )


        UNQ_CT_DICT = good_unq_ct_dict(_X_wip)
        GOOD_INSTR = good_instr(UNQ_CT_DICT, _thresh)
        for _c_idx in GOOD_INSTR:
            assert len(GOOD_INSTR[_c_idx]) > 0, \
                f"if this excepts, it wants to keep all unqs"

        # put unseen values into data
        _rand_c_idx = int(np.random.randint(0, _shape[1]))
        if isinstance(_X_wip[:, _rand_c_idx][0], str):
            _X_wip[np.random.randint(0, _shape[0]), _rand_c_idx] = 'z'
        else:
            _X_wip[np.random.randint(0, _shape[0]), _rand_c_idx] = 13
        del _rand_c_idx

        # False does not except
        out = _parallelized_row_masks(
            _X_wip,
            UNQ_CT_DICT,
            good_instr(UNQ_CT_DICT, _thresh),
            _reject_unseen_values=False,
        )

        # True raises ValueError
        with pytest.raises(ValueError):
            out = _parallelized_row_masks(
                _X_wip,
                UNQ_CT_DICT,
                good_instr(UNQ_CT_DICT, _thresh),
                _reject_unseen_values=True
            )





