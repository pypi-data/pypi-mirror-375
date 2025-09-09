# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np
from pybear.model_selection.autogridsearch._autogridsearch_wrapper. \
    _validation._params import _val_params



allowed_types = [
    'soft_float', 'hard_float', 'fixed_float', 'soft_integer',
    'hard_integer', 'fixed_integer', 'fixed_string', 'fixed_bool'
]



class TestParamsValidation:


    @pytest.mark.parametrize('non_iterable',
        (0, 1, True, None, np.pi, min, lambda x: x)
    )
    def test_rejects_non_iterable(self, non_iterable):
        with pytest.raises(TypeError):
            _val_params(non_iterable, 3)


    @pytest.mark.parametrize('non_dict',
        ('junk', [1, 2], [[1, 2]], (1, 2), {1, 2}, np.array([1, 2], dtype=int))
    )
    def test_rejects_non_dict(self, non_dict):
        with pytest.raises(TypeError):
            _val_params(non_dict, 3)


    @pytest.mark.parametrize('non_str',
        (0, 1, True, None, np.pi, min, {1, 2}, [1, 2], (1, 2), lambda x: x)
    )
    def test_reject_non_str_keys(self, non_str):
        with pytest.raises(TypeError):
            _val_params(
                {non_str: [[1, 2, 3], [3, 3, 3], 'hard_integer']},
                3
            )

        with pytest.raises(TypeError):
            _val_params(
                {non_str: [[1, 2, 3], [3, 3, 3], 'hard_integer'],
                 'b': [[1.1, 2.1, 3.1], [3, 3, 3], 'hard_float']},
                3
            )


    @pytest.mark.parametrize('junk_dict',
        ({'a': 1}, {'a': 'junk'}, {'a': {1, 2, 3}}, {'a': None})
    )
    def test_rejects_junk_dictionaries(self, junk_dict):
        with pytest.raises((TypeError, ValueError)):
            _val_params(junk_dict, 3)


    def test_accepts_dict(self, mock_estimator_params):
        assert _val_params(mock_estimator_params, 3) is None


    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            _val_params({}, 3)


    @pytest.mark.parametrize('total_passes', (2, 4))
    def test_rejects_bad_len(self, total_passes):

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [[1, 2, 3], [3, 3, 3]]}, total_passes
            )


@pytest.mark.parametrize('_type', allowed_types)
@pytest.mark.parametrize('total_passes', (1, 3))
class TestFirstGrid:


    @pytest.mark.parametrize('non_list_like',
        (0, np.pi, True, None, min, 'junk', lambda x: x, {'a': 1})
    )
    def test_rejects_non_list_like(
        self, non_list_like, total_passes, _type
    ):
        with pytest.raises(TypeError):
            _val_params(
                {'good_key': [non_list_like, [1]*total_passes, _type]},
                total_passes
            )


    @pytest.mark.parametrize('list_like', ([1,2,3], (1,2,3), {1,2,3}))
    def test_accepts_list_like(self, list_like, total_passes, _type):

        points = [3 for _ in range(total_passes)]

        if _type == 'fixed_string':
            list_like = type(list_like)(list(map(str, list_like)))
        elif _type == 'fixed_bool':
            list_like = type(list_like)([True, False, None])

        assert _val_params(
            {'good_key': [list_like, points, _type]},
            total_passes
        ) is None


    def test_rejects_empty(self, total_passes, _type):

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [[], [2 for _ in range(total_passes)], _type]},
                total_passes
            )


    def test_rejects_duplicate(self, total_passes, _type):

        if 'string' in _type:
            _bad_grid = list('aabc')
        elif 'bool' in _type:
            _bad_grid = [True, False, False, None]
        elif 'float' in _type:
            _bad_grid = [-np.e, np.e, np.e, np.pi]
        elif 'integer' in _type:
            _bad_grid = [0, 0, 1, 2]
        else:
            raise Exception

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [_bad_grid, [4 for _ in range(total_passes)], _type]},
                total_passes
            )


@pytest.mark.parametrize('_type', allowed_types)
@pytest.mark.parametrize('total_passes', (1, 3))
class TestPoints:


    @pytest.mark.parametrize('non_list_type',
        (np.pi, True, False, None, 'junk', {'a': 1}, lambda x: x)
    )
    def test_rejects_non_int_non_list_type(
        self, total_passes, _type, non_list_type
    ):

        with pytest.raises(TypeError):
            _val_params(
                {'good_key': [[1,2,3], non_list_type, _type]}, total_passes
            )


    @pytest.mark.parametrize('list_type', (list, tuple, np.array))
    def test_accepts_list_type(self, total_passes, list_type, _type):

        if _type == 'fixed_string':
            _grid = ['y', 'z', None]
        elif _type == 'fixed_bool':
            _grid = [True, False, None]
        else:
            _grid = [2, 4, 6]

        assert _val_params(
            {'good_key': [_grid, list_type([3]*total_passes), _type]},
            total_passes
        ) is None


    def test_rejects_points_len_ne_total_passes(self, total_passes, _type):

        if _type == 'fixed_string':
            _params = {
                'a': [list(map(str, [2,3,4,5])), [4,4,4], _type],
                'b': [list(map(str, np.logspace(0, 4))), [5,5,5,5], 'soft_float']
            }
        elif _type == 'fixed_bool':
            _params = {
                'a': [[True, False], [2,2,2], _type],
                'b': [[True, False, None], [2,2,2,2], 'soft_float']
            }
        else:
            _params = {
                'a': [[2,3,4,5], [4,4,4], _type],
                'b': [np.logspace(0, 4), [5,5,5,5], 'soft_float']
            }

        with pytest.raises(ValueError):
            _val_params(_params, total_passes)


    def test_rejects_none(self, total_passes, _type):

        with pytest.raises(TypeError):
            _val_params(
                {'good_key': [[1, 2], [None, 2, 2][:total_passes], _type]},
                total_passes
            )


    def test_accepts_integer_gte_one(self, total_passes, _type):

        if _type == 'fixed_string':
            _grid = list('123')
        elif _type == 'fixed_bool':
            _grid = [True, False, None]
        else:
            _grid = [99, 100, 101]

        assert _val_params(
            {'good_key': [_grid, 3, _type]},
            total_passes
        ) is None


    @pytest.mark.parametrize('bad_points', (-1, 0))
    def test_rejects_integer_less_than_one(
        self, _type, total_passes, bad_points
    ):

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [[1,2], bad_points, _type]}, total_passes
            )

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [[1,2], [2, bad_points], _type]}, total_passes
            )

        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [[1,2], [bad_points, 2], _type]}, total_passes
            )


@pytest.mark.parametrize('_type',
    ('fixed_integer', 'fixed_float', 'fixed_bool', 'fixed_string')
)
class TestPointsWhenFixed:


    @pytest.mark.parametrize('_points, total_passes',
         (
             (3, 1),
             (3, 3),
             ([3], 1),
             ([3,3,3], 3)
         )
    )
    def test_fixed_accepts_points_equals_len_grid(
        self, _type, _points, total_passes
    ):

        if _type == 'fixed_string':
            _grid = list('rst')
        elif _type == 'fixed_bool':
            _grid = [True, False, None]
        else:
            _grid = [1, 2, 3]

        assert _val_params(
            {'good_key': [_grid, _points, _type]}, total_passes
        ) is None


    @pytest.mark.parametrize('pass_num, _points, total_passes',
         (
             (1, 1, 1),
             (2, 1, 3),
             (3, [1], 1),
             (4, [3,1,1], 3),
             (5, [3,3,1], 3),
             (6, [3,1,3], 3),
             (7, [1,1,1], 3)
         )
    )
    def test_fixed_accepts_points_equals_1_after_first_pass(
        self, pass_num, _type, _points, total_passes
    ):

        if _type == 'fixed_string':
            _list_like = ['a', 'b', None]
        elif _type == 'fixed_bool':
            _list_like = [True, False, None]
        else:
            _list_like = [1, 2, 3]

        if pass_num in [6]:
            with pytest.raises(ValueError):
                _val_params(
                    {'good_key': [_list_like, _points, _type]}, total_passes
                )
        elif pass_num in [1, 2, 3, 4, 5, 7]:
            assert _val_params(
                {'good_key': [_list_like, _points, _type]}, total_passes
            ) is None


    @pytest.mark.parametrize('v1', (3, 4))
    @pytest.mark.parametrize('v2', (3, 4))
    @pytest.mark.parametrize('v3', (3, 4))
    def test_fixed_rejects_points_not_equal_len_grid_or_1(
        self, _type, v1, v2, v3
    ):

        # for points after first pass (first pass points is overwritten by
        # actual points in first grid)

        if v2 == 3 and v3 == 3:   # v1 can equal anything > 0
            # v1 will always be set to 3
            pytest.skip(reason=f"this combination will pass")

        with pytest.raises(ValueError):
            _val_params({'good_key': [[1 ,2, 3], 4, _type]}, 3)

        with pytest.raises(ValueError):
            _val_params({'good_key': [[1, 2, 3], [v1, v2, v3], _type]}, 3)


@pytest.mark.parametrize('_type', allowed_types)
class TestPointsAsInteger:


    def test_accepts_points_equals_len_grid(self, _type):

        # accepts first points == len(grid) and any other points elsewhere

        if _type == 'fixed_string':
            _grid = list(map(str, [11, 21, 31]))
        elif _type == 'fixed_bool':
            _grid = [True, False, None]
        else:
            _grid = [11, 21, 31]

        assert _val_params(
            {'good_key': [_grid, 3, _type]}, 3
        ) is None


    @pytest.mark.parametrize('v1', (2, 4, 5))
    def test_rejects_points_not_equal_len_grid(self, _type, v1):

        if _type == 'fixed_string' or _type == 'fixed_bool':
            with pytest.raises(ValueError):
                _val_params(
                    {'good_key': [[11, 21, 13], v1, _type]}, 3
                )
        elif 'hard' in _type:
            assert _val_params(
                {'good_key': [[11 ,21, 13], v1, _type]}, 3
            ) is None
        elif 'fixed' in _type:
            with pytest.raises(ValueError):
                _val_params(
                    {'good_key': [[11, 21, 13], v1, _type]}, 3
                )
        elif 'soft' in _type:
            if v1 != 2:
                assert _val_params(
                    {'good_key': [[11 ,21, 13], v1, _type]}, 3
                ) is None

            elif v1 == 2:
                with pytest.raises(ValueError):
                    _val_params(
                        {'good_key': [[11, 21, 13], v1, _type]}, 3
                    )
        else:
            raise Exception


class TestPointsAsListType:


    @pytest.mark.parametrize('_type',
        ('hard_integer', 'hard_float', 'soft_integer', 'soft_float'))
    @pytest.mark.parametrize('v1', (2, 3, 4, 5))
    @pytest.mark.parametrize('v2', (2, 3, 4, 5))
    @pytest.mark.parametrize('v3', (2, 3, 4, 5))
    def test_hard_soft_conditionally_accepts_any_points(
        self, v1, v2, v3, _type
    ):

        # soft rejects anywhere points == 2 but otherwise accepts any
        # of these values, _numerical_params always overwrites v1 with
        # actual points in first grid, and can accept any number in the
        # remaining positions

        if 'soft' in _type and (v1 == 2 or v2 == 2 or v3 == 2):
            with pytest.raises(ValueError):
                _val_params(
                    {'good_key': [[11, 12, 13], [v1, v2, v3], _type]},
                    3
                )
        else:
            assert _val_params(
                {'good_key': [[11, 12, 13], [v1, v2, v3], _type]}, 3
            ) is None



class TestType:


    @pytest.mark.parametrize('bad_param_type',
        (0, np.pi, True, None, min, lambda x: x, {'a': 1}, [1, ], (1,), {1, 2})
    )
    def test_rejects_any_non_string(self, bad_param_type):
        with pytest.raises(TypeError):
            _val_params(
                {'good_key': [['a', 'b'], None, bad_param_type]}, 2
            )


    @pytest.mark.parametrize('bad_string', ('junk', 'and', 'more_junk'))
    def test_rejects_bad_strings(self, bad_string):
        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [['a', 'b'], None, bad_string]}, 2
            )


    @pytest.mark.parametrize('bad_case',
        ('FIXED_INTEGER', 'FIXED_float', 'hard_INTEGER', 'HaRd_FlOaT',
         'sOfT_iNtEgEr', 'sofT_Float')
    )
    def test_rejects_bad_case(self, bad_case):
        with pytest.raises(ValueError):
            _val_params(
                {'good_key': [['a', 'b'], None, bad_case]}, 2
            )


    @pytest.mark.parametrize('good_type',
        ['fixed_integer', 'fixed_float', 'hard_integer',
        'hard_float', 'soft_integer', 'soft_float']
    )
    def test_accepts_valid_strings(self, good_type):
        assert _val_params(
            {'good_key': [[1, 2, 3], 3, good_type]}, 1
        ) is None






