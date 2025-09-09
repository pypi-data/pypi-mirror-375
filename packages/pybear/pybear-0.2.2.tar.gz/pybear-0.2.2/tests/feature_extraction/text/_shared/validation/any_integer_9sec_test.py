# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np

from pybear.feature_extraction.text.__shared._validation._any_integer import \
    _val_any_integer



class TestValAnyInteger:


    @staticmethod
    @pytest.fixture(scope='module')
    def _shorthand():

        def foo(_int, _min, _max, _disallowed, _can_be_bool, _can_be_None):
            """Helper function to make the code shorter."""
            _val_any_integer(
                _int=_int,
                _min=_min,
                _max=_max,
                _disallowed=_disallowed,
                _can_be_bool=_can_be_bool,
                _can_be_None=_can_be_None
            )

        return foo


    @pytest.mark.parametrize('_int',
        (None, 'trash', True, False, -10_000, -2.7, -1, 0, 1, 2.7, np.pi, 10_000))
    @pytest.mark.parametrize('_min', (float('-inf'), -1, float('-inf')))
    @pytest.mark.parametrize('_max', (float('-inf'), 1, float('-inf')))
    @pytest.mark.parametrize('_disallowed', ([-2, -1], [10_000]))
    @pytest.mark.parametrize('_can_be_bool', (True, False))
    @pytest.mark.parametrize('_can_be_None', (True, False))
    def test_accuracy_single(
        self, _shorthand, _int, _min, _max, _disallowed, _can_be_bool,
        _can_be_None
    ):

        _type_error = 0
        _value_error = 0

        while True:

            if _min > _max:
                _value_error += 1
                break
            elif _int is None:
                if not _can_be_None:
                    _type_error += 1
                break
            elif isinstance(_int, bool):
                if not _can_be_bool:
                    _type_error += 1
                    break
            elif not isinstance(_int, numbers.Integral):
                _type_error += 1
                break

            if _int < _min:
                _value_error += 1
            elif _int > _max:
                _value_error += 1
            elif _int in _disallowed:
                _value_error += 1

            break

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _value_error and not _type_error:
            with pytest.raises(ValueError):
                _shorthand(
                    _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
                )
        elif _type_error and not _value_error:
            with pytest.raises(TypeError):
                _shorthand(
                    _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
                )
        elif _type_error and _value_error:
            # shouldnt get in here
            raise Exception
        else:
            assert _shorthand(
                _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
            ) is None


    @pytest.mark.parametrize('_int',
        ([None, 0, 1], [-2.7, 2.7], [-10_000, np.pi, -1, False],
         [True, np.pi, 10_000])
    )
    @pytest.mark.parametrize('_min', (float('-inf'), -1, float('-inf')))
    @pytest.mark.parametrize('_max', (float('-inf'), 1, float('-inf')))
    @pytest.mark.parametrize('_disallowed', ([-2, -1], [10_000]))
    @pytest.mark.parametrize('_can_be_bool', (True, False))
    @pytest.mark.parametrize('_can_be_None', (True, False))
    def test_accuracy_sequence(
        self, _shorthand, _int, _min, _max, _disallowed, _can_be_bool,
        _can_be_None
    ):

        _type_error = 0
        _value_error = 0

        while True:

            if _min > _max:
                _value_error += 1
                break
            elif any(map(lambda x: x is None, _int)):
                if not _can_be_None:
                    _type_error += 1
                    break   # this must be under the if!

            # at this point, _int may have allowed Nones in it that will
            # screw up the calculations, so rebuild _int with no Nones
            # in it
            _int = [i for i in _int if i is not None]

            if any(map(lambda x: isinstance(x, bool), _int)):
                if not _can_be_bool:
                    _type_error += 1
                    break

            if not all(map(isinstance, _int, (numbers.Integral for _ in _int))):
                _type_error += 1
                break

            # these cannot be elif!
            if any(map(lambda x: x < _min, _int)):
                _value_error += 1
            if any(map(lambda x: x > _max, _int)):
                _value_error += 1
            if any(map(lambda x: x in _disallowed, _int)):
                _value_error += 1

            break

        # assertions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _value_error and not _type_error:
            with pytest.raises(ValueError):
                _shorthand(
                    _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
                )
        elif _type_error and not _value_error:
            with pytest.raises(TypeError):
                _shorthand(
                    _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
                )
        elif _type_error and _value_error:
            # shouldnt get in here
            raise Exception
        else:
            assert _shorthand(
                _int, _min, _max, _disallowed, _can_be_bool, _can_be_None
            ) is None






