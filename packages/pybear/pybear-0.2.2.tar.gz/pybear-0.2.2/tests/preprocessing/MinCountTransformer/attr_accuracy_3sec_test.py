# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


# n_features_in_

# feature_names_in_

# get_feature_names_out

# get_support - NDArray of retained columns in the output

# get_row_support - NDArray of the rows retained in the last data passed
# to transform

# original_dtypes_ NDArray of MCT-assigned dtypes for each column.
# the accuracy of building one of them for real data is tested in
# parallel_dtype_unqs_cts_test.

# total_counts_by_column_ is a dict of uniques and counts in each column.
# the accuracy of building one of them for real data is tested in
# parallel_dtype_unqs_cts_test. the accuracy of merging 2 of these is
# tested with fabricated tcbcs is in tcbc_merger_test.

# instructions_ is built directly off of total_counts_by_column_. the
# accuracy of instructions_ vis-a-vis fabricated total_counts_by_column
# is tested in make_instructions_test.



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.preprocessing import MinCountTransformer as MCT



class TestAccuracy:


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl'))
    @pytest.mark.parametrize('_recursions', (1, 2))
    def test_accuracy(self, _X_factory, _columns, X_format, _recursions):

        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _shape = (100, 5)

        _X_wip = np.vstack((
            np.random.randint(0, 2, _shape[0]).astype(np.uint8),
            np.random.randint(0, 3, _shape[0]).astype(np.int32),
            np.random.uniform(0, 1, _shape[0]).astype(np.float64),
            np.random.choice(['a', 'b', 'c'], _shape[0]),
            # one column that gets removed
            np.full((_shape[0],), 1).astype(np.uint8)
        ))

        _X_wip = _X_wip.transpose()

        if X_format == 'np':
            pass
        elif X_format == 'pd':
            _X_wip = pd.DataFrame(data=_X_wip, columns=_columns[:_shape[1]])
        elif X_format == 'pl':
            _X_wip = pl.from_numpy(data=_X_wip, schema=list(_columns[:_shape[1]]))
        else:
            raise Exception

        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # set _kwargs
        _kwargs = {
            'count_threshold': _shape[0] // 10,
            'ignore_float_columns': True,
            'ignore_non_binary_integer_columns': False,
            'delete_axis_0': False,
            'max_recursions': _recursions
        }

        TestCls = MCT(**_kwargs)

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        # get expected number of kept columns
        if _recursions == 1:
            exp_num_kept = _shape[1] - 1

        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # attributes:
        #     'n_features_in_'
        #     'feature_names_in_'
        #     'original_dtypes_'
        #     'total_counts_by_column_'
        #     'instructions_'
        # and 'get_feature_names_out'
        #     'get_support'
        #     'get_row_support'

        # attr 'n_features_in_' is correct
        assert TestCls.n_features_in_ == _X_wip.shape[1]

        # attr 'feature_names_in_' is correct
        if X_format in ['pd', 'pl']:
            assert np.array_equal(TestCls.feature_names_in_, _columns[:_shape[1]])
            assert TestCls.feature_names_in_.dtype == object
        else:
            assert not hasattr (TestCls, 'feature_names_in_')

        # number of columns in output == number of expected
        if _recursions == 1:
            assert TRFM_X.shape[1] == exp_num_kept
        # this cannot be controlled for 2 recursions

        # validate TestCls attrs against ref objects v^v^v^v^v^v^v^v^v^v

        n_features_in_ = TestCls.n_features_in_

        # get_support_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # number of columns in output is adjusted correctly for num removed
        # assert all columns that werent constants are in the output
        ref_support = np.ones((_shape[1],)).astype(bool)
        ref_support[-1] = False
        _act_support = TestCls.get_support(indices=False)
        assert isinstance(_act_support, np.ndarray)
        assert len(_act_support) == n_features_in_
        if _recursions == 1:
            assert sum(_act_support) == exp_num_kept
        elif _recursions == 2:
            assert sum(_act_support) == TRFM_X.shape[1]
        assert np.array_equal(ref_support, _act_support)
        # END get_support_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # get_row_support_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # number of rows in output is adjusted correctly
        # dont know what the actual output should be, but it should be
        # <= to the original rows
        _act_row_support = TestCls.get_row_support(indices=False)
        assert isinstance(_act_row_support, np.ndarray)
        assert len(_act_row_support) == _shape[0]
        assert 0 < sum(_act_row_support) <= _shape[0]
        # END get_row_support_ -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # feature_names_out -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if X_format in ['pd', 'pl']:
            ref_feature_names_out = _columns[:_shape[1]-1]
        else:
            ref_feature_names_out = [f'x{i}' for i in range(_shape[1]-1)]

        if _recursions == 1:
            assert len(TestCls.get_feature_names_out()) == exp_num_kept
        elif _recursions == 2:
            assert len(TestCls.get_feature_names_out()) == TRFM_X.shape[1]

        assert np.array_equal(
            TestCls.get_feature_names_out(),
            ref_feature_names_out
        )
        # END feature_names_out -- -- -- -- -- -- -- -- -- -- -- -- --

        # original_dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        original_dtypes = TestCls.original_dtypes_
        assert isinstance(original_dtypes, np.ndarray)
        assert len(original_dtypes) == n_features_in_
        assert all(map(
            isinstance,
            list(original_dtypes),
            (str for _ in original_dtypes)
        ))
        assert np.array_equal(
            ['bin_int', 'int', 'float', 'obj', 'int'],
            original_dtypes
        )
        # END original_dtypes -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # total_counts_by_column_ -- -- -- -- -- -- -- -- -- -- -- -- --
        tcbc_ = TestCls.total_counts_by_column_
        assert isinstance(tcbc_, dict)
        assert len(tcbc_) == n_features_in_
        assert np.array_equal(sorted(list(tcbc_.keys())), range(n_features_in_))
        for k, v in tcbc_.items():
            assert isinstance(k, int)
            assert isinstance(v, dict)
            assert all(map(isinstance, v.values(), (int for _ in v)))
        # remember that _X_wip must be dtype object, so nums are strs
        assert tcbc_[_shape[1]-1] == {'1': _shape[0]}
        # END total_counts_by_column_ -- -- -- -- -- -- -- -- -- -- --

        # instructions_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _instr = TestCls.instructions_
        assert isinstance(_instr, dict)
        assert len(_instr) == n_features_in_
        assert np.array_equal(sorted(list(_instr.keys())), range(n_features_in_))
        for k, v in _instr.items():
            assert isinstance(k, int)
            assert isinstance(v, list)
        assert _instr[_shape[1]-1] == ['DELETE COLUMN']
        # END instructions_ -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # END validate TestCls attrs against ref objects v^v^v^v^v^v^v^v

        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **




