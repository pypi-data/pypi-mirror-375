# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._InterceptManager._shared._make_instructions \
    import _make_instructions



class TestMakeInstructions:

    # def _make_instructions(
    #     _keep: KeepType,
    #     constant_columns_: ConstantColumnsType,
    #     _n_features_in: int
    # ) -> InstructionType:


    def test_accuracy(self, _shape):

        _constant_columns_1 = {0: 1, 8: 1}  # must have index 8 in it
        assert max(_constant_columns_1) < _shape[1]

        _constant_columns_2 = {1: 1, 0: 0, 8: 1}  # must have index 8 in it
        assert max(_constant_columns_2) < _shape[1]

        _keep_dict = {'Intercept': 1}

        _keep_int = _shape[1] - 2  # not arbitrary, must equal 8


        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # keep is int ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # if no constant columns, returns all Nones
        out = _make_instructions(_keep_int, {}, _shape[1])
        assert out == {'keep': None, 'delete': None, 'add': None}

        # keep _keep_int idx, delete all others
        out = _make_instructions(_keep_int, _constant_columns_1, _shape[1])
        _sorted = sorted(list(_constant_columns_1))
        _sorted.remove(_keep_int)
        assert out == {'keep': [_keep_int], 'delete': _sorted, 'add': None}
        del _sorted

        # keep _keep_int idx, delete all others
        out = _make_instructions(_keep_int, _constant_columns_2, _shape[1])
        _sorted = sorted(list(_constant_columns_2))
        _sorted.remove(_keep_int)
        assert out == {'keep': [_keep_int], 'delete': _sorted, 'add': None}
        del _sorted
        # END keep is int ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # 'none' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # if no constant columns, returns all Nones
        out = _make_instructions('none', {}, _shape[1])
        assert out == {'keep': None, 'delete': None, 'add': None}

        # delete all constant columns
        out = _make_instructions('none', _constant_columns_1, _shape[1])
        assert out == {
            'keep': None,
            'delete': sorted(list(_constant_columns_1)),
            'add': None
        }

        # delete all constant columns
        out = _make_instructions('none', _constant_columns_2, _shape[1])
        assert out == {
            'keep': None,
            'delete': sorted(list(_constant_columns_2)),
            'add': None
        }
        # END 'none' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # dict ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # if no constant columns, returns all Nones except 'add'
        out = _make_instructions(_keep_dict, {}, _shape[1])
        assert out == {'keep': None, 'delete': None, 'add': _keep_dict}

        # delete all constant columns, append contents of keep dict
        out = _make_instructions(_keep_dict, _constant_columns_1, _shape[1])
        assert out == {
            'keep': None,
            'delete': sorted(list(_constant_columns_1)),
            'add': _keep_dict
        }

        # delete all constant columns, append contents of keep dict
        out = _make_instructions(_keep_dict, _constant_columns_2, _shape[1])
        assert out == {
            'keep': None,
            'delete': sorted(list(_constant_columns_2)),
            'add': _keep_dict
        }
        # END dict ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_all_columns_constant(self):

        # if all columns are constant and not appending new constants, raise
        with pytest.raises(ValueError):
            _make_instructions(
                _keep='none',
                constant_columns_=dict((zip(range(5), (1 for _ in range(5))))),
                _n_features_in=5
            )

        # if all columns are constant but appending new constants, warn
        with pytest.warns():
            out = _make_instructions(
                _keep={'Intercept': 1},
                constant_columns_=dict((zip(range(5), (1 for _ in range(5))))),
                _n_features_in=5
            )

            assert out['keep'] == None
            assert out['delete'] == list(range(5))
            assert out['add'] == {'Intercept': 1}




