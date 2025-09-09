# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import uuid

import numpy as np
import pandas as pd

from pybear.preprocessing._MinCountTransformer._validation. \
    _ignore_columns_handle_as_bool import _val_ignore_columns_handle_as_bool



class TestValIgnoreColumns:


    @staticmethod
    @pytest.fixture(scope='module')
    def full_allowed():
        return ['None', 'callable', 'Sequence[int]', 'Sequence[str]']


    # helper param validation ** * ** * ** * ** * ** * ** * ** * ** * **

    # _name -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_name',
        (-2, 0, 1, np.pi, True, None, min, [0, 1], {'a':1}, lambda x: x)
    )
    def test_reject_junk_name(self, junk_name):
        with pytest.raises(AssertionError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, 2, 3],
                junk_name,
                ['Sequence[int]'],
                4,
                None
            )


    @pytest.mark.parametrize('bad_name', ('lemon', 'lime', 'orange'))
    def test_reject_bad_name(self, bad_name):
        with pytest.raises(AssertionError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, 2, 3],
                bad_name,
                ['Sequence[int]'],
                4,
                None
            )


    @pytest.mark.parametrize('good_name', ('ignore_columns', 'handle_as_bool'))
    def test_accepts_good_name(self, good_name):

        _val_ignore_columns_handle_as_bool(
            [0, 1, 2, 3],
            good_name,
            ['Sequence[int]'],
            4,
            None
        )

    # END _name -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # _allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_allowed',
        (-2, 0, 1, np.pi, True, None, min, [0, 1], {'a':1}, lambda x: x)
    )
    def test_reject_junk_allowed(self, junk_allowed):
        with pytest.raises(TypeError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, 2, 3],
                'ignore_columns',
                junk_allowed,
                4,
                None
            )


    @pytest.mark.parametrize('bad_allowed', (['lemon', 'lime', 'orange'], []))
    def test_reject_bad_allowed(self, bad_allowed):

        # notice that its testing an empty

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, 2, 3],
                'handle_as_bool',
                bad_allowed,
                4,
                None
            )


    @pytest.mark.parametrize('container', (list, set, tuple, np.array))
    def test_accepts_good_allowed(self, container, full_allowed):

        _val_ignore_columns_handle_as_bool(
            [0, 1, 2, 3],
            'handle_as_bool',
            container(full_allowed),
            4,
            None
        )

    # END _allowed -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # END helper param validation ** * ** * ** * ** * ** * ** * ** * **



    @pytest.mark.parametrize('junk_value',
        (-2.7, -1, 0, 1, 2.7, np.pi, True, 'junk', {'a': 1})
    )
    def test_rejects_junk_value(self, junk_value, full_allowed):

        with pytest.raises(TypeError):
            _val_ignore_columns_handle_as_bool(
                junk_value,
                'handle_as_bool',
                deepcopy(full_allowed),
                _n_features_in=4,
                _feature_names_in=np.array(list('abcd'))
            )


    def test_rejects_bad_value(self, full_allowed):

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                [[0,1,2], [3,4,5]],
                'handle_as_bool',
                deepcopy(full_allowed),
                _n_features_in=4,
                _feature_names_in=np.array(list('abcd'))
            )


    def test_accepts_empty_listlike_value(self, full_allowed):

        _val_ignore_columns_handle_as_bool(
            [],
            'ignore_columns',
            full_allowed,
            _n_features_in=4,
            _feature_names_in=np.array(list('abcd'))
        )


    @pytest.mark.parametrize('fxn_type', ('def', 'lambda'))
    def test_ignore_columns_accepts_callable(self, fxn_type, full_allowed):

        def _dum_fxn(X):
            return [0,1]

        if fxn_type == 'def':
            _fxn = _dum_fxn
        elif fxn_type == 'lambda':
            _fxn = lambda X: [0, 1]
        else:
            raise Exception

        out = _val_ignore_columns_handle_as_bool(
            _fxn,
            'handle_as_bool',
            full_allowed,
            _n_features_in=4,
            _feature_names_in= np.array(['a', 'b', 'c', 'd'], dtype='<U1')
        )

        assert out is None


    @pytest.mark.parametrize('_fni',
        (None, np.array(['a', 'b', 'c', 'd'], dtype='<U1'))
    )
    def test_value_accepts_None(self, _fni, full_allowed):

        out = _val_ignore_columns_handle_as_bool(
            None,
            'ignore_columns',
            full_allowed,
            _n_features_in=4,
            _feature_names_in=_fni
        )

        assert out is None


    @pytest.mark.parametrize('list_like',
        (list('abcd'), set('abcd'), tuple('abcd'),
        np.array(list('abcd'), dtype='<U1'))
    )
    def test_value_accepts_list_like(self, list_like, full_allowed):
        out = _val_ignore_columns_handle_as_bool(
            list_like,
            'handle_as_bool',
            full_allowed,
            _n_features_in=4,
            _feature_names_in=np.array(['a', 'b', 'c', 'd'], dtype='<U1')
        )

        assert out is None


    @pytest.mark.parametrize('duplicate_values', (list('aacd'), (0, 1, 2, 2, 3)))
    def test_rejects_duplicate_values(self, duplicate_values, full_allowed):
        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                duplicate_values,
                'handle_as_bool',
                full_allowed,
                _n_features_in=4,
                _feature_names_in=np.array(['a', 'b', 'c', 'd'], dtype='<U1')
            )


    # test values in list-like ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('junk_value',
        (True, False, np.pi, None, min, [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    @pytest.mark.parametrize('_fni', (None, np.array(['a'])))
    def test_rejects_non_int_not_str_in_list_type(
        self, junk_value, _fni, full_allowed
    ):
        with pytest.raises((TypeError, ValueError)):
            _val_ignore_columns_handle_as_bool(
                [junk_value],
                'ignore_columns',
                full_allowed,
                _n_features_in=1,
                _feature_names_in=_fni
            )


    @pytest.mark.parametrize('_fni', (None, np.array(list('abcde'))))
    def test_rejects_nanlike_in_list_type(self, _fni, full_allowed):

        with pytest.raises(TypeError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, np.nan],
                'ignore_columns',
                full_allowed,
                _n_features_in=5,
                _feature_names_in=_fni
            )


        with pytest.raises(TypeError):
            _val_ignore_columns_handle_as_bool(
                [pd.NA, 2],
                'ignore_columns',
                full_allowed,
                _n_features_in=5,
                _feature_names_in=_fni
            )


    @pytest.mark.parametrize('_fni', (None, np.array(list('abcd'))))
    def test_reject_list_types_of_different_types(
        self, _fni, full_allowed,
    ):

        with pytest.raises(TypeError):
            _val_ignore_columns_handle_as_bool(
                ['a', 'b', 3, 4],
                'handle_as_bool',
                full_allowed,
                _n_features_in=4,
                _feature_names_in=_fni
            )


    def test_value_error_idx_out_of_bounds(self, full_allowed):

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                [0, 1, 2, 3],
                'ignore_columns',
                full_allowed,
                3,
                None
            )

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                [-4, -3, -2],
                'handle_as_bool',
                full_allowed,
                3,
                None
            )


    def test_value_error_column_names_passed_when_no_fni(self, full_allowed):

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                ['a', 'b', 'c', 'd'],
                'ignore_columns',
                full_allowed,
                4,
                None
            )


    def test_value_error_col_name_not_in_feature_names(self, full_allowed):

        feature_names_in = np.array(['a', 'b', 'c', 'd'], dtype='<U1')

        with pytest.raises(ValueError):
            _val_ignore_columns_handle_as_bool(
                ['e'],
                'handle_as_bool',
                full_allowed,
                4,
                feature_names_in
            )

    # END test values in list-like ** * ** * ** * ** * ** * ** * ** * **



    def test_differentiates_str_and_int_values(self, full_allowed):

        # this shouldnt pass if is assessed as 'int'
        _val_ignore_columns_handle_as_bool(
            ['4890', '1089', '4821', '1243'],
            'handle_as_bool',
            ['Sequence[str]'],
            4,
            ['4890', '1089', '4821', '1243']
        )

        _val_ignore_columns_handle_as_bool(
            [4890, 1089, 4821, 1243],
            'handle_as_bool',
            ['Sequence[int]'],
            10000,
            None
        )


    @pytest.mark.parametrize('given_value',
        ('callable', 'list-str', 'list-int', 'none')
    )
    @pytest.mark.parametrize('name', ('ignore_columns', 'handle_as_bool'))
    @pytest.mark.parametrize('fni', ('passed', None))
    def test_allowed(self, given_value, name, fni):

        # skip other incidental trip-ups
        if given_value == 'list-str' and fni is None:
            pytest.skip(f"will fail for reason beyond the scope of this test")


        _n_features_in = 4

        _fni = [str(uuid.uuid4())[:4] for _ in range(_n_features_in)]

        _allowed_allowed = ['callable', 'None', 'Sequence[int]', 'Sequence[str]']

        if given_value == 'callable':
            _value = lambda X: [0, 1]
        elif given_value == 'list-int':
            _value = [0, 2]
        elif given_value == 'list-str':
            _value = _fni[:2]
        elif given_value == 'none':
            _value = None
        else:
            raise Exception




        # run a bunch of trials with random settings

        for trial in range(50):

            _len = int(np.random.randint(1, 5))
            _allowed = np.random.choice(_allowed_allowed, _len, replace=False)

            will_raise = False
            if given_value == 'callable' and 'callable' not in _allowed:
                will_raise = True
            elif given_value == 'none' and 'None' not in _allowed:
                will_raise = True
            elif given_value == 'list-str' and 'Sequence[str]' not in _allowed:
                will_raise = True
            elif given_value == 'list-int' and 'Sequence[int]' not in _allowed:
                will_raise = True

            if will_raise:
                with pytest.raises(ValueError):
                    _val_ignore_columns_handle_as_bool(
                        _value,
                        name,
                        _allowed,
                        _n_features_in,
                        _fni if fni=='passed' else None
                    )
            else:
                _val_ignore_columns_handle_as_bool(
                    _value,
                    name,
                    _allowed,
                    _n_features_in,
                    _fni if fni=='passed' else None
                )



