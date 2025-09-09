# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# Test basic validation and accuracy for some rigged test cases. For the
# actual appearance of the printouts, see the sandbox file
# _repr_instructions_sandbox.


import pytest

from pybear.preprocessing._MinCountTransformer._print_instructions. \
    _repr_instructions import _repr_instructions



class TestReprInstructions:


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _n_features_in is validated by _val_delete_instr, which is tested
    # elsewhere.

    # _feature_names_in is validated by _val_feature_names_in, which is tested
    # elsewhere.

    # _delete_instr is validated by _val_delete_instr, # which is tested
    # elsewhere.

    # _total_counts_by_column is validated by _val_total_counts_by_column,
    # which is tested elsewhere.

    # _thresholds is validated by _val_count_threshold, which is tested elsewhere.


    # clean_printout -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_clean_printout',
        (-1, 0, 1, None, 'trash', [0,1], (0,1), {0,1}, {'a':1}, lambda x: 1)
    )
    def test_rejects_junk_clean_printout(self, junk_clean_printout):
        with pytest.raises(TypeError):
            _repr_instructions(
                _delete_instr={0: []},
                _total_counts_by_column={0: {'a':10, 'b':20}},
                _thresholds=15,
                _n_features_in=1,
                _feature_names_in=None,
                _clean_printout=junk_clean_printout,
                _max_char=80
            )


    @pytest.mark.parametrize('clean_printout', (True, False))
    def test_bool_clean_printout(self, clean_printout):

        _repr_instructions(
            _delete_instr={0: []},
            _total_counts_by_column={0: {'a':10, 'b':20}},
            _thresholds=10,
            _n_features_in=1,
            _feature_names_in=None,
            _clean_printout=clean_printout,
            _max_char=80
        )
    # END clean_printout -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # max_char -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_max_char',
        (-2.7, 2.7, None, 'trash', [0,1], (0,1), {0,1}, {'a':1}, lambda x: 1)
    )
    def test_rejects_junk_max_char(self, junk_max_char):

        with pytest.raises(TypeError):
            _repr_instructions(
                _delete_instr={0: []},
                _total_counts_by_column={0: {'a':10, 'b':20}},
                _thresholds=15,
                _n_features_in=1,
                _feature_names_in=None,
                _clean_printout=True,
                _max_char=junk_max_char
            )


    @pytest.mark.parametrize('bad_max_char', (-1, 0, 10, 20000))
    def test_bad_max_char(self, bad_max_char):

        with pytest.raises(ValueError):
            _repr_instructions(
                _delete_instr={0: []},
                _total_counts_by_column={0: {'a':10, 'b':20}},
                _thresholds=15,
                _n_features_in=1,
                _feature_names_in=None,
                _clean_printout=True,
                _max_char=bad_max_char
            )


    @pytest.mark.parametrize('good_max_char', (80, 110))
    def test_good_max_char(self, good_max_char):

        _repr_instructions(
            _delete_instr={0: []},
            _total_counts_by_column={0: {'a':10, 'b':20}},
            _thresholds=15,
            _n_features_in=1,
            _feature_names_in=None,
            _clean_printout=True,
            _max_char=good_max_char
        )

    # END max_char -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def test_catches_len_tcbc_not_equal_n_features_in(self):

        with pytest.raises(AssertionError):
            _repr_instructions(
                _delete_instr={0: []},
                _total_counts_by_column={0: {'a':10, 'b':20}, 1: {1: 30}},
                _thresholds=15,
                _n_features_in=1,
                _feature_names_in=None,
                _clean_printout=True,
                _max_char=99
            )


    @pytest.mark.parametrize('thresholds', (2, [2, 3]))
    def test_accept_int_or_list_thresholds(self, thresholds):

        _repr_instructions(
            _delete_instr={0: [], 1: []},
            _total_counts_by_column={0: {'a':10, 'b':20}, 1: {'c': 5, 'd': 15}},
            _thresholds=thresholds,
            _n_features_in=2,
            _feature_names_in=None,
            _clean_printout=True,
            _max_char=100
        )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # v v v v v v v v ACCURACY v v v v v v v v v v v v v v v v v v v v

    # no need to test all the machinery of MCT by actually running it.
    # just make rigged _delete_instr / _tcbc and confirm output.


    def test_case_1(self):

        # 'INACTIVE' prints 'Ignored.'

        out = _repr_instructions(
            _delete_instr={0: ['INACTIVE']},
            _total_counts_by_column={0: {'a':10, 'b':20, 'c': 30}},
            _thresholds=15,
            _n_features_in=1,
            _feature_names_in=None,
            _clean_printout=True,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) Column 1 (15)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith('Ignored.')


    def test_case_2(self):

        # empty prints 'No operations.'

        out = _repr_instructions(
            _delete_instr={0: []},
            _total_counts_by_column={0: {'a':10, 'b':20, 'c': 30}},
            _thresholds=5,
            _n_features_in=1,
            _feature_names_in=['pybear_feature'],
            _clean_printout=True,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) pybear_feature (5)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith('No operations.')


    def test_case_3(self):

        # 'DELETE COLUMN'

        out = _repr_instructions(
            _delete_instr={0: ['DELETE COLUMN']},
            _total_counts_by_column={0: {'a':10, 'b':20}},
            _thresholds=15,
            _n_features_in=1,
            _feature_names_in=['ABC'],
            _clean_printout=False,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 2
        # there should always be 2 char gap
        _exp_desc = f"0) ABC (15)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith('Delete column.')
        assert out[1].endswith('All columns will be deleted.')


    def test_case_4(self):

        # 'DELETE COLUMN' with some rows also deleted

        out = _repr_instructions(
            _delete_instr={0: ['a', 'DELETE COLUMN']},
            _total_counts_by_column={0: {'a':10, 'b':20}},
            _thresholds=15,
            _n_features_in=1,
            _feature_names_in=['XYZ'],
            _clean_printout=False,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 2
        # there should always be 2 char gap
        _exp_desc = f"0) XYZ (15)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert "Delete rows containing a" in out[0]
        assert out[0].endswith('Delete column.')
        assert out[1].endswith('All columns will be deleted.')


    def test_case_5(self):

        # All are deleted the old-fashioned way, pre-'DELETE ALL',
        # instr_list is full of all unique values.

        out = _repr_instructions(
            _delete_instr={0: ['a', 'b', 'c']},
            _total_counts_by_column={0: {'a':10, 'b':20, 'c': 8}},
            _thresholds=30,
            _n_features_in=1,
            _feature_names_in=['this_name_should_get_truncated'],
            _clean_printout=True,
            _max_char=72
        )

        assert isinstance(out, list)
        assert len(out) == 2
        # there should always be 2 char gap
        _exp_desc = f"0) this_name_should_get_t... (30)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith(f"All rows will be deleted. " )
        assert out[1].endswith(f"All rows are guaranteed to be deleted.")


    def test_case_6(self):

        # 'DELETE ALL' & 'DELETE COLUMN'
        # (if 'DELETE ALL' is in 'DELETE COLUMN' must be in)
        # 'DELETE ALL' only prints f"All rows will be deleted. "

        out = _repr_instructions(
            _delete_instr={0: ['DELETE ALL', 'DELETE COLUMN']},
            _total_counts_by_column={0: {'a':10, 'b':20}},
            _thresholds=100,
            _n_features_in=1,
            _feature_names_in=['Column 1'],
            _clean_printout=False,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 3
        # there should always be 2 char gap
        _exp_desc = f"0) Column 1 (100)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith(f"All rows will be deleted. Delete column." )
        assert out[1].endswith(f"All columns will be deleted.")
        assert out[2].endswith(f"All rows are guaranteed to be deleted.")


    def test_case_7(self):

        # delete less than all uniques

        out = _repr_instructions(
            _delete_instr={0: ['a', 'c']},
            _total_counts_by_column={0: {'a':10, 'b':30, 'c':20, 'd': 40}},
            _thresholds=25,
            _n_features_in=1,
            _feature_names_in=['ABC'],
            _clean_printout=False,
            _max_char=100
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) ABC (25)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert "Delete rows containing a, c." in out[0]


    def test_case_8(self):

        # deleting long name values with clean_printout

        out = _repr_instructions(
            _delete_instr={
                0: ['this_is_long', 'this_is_even_longer', 'still_pretty_long']
            },
            _total_counts_by_column={
                0: {
                    'this is long':10,
                    'this is even longer':20,
                    'still pretty long':30,
                    'd': 40,
                    'e': 50
                }
            },
            _thresholds=35,
            _n_features_in=1,
            _feature_names_in=['my feature'],
            _clean_printout=True,
            _max_char=80
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) my feature (35)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert "Delete rows containing this_is_long, ... + 2 other(s)." in out[0]


    def test_case_9(self):

        # a super duper long name

        out = _repr_instructions(
            _delete_instr={0: ['this is a super duper wicked long value']},
            _total_counts_by_column={
                0: {
                    'this is a super duper wicked long value':10,
                    'a': 20,
                    'b': 30,
                    'c': 30,
                    'd': 40,
                    'e': 50
                }
            },
            _thresholds=15,
            _n_features_in=1,
            _feature_names_in=['the crazy feature'],
            _clean_printout=True,
            _max_char=80
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) the crazy feature (15)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith(f"Delete 1 of 6 uniques. ")


    def test_case_10(self):

        # all values can be displayed

        out = _repr_instructions(
            _delete_instr={0: ['a', 'b', 'c']},
            _total_counts_by_column={0: {'a':10, 'b':20, 'c': 30, 'd': 40, 'e': 50}},
            _thresholds=35,
            _n_features_in=1,
            _feature_names_in=None,
            _clean_printout=True,
            _max_char=120
        )

        assert isinstance(out, list)
        assert len(out) == 1
        # there should always be 2 char gap
        _exp_desc = f"0) Column 1 (35)"
        _desc_len = len(_exp_desc)
        assert out[0].startswith(_exp_desc)
        assert out[0][_desc_len] == ' '
        assert out[0][_desc_len+1] == ' '
        assert out[0][_desc_len+2] != ' '
        assert out[0].endswith("Delete rows containing a, b, c. ")




