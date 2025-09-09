# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _validation._total_counts_by_column import _val_total_counts_by_column



@pytest.fixture
def good_tcbc():
    return  {
        0: {'a': 3, 'b':2, 'c':5},
        1: {0:75, 1: 59},
        2: {3: 39, 2: 23, 1: 85, 0: 53}
}



class TestValTotalCountsByColumns:


    @pytest.mark.parametrize('_non_dict',
        (0, 3.14, True, None, 'junk', min, [1,2], (1,2), {1,2}, lambda x: x)
    )
    def test_type_error_non_dict(self, _non_dict):

        with pytest.raises(TypeError):
            _val_total_counts_by_column(_non_dict)


    @pytest.mark.parametrize('_junk_outer_key',
        (3.14, None, 'junk', min, (1,2), lambda x: x)
    )
    def test_type_error_non_integer_outer_keys(self, good_tcbc, _junk_outer_key):

        # for some reason, bools are getting thru TypeError part and being
        # caught by ValueError... might have something to do with pytest
        # fixtures. independently verified TypeError does catch bools.

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            bad_tcbc[_junk_outer_key] = bad_tcbc.pop(outer_key)

            with pytest.raises(TypeError):
                _val_total_counts_by_column(bad_tcbc)


    @pytest.mark.parametrize('_bad_outer_key', (-1, 100))
    def test_value_error_bad_outer_keys(self, good_tcbc, _bad_outer_key):

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            bad_tcbc[_bad_outer_key] = bad_tcbc[outer_key]
            del bad_tcbc[outer_key]

            with pytest.raises(ValueError):
                _val_total_counts_by_column(bad_tcbc)


    @pytest.mark.parametrize('_junk_inner_dict',
        (3.14, True, None, 'junk', min, [1,2], (1,2), lambda x: x)
    )
    def test_type_error_values_must_be_dict(self, good_tcbc, _junk_inner_dict):

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            bad_tcbc[outer_key] = _junk_inner_dict

            with pytest.raises(TypeError):
                _val_total_counts_by_column(bad_tcbc)


    @pytest.mark.parametrize('_junk_inner_dict_key', ((1,2,3,4), ('a','b','c')))
    def test_type_error_inner_key_sequence(self, good_tcbc, _junk_inner_dict_key):

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            _first_inner_key = list(bad_tcbc[outer_key])[0]
            bad_tcbc[outer_key][_junk_inner_dict_key] = \
                bad_tcbc[outer_key].pop(_first_inner_key)

            with pytest.raises(TypeError):
                _val_total_counts_by_column(bad_tcbc)


    # inner values must be int
    @pytest.mark.parametrize('_junk_inner_dict_value',
        (3.14, True, None, 'junk', min, [1,2], (1,2), {1,2}, {'a':1}, lambda x: x)
    )
    def test_type_error_inner_values_not_int(
        self, good_tcbc, _junk_inner_dict_value
    ):

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            bad_tcbc[outer_key][list(bad_tcbc[outer_key])[0]] = \
                _junk_inner_dict_value

            with pytest.raises(TypeError):
                _val_total_counts_by_column(bad_tcbc)


    @pytest.mark.parametrize('_bad_inner_dict_value', (-2, -1))
    def test_value_error_bad_inner_values(self, good_tcbc, _bad_inner_dict_value):

        for outer_key in good_tcbc:

            bad_tcbc = deepcopy(good_tcbc)
            _first_inner_key = list(bad_tcbc)[0]
            bad_tcbc[outer_key][_first_inner_key] = _bad_inner_dict_value

            with pytest.raises(ValueError):
                _val_total_counts_by_column(bad_tcbc)


    def test_accepts_good_tcbc(self, good_tcbc):
        assert _val_total_counts_by_column(good_tcbc) is None


    def test_accepts_empty_inner_dicts(self):
        good_tcbc = {0: {'a':25, 'b':10}, 1: {}, 2:{}, 3: {0: 17, 1:28}}
        assert _val_total_counts_by_column(good_tcbc) is None




