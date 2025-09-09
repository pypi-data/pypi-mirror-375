# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing import MinCountTransformer as MCT


class TestSetParams:


    @staticmethod
    @pytest.fixture(scope='module')
    def _kwargs(_shape):
        return {
            'count_threshold': _shape[0] // 20,
            'ignore_float_columns': True,
            'ignore_non_binary_integer_columns': True,
            'ignore_columns': None,
            'ignore_nan': True,
            'handle_as_bool': None,
            'delete_axis_0': True,
            'reject_unseen_values': False,
            'max_recursions': 1
        }


    @staticmethod
    @pytest.fixture(scope='module')
    def _alt_kwargs(_shape):

        return {
            'count_threshold': _shape[0] // 10,
            'ignore_float_columns': False,
            'ignore_non_binary_integer_columns': False,
            'ignore_columns': [0, 1],
            'ignore_nan': False,
            'handle_as_bool': [2, 3],
            'delete_axis_0': False,
            'reject_unseen_values': True,
            'max_recursions': 1,  # make life easier, dont do 2+ here
        }

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_blocks_some_params_after_fit(self, X_np, y_np, _kwargs):

        # INITIALIZE
        TestCls = MCT(**_kwargs)

        # CAN SET ANYTHING BEFORE FIT
        TestCls.set_params(**_kwargs)

        # everything is open after fit except 'max_recursions', and ic/hab
        # cannot be set to callable.
        TestCls.fit(X_np, y_np)

        TestCls.set_params(count_threshold=66)
        assert getattr(TestCls, 'count_threshold') == 66
        TestCls.set_params(ignore_float_columns=False)
        assert getattr(TestCls, 'ignore_float_columns') is False
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        TestCls.set_params(ignore_columns=[0, 1])
        assert getattr(TestCls, 'ignore_columns') == [0, 1]
        TestCls.set_params(ignore_columns=None)
        assert getattr(TestCls, 'ignore_columns') is None
        with pytest.warns():  # callable -> no-op with warn
            TestCls.set_params(ignore_columns=lambda x: [2, 3])
        assert getattr(TestCls, 'ignore_columns') is None  # did not change
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        TestCls.set_params(handle_as_bool=[0, 1])
        assert getattr(TestCls, 'handle_as_bool') == [0, 1]
        TestCls.set_params(handle_as_bool=None)
        assert getattr(TestCls, 'handle_as_bool') is None
        with pytest.warns():  # callable -> no-op with warn
            TestCls.set_params(ignore_columns=lambda x: [2, 3])
        assert getattr(TestCls, 'handle_as_bool') is None  # did not change
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        TestCls.set_params(ignore_nan=False)
        assert getattr(TestCls, 'ignore_nan') == False
        TestCls.set_params(delete_axis_0=3)
        assert getattr(TestCls, 'delete_axis_0') == 3
        TestCls.set_params(reject_unseen_values=3)
        assert getattr(TestCls, 'reject_unseen_values') == 3
        with pytest.warns():  # max_recursions -> no-op with warn
            TestCls.set_params(max_recursions=3)
        assert TestCls.max_recursions == 1  # did not change


    def test_fitted_max_rcr_over_one_blocks(self, X_np, y_np, _kwargs, _alt_kwargs):

        # everything blocked after fit with max_recursions >=2
        # can only do fit_transform when 2+ recursions

        # INITIALIZE
        TestCls = MCT(**_kwargs)

        # CAN SET ANYTHING BEFORE FIT
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['max_recursions'] = 2
        TestCls.set_params(**_new_kwargs)

        TestCls.fit_transform(X_np, y_np)

        # should always except whenever set_params on anything
        for param, value in _kwargs.items():

            with pytest.raises(ValueError):
                TestCls.set_params(**{param: value})

        # nothing should have changed, should all be the original values
        for param, value in _new_kwargs.items():

            assert getattr(TestCls, param) == value


    def test_max_recursions_blocked(self, X_np, y_np, _kwargs):

        # max_recursions always blocked

        # INITIALIZE
        TestCls = MCT(**_kwargs)

        # CAN SET ANYTHING BEFORE FIT
        TestCls.set_params(max_recursions=2)
        assert TestCls.max_recursions == 2

        TestCls.set_params(max_recursions=1)
        assert TestCls.max_recursions == 1

        TestCls.fit(X_np, y_np)

        with pytest.warns():
            TestCls.set_params(max_recursions=2)
        assert TestCls.max_recursions == 1

        TestCls.transform(X_np, y_np)

        with pytest.warns():
            TestCls.set_params(max_recursions=2)
        assert TestCls.max_recursions == 1


    def test_equality_set_params_before_and_after_fit(
        self, X_np, y_np, _kwargs, _alt_kwargs, mmct
    ):

        # test the equality of the data output under:
        # 1) set_params(via init) -> fit -> transform
        # 2) fit -> set_params -> transform

        # set_params(via init) -> fit -> transform
        FirstTestClass = MCT(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(FirstTestClass, param) == value
        FirstTestClass.fit(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(FirstTestClass, param) == value
        FIRST_TRFM_X, FIRST_TRFM_Y = FirstTestClass.transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(FirstTestClass, param) == value
        del FirstTestClass


        # fit -> set_params -> transform
        # all different params to start
        SecondTestClass = MCT(**_alt_kwargs)
        for param, value in _alt_kwargs.items():
            assert getattr(SecondTestClass, param) == value
        SecondTestClass.fit(X_np, y_np)
        for param, value in _alt_kwargs.items():
            assert getattr(SecondTestClass, param) == value
        SECOND_TRFM_X, SECOND_TRFM_Y = SecondTestClass.transform(X_np, y_np)
        for param, value in _alt_kwargs.items():
            assert getattr(SecondTestClass, param) == value

        # should not be equal to first transform
        assert not np.array_equal(FIRST_TRFM_X, SECOND_TRFM_X)
        assert not np.array_equal(FIRST_TRFM_Y, SECOND_TRFM_Y)

        # all params are being changed back to those in FirstTestClass
        SecondTestClass.set_params(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(SecondTestClass, param) == value
        THIRD_TRFM_X, THIRD_TRFM_Y = SecondTestClass.transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(SecondTestClass, param) == value
        del SecondTestClass

        # CHECK OUTPUT EQUAL REGARDLESS OF WHEN SET_PARAMS
        assert np.array_equiv(FIRST_TRFM_X, THIRD_TRFM_X)
        assert np.array_equiv(FIRST_TRFM_Y, THIRD_TRFM_Y)


        # VERIFY transform AGAINST REFEREE OUTPUT WITH SAME INPUTS
        MOCK_X = mmct().trfm(
            X_np,
            None,
            _kwargs['ignore_columns'],
            _kwargs['ignore_nan'],
            _kwargs['ignore_non_binary_integer_columns'],
            _kwargs['ignore_float_columns'],
            _kwargs['handle_as_bool'],
            _kwargs['delete_axis_0'],
            _kwargs['count_threshold']
        )

        assert np.array_equiv(FIRST_TRFM_X.astype(str), MOCK_X.astype(str))

        del MOCK_X


    def test_set_params_between_fit_transforms(
        self, X_np, y_np, _kwargs, _alt_kwargs, mmct
    ):

        # only with max_recursions == 1

        # fit_transform
        FirstTestClass = MCT(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(FirstTestClass, param) == value
        FIRST_TRFM_X, FIRST_TRFM_Y = \
            FirstTestClass.fit_transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(FirstTestClass, param) == value

        # fit_transform -> set_params -> fit_transform
        SecondTestClass = MCT(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(SecondTestClass, param) == value
        SecondTestClass.set_params(**_alt_kwargs)
        for param, value in _alt_kwargs.items():
            assert getattr(SecondTestClass, param) == value
        SECOND_TRFM_X, SECOND_TRFM_Y = \
            SecondTestClass.fit_transform(X_np, y_np)
        for param, value in _alt_kwargs.items():
            assert getattr(SecondTestClass, param) == value

        # should not be equal to first transform
        assert not np.array_equal(FIRST_TRFM_X, SECOND_TRFM_X)
        assert not np.array_equal(FIRST_TRFM_Y, SECOND_TRFM_Y)

        # all params are being changed back to the original
        SecondTestClass.set_params(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(SecondTestClass, param) == value
        THIRD_TRFM_X, THIRD_TRFM_Y = \
            SecondTestClass.fit_transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(SecondTestClass, param) == value

        assert np.array_equiv(FIRST_TRFM_X, THIRD_TRFM_X)
        assert np.array_equiv(FIRST_TRFM_Y, THIRD_TRFM_Y)


    def test_set_params_output_repeatability(
        self, X_np, y_np, _kwargs, _alt_kwargs
    ):

        # changing and changing back on the same class gives same result
        # initialize, fit, transform, keep results
        # set all new params and transform
        # set back to the old params and transform, compare with the first output

        # initialize, fit, transform, and keep result
        TestClass = MCT(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(TestClass, param) == value
        TestClass.fit(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(TestClass, param) == value
        FIRST_TRFM_X, FIRST_TRFM_Y = TestClass.transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(TestClass, param) == value
        # use set_params to change all params.  DO NOT FIT!
        TestClass.set_params(**_alt_kwargs)
        for param, value in _alt_kwargs.items():
            assert getattr(TestClass, param) == value
        SECOND_TRFM_X, SECOND_TRFM_Y = TestClass.transform(X_np, y_np)
        for param, value in _alt_kwargs.items():
            assert getattr(TestClass, param) == value

        # should not be equal to first transform
        assert not np.array_equal(FIRST_TRFM_X, SECOND_TRFM_X)
        assert not np.array_equal(FIRST_TRFM_Y, SECOND_TRFM_Y)

        # use set_params again to change all params back to original values
        TestClass.set_params(**_kwargs)
        for param, value in _kwargs.items():
            assert getattr(TestClass, param) == value
        # transform again, and compare with the first output
        THIRD_TRFM_X, THIRD_TRFM_Y = TestClass.transform(X_np, y_np)
        for param, value in _kwargs.items():
            assert getattr(TestClass, param) == value

        assert np.array_equal(FIRST_TRFM_X, THIRD_TRFM_X)
        assert np.array_equal(FIRST_TRFM_Y, THIRD_TRFM_Y)





