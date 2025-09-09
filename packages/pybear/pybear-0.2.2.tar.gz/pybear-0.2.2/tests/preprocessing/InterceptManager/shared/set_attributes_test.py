# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._InterceptManager._shared._set_attributes import \
    _set_attributes



class TestSetAttributes:


    # def _set_attributes(
    #     constant_columns_: ConstantColumnsType,
    #     _instructions: InstructionType,
    #     _n_features_in: int
    # ) -> tuple[KeptColumnsType, RemovedColumnsType, ColumnMaskType]:


    @pytest.mark.parametrize('keep, delete',
        (
            (None, [1, 3, 5, 7]),
            ([1, 5], [3, 7]),
            ([1, 3, 5, 7], None),
            (None, None),
            ([1, 3, 5], [1, 3, 5]),
            ([1], [3, 5, 7])
        )
    )
    @pytest.mark.parametrize('add', (None, {'Intercept': 1}))
    def test_accuracy(self, keep, delete, add):

        # this test goes beyond what should normally would be seen by
        # _set_attributes. keep should at most have only one value in it.

        _n_features_in = 8

        _constant_columns = {1: 0, 3: 1, 5: np.nan, 7: np.pi}

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # build '_instructions' from the given keep, delete, & add

        # all constant columns must be accounted for. the 'slush' place is
        # 'keep', so fill that based on what is in 'delete'
        _keep = keep or []
        for _col_idx in _constant_columns.keys():
            if (_col_idx in _keep) or (delete and _col_idx in delete):
                pass
            else:
                _keep.append(_col_idx)

        _instructions = {
            'keep': _keep if len(_keep) else None,
            'delete': delete,
            'add': add
        }


        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        if len(set(delete or []).intersection(keep or [])):
            # a col idx in both 'keep' & 'delete'
            with pytest.raises(AssertionError):
                _set_attributes(
                    _constant_columns,
                    _instructions,
                    _n_features_in=_n_features_in
                )
            pytest.skip(reason=f'cant continue after except')
        else:
            out_kept_columns, out_removed_columns, out_column_mask = \
                _set_attributes(
                    _constant_columns,
                    _instructions,
                    _n_features_in=_n_features_in
                )

        assert out_kept_columns == {k:_constant_columns[k] for k in _keep}

        assert out_removed_columns == \
               {k:_constant_columns[k] for k in (delete or [])}

        assert out_column_mask.dtype == bool
        assert len(out_column_mask) == _n_features_in
        exp_col_mask = []
        for i in range(_n_features_in):
            if (i in _keep) or (i not in _constant_columns):
                exp_col_mask.append(True)
            else:
                exp_col_mask.append(False)
        assert np.array_equal(
            out_column_mask,
            exp_col_mask
        )




