# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _make_instructions import _make_instructions



class TestMakeInstructions:


    @staticmethod
    @pytest.fixture
    def good_tcbc():

        return {
            0: {'a': 500, 'b': 350, 'c': 100, np.nan: 50},
            1: {0: 640, 1: 350, np.nan: 10},
            2: {0: 200, 2.718: 400, 3.141: 300, 6.638: 50, 8.834: 40, np.nan: 10},
            3: {0: 600, 1: 200, 2: 100, 3: 50, 4: 25, np.nan: 25}
        }


    @staticmethod
    @pytest.fixture
    def good_og_dtypes():

        return np.array(['obj', 'int', 'float', 'int'], dtype='<U5')

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # all the _validation is handled in individual modules, and tested indiv
    # _make_instructions_validation(
    #     _count_threshold,
    #     _ignore_float_columns,
    #     _ignore_non_binary_integer_columns,
    #     _ignore_columns,
    #     _ignore_nan,
    #     _handle_as_bool,
    #     _delete_axis_0,
    #     _original_dtypes,
    #     _n_features_in,
    #     _feature_names_in,
    #     _total_counts_by_column,
    # )

    # random spot check _validation when accessing _make_instructinos
    @pytest.mark.parametrize('junk_value',
        (-1, 0, 1, 2.7, 'junk', np.nan, {1: 2})
    )
    def test_random_validation(self, junk_value, good_og_dtypes, good_tcbc):

        with pytest.raises(TypeError):
            _make_instructions(
                _count_threshold=100,
                _ignore_float_columns=True,
                _ignore_non_binary_integer_columns=True,
                _ignore_columns=junk_value,
                _ignore_nan=False,
                _handle_as_bool=[2,3],
                _delete_axis_0=False,
                _original_dtypes=good_og_dtypes,
                _n_features_in=len(good_og_dtypes),
                _feature_names_in=None,
                _total_counts_by_column=good_tcbc
            )

        with pytest.raises((TypeError, ValueError)):
            _make_instructions(
                _count_threshold=junk_value,
                _ignore_float_columns=True,
                _ignore_non_binary_integer_columns=True,
                _ignore_columns=[0,1],
                _ignore_nan=False,
                _handle_as_bool=[2,3],
                _delete_axis_0=False,
                _original_dtypes=good_og_dtypes,
                _n_features_in=len(good_og_dtypes),
                _feature_names_in=None,
                _total_counts_by_column=good_tcbc
            )

        with pytest.raises(TypeError):
            _make_instructions(
                _count_threshold=100,
                _ignore_float_columns=True,
                _ignore_non_binary_integer_columns=junk_value,
                _ignore_columns=[0,1],
                _ignore_nan=False,
                _handle_as_bool=[2,3],
                _delete_axis_0=False,
                _original_dtypes=good_og_dtypes,
                _n_features_in=len(good_og_dtypes),
                _feature_names_in=None,
                _total_counts_by_column=good_tcbc
            )

        # accepts all good
        _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[0,1],
            _ignore_nan=False,
            _handle_as_bool=[2,3],
            _delete_axis_0=False,
            _original_dtypes=good_og_dtypes,
            _n_features_in=len(good_og_dtypes),
            _feature_names_in=None,
            _total_counts_by_column=good_tcbc
        )

    # END random spot check validation ** * ** * ** * ** * ** * ** * **


    # TEST EDGE CASES ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    def test_ignore_all_columns_returns_all_inactive(
        self, good_tcbc, good_og_dtypes
    ):

        out = _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[0,1,2,3],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=good_og_dtypes,
            _n_features_in=len(good_og_dtypes),
            _feature_names_in=None,
            _total_counts_by_column=good_tcbc
        )

        assert out == {idx: ['INACTIVE'] for idx in range(4)}


    def test_empty_tcbcs_returns_all_inactive(self, good_og_dtypes):

        out = _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=good_og_dtypes,
            _n_features_in=len(good_og_dtypes),
            _feature_names_in=None,
            _total_counts_by_column={0:{}, 1:{}, 2:{}, 3:{}}
        )

        assert out == {idx: ['INACTIVE'] for idx in range(4)}


    def test_ignore_all_floats_returns_all_inactive(self, good_og_dtypes):

        _tcbc = {}
        for _ in range(4):
            _tcbc[_] = {
                np.random.uniform(0, 1): np.random.randint(0, 10)
                for i in range(10)
            }

        out = _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=np.array(['float' for _ in good_og_dtypes]),
            _n_features_in=len(good_og_dtypes),
            _feature_names_in=None,
            _total_counts_by_column=_tcbc
        )

        assert out == {idx: ['INACTIVE'] for idx in range(4)}


    def test_ignore_all_nonbinint_returns_all_inactive(self, good_og_dtypes):

        _len = range(len(good_og_dtypes))

        out = _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=np.array(['int' for _ in _len]),
            _n_features_in=len(good_og_dtypes),
            _feature_names_in=None,
            _total_counts_by_column={i: {1: 10, 2: 10, 3: 10} for i in _len}
        )

        assert out == {idx: ['INACTIVE'] for idx in range(4)}


    def test_DELETE_ALL_msg_for_all_floats(self):

        _tcbc = {}
        for _ in range(4):
            _tcbc[_] = {
                np.random.uniform(0, 1): np.random.randint(0, 10)
                for i in range(10)
            }

        out = _make_instructions(
            _count_threshold=100,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=np.array(['float' for _ in range(4)]),
            _n_features_in=4,
            _feature_names_in=None,
            _total_counts_by_column=_tcbc
        )

        for _instr in out.values():
            assert len(_instr) == 2
            assert _instr[-2] == 'DELETE ALL'
            assert _instr[-1] == 'DELETE COLUMN'


    @pytest.mark.parametrize('tcbc',
        (
            {0: {'a': 500}},
            {0: {'a': 475, np.nan: 25}},
            {0: {'a':250, 'b': 200, np.nan: 50}},
            {0: {'a': 250, 'b': 200, 'c': 25, np.nan: 25}}
        )
    )
    def test_rejects_str_into_hab(self, tcbc):

        with pytest.raises(ValueError):
            _make_instructions(
                _count_threshold=100,
                _ignore_float_columns=True,
                _ignore_non_binary_integer_columns=True,
                _ignore_columns=[],
                _ignore_nan=False,
                _handle_as_bool=np.array([0]),
                _delete_axis_0=False,
                _original_dtypes=np.array(['obj']),
                _n_features_in=1,
                _feature_names_in=None,
                _total_counts_by_column=tcbc
            )


    def test_a_column_of_all_nans(self):

        out = _make_instructions(
            _count_threshold=5,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=False,
            _original_dtypes=np.array(['float']),
            _n_features_in=1,
            _feature_names_in=None,
            _total_counts_by_column={0: {np.nan: 1194}}
        )

        assert out == {0: ['DELETE COLUMN']}

    # END TEST EDGE CASES ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_accuracy(self):

        # run of the mill integer data
        out = _make_instructions(
            _count_threshold=5,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=False,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=True,
            _original_dtypes=np.array(['int', 'int']),
            _n_features_in=2,
            _feature_names_in=None,
            _total_counts_by_column={
                0: {0: 6, 1: 4, 2: 6, 3: 4, 4: 6},
                1: {0: 4, 1: 5, 2: 4, 3: 5, 4: 4},
            }
        )

        assert out == {0: [1, 3], 1: [0, 2, 4]}

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a constant column
        out = _make_instructions(
            _count_threshold=5,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=True,
            _original_dtypes=np.array(['obj']),
            _n_features_in=1,
            _feature_names_in=None,
            _total_counts_by_column={0: {'a':100}}
        )

        # even tho _delete_axis_0 is True, not 'DELETE ALL' because
        # it is a constant column, which never has rows deleted.
        assert out == {0: ['DELETE COLUMN']}

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # a column where all but one of the values is deleted
        out = _make_instructions(
            _count_threshold=5,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=[],
            _ignore_nan=False,
            _handle_as_bool=[],
            _delete_axis_0=True,
            _original_dtypes=np.array(['obj']),
            _n_features_in=1,
            _feature_names_in=None,
            _total_counts_by_column={0: {'a':3, 'b': 9, 'c': 3, np.nan: 4}}
        )

        assert out == {0: ['a', 'c', np.nan, 'DELETE COLUMN']}




