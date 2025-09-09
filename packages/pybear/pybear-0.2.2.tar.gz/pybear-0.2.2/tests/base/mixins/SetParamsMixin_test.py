# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re
from copy import deepcopy

import numpy as np
import inspect



# things tested for single estimator, single transformer, est wrapped in a mock GSCV:
# calling get_params on not instantiated - single est, single trfm,
#       GSCV not instantiated, GSCV instantiated estimator not instantiated
# single est, single trfm:
# - init was correctly applied
# - rejects positional arguments
# - rejects invalid params
# - accepts allowed params
# nested:
# - junk estimator (does not have set_params method) is rejected
# - init was correctly applied
# - rejects positional arguments
# - rejects invalid params
# - accepts allowed params
# single est, single trfm, nested:
# - setting of leading, trailing underscores is not allowed


@pytest.fixture(scope='function')
def _est_kwargs():
    return {
        'bananas': True,
        'fries': 'yes',
        'ethanol': 1,
        'apples': [0, 1]
    }


@pytest.fixture(scope='function')
def _gscv_kwargs(DummyEstimator):
    return {
        'estimator': DummyEstimator(),
        'param_grid': {
            'fries': [7, 8, 9],
            'ethanol': [5, 6, 7],
            'apples': [3, 4, 5]
        },
        'refit': True,
        'scoring': 'balanced_accuracy'
    }


@pytest.fixture(scope='function')
def _trfm_kwargs():
    return {
        'tbone': False,
        'wings': 'yes',
        'bacon': 0,
        'sausage': [4, 4],
        'hambone': False
    }

# END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


class TestSetParams__NotInstantiated:

    # test a bad estimator:
    # - is class not instance  (wont be able to do post-fit, cant be fitted)
    # - estimator does not have set_params

    # single_est not instantiated
    # single_trfm not instantiated
    # GSCV_est is not instantiated
    # GSCV_est instantiated, estimator not instantiated


    @staticmethod
    @pytest.fixture()
    def err_msg():

        return (
            f":meth: 'set_params' is being called on the class, not an "
            f"instance. Instantiate the class, then call set_params."
        )


    def test_single_est(self, DummyEstimator, err_msg, _est_kwargs):

        # call on class not instance, self is not passed -- -- -- -- --
        # these error types/messages are controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyEstimator.set_params()

        with pytest.raises(Exception):
            DummyEstimator.set_params(**_est_kwargs)
        # END call on class not instance, self is not passed -- -- -- -- --

        # call on class not instance, bad positionals passed -- -- -- -- --
        a = 1
        b = 2
        # this error type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyEstimator.set_params(a)

        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyEstimator.set_params(a, b)
        # END call on class not instance, bad positionals passed -- -- -- -- --


    def test_single_trfm(self, DummyTransformer, err_msg, _trfm_kwargs):

        # call on class not instance, self is not passed -- -- -- -- --
        # these error types/messages are controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyTransformer.set_params()

        with pytest.raises(Exception):
            DummyTransformer.set_params(**_trfm_kwargs)
        # END call on class not instance, self is not passed -- -- -- --

        # call on class not instance, bad positionals passed -- -- -- -- --
        a = 1
        b = 2
        # this error type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyTransformer.set_params(a)

        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyTransformer.set_params(a, b)
        # END call on class not instance, bad positionals passed -- -- -- --


    def test_gscv_est_part1(
        self, DummyGridSearch, DummyEstimator, err_msg, _gscv_kwargs
    ):

        # GSCV_est is not instantiated

        # call on class not instance, self is not passed -- -- -- -- --
        # these error types/messages are controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyGridSearch.set_params()

        with pytest.raises(Exception):
            DummyGridSearch.set_params(**_gscv_kwargs)
        # END call on class not instance, self is not passed -- -- -- --

        # call on class not instance, bad positionals passed -- -- -- --
        a = 1
        b = 2
        # this error type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyGridSearch.set_params(a)

        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyGridSearch.set_params(a, b)
        # END call on class not instance, bad positionals passed -- -- -- --


    def test_gscv_est_part2(self, DummyGridSearch, DummyEstimator):
        # GSCV_est instantiated, estimator not instantiated

        gscv = DummyGridSearch(
            estimator=DummyEstimator,
            param_grid={
                'bananas': [0, 1],
                'fries': [0, 1],
                'ethanol': [0, 1],
                'apples': [0, 1]
            }
        )

        # these are actually raising WHEN TRYING TO FILL 'ALLOWED_SUB_PARAMS':list
        # IN GetParamsMixin.get_params, because junk_estimator doesnt have
        # get_params. so this error message has a get_params reference instead
        # of a set_params reference. (remember that if SetParamsMixin in being
        # used, then the child must also have the GetParamsMixin)
        err_msg = (
            f"'estimator' must be an instance (not class) of a valid "
            f"estimator or transformer that has a get_params method."
        )

        _est_params = {
            'estimator__bananas': True,
            'estimator__fries': 'yes',
            'estimator__ethanol': 1,
            'estimator__apples': [0, 1]
        }

        # call on class not instance, self is not passed -- -- -- -- --
        # this type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            gscv.set_params(**_est_params)
        # END call on class not instance, self is not passed -- -- -- -- --


@pytest.mark.parametrize('top_level_object', ('single_est', 'single_trfm'))
@pytest.mark.parametrize('state', ('pre-fit', 'post-fit'))
class TestSetParams__NonEmbedded:

    # simple est/trfms should be straightforward to test. verify that
    # bad params bounce off. verify that good params are set correctly.


    @staticmethod
    @pytest.fixture(scope='function')
    def _kwargs(top_level_object, _est_kwargs, _trfm_kwargs):

        if top_level_object == 'single_est':
            return _est_kwargs
        elif top_level_object == 'single_trfm':
            return _trfm_kwargs
        else:
            raise Exception


    @staticmethod
    @pytest.fixture(scope='function')
    def TopLevelObject(
        top_level_object, state, DummyEstimator, DummyTransformer, _X_np, _kwargs
    ):

        if top_level_object == 'single_est':
            foo = DummyEstimator(**_kwargs)
        elif top_level_object == 'single_trfm':
            foo = DummyTransformer(**_kwargs)
        else:
            raise Exception

        if state == 'post-fit':
            foo.fit(_X_np)

        return foo

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def test_init_was_correctly_applied(self, TopLevelObject, _kwargs):

        # assert TestCls initiated correctly
        for _param, _value in _kwargs.items():
            assert getattr(TopLevelObject, _param) == _value


    def test_positional_arguments_rejected(self, TopLevelObject, _kwargs):

        a, b, c = 1, 2, 3

        with pytest.raises(TypeError):
            TopLevelObject.set_params(a, b, c)


    def test_rejects_unknown_param(self, TopLevelObject):

        with pytest.raises(ValueError):
            TopLevelObject.set_params(garbage=True)

        with pytest.raises(ValueError):
            TopLevelObject.set_params(estimator__trash=True)


    def test_set_params_correctly_applies(
        self, top_level_object, TopLevelObject, _kwargs
    ):

        _new_kwargs = deepcopy(_kwargs)

        if top_level_object == 'single_est':
            _new_kwargs['bananas'] = False
            _new_kwargs['fries'] = 'no'
            _new_kwargs['ethanol'] = 0
            _new_kwargs['apples'] = 'yikes'
        elif top_level_object == 'single_trfm':
            _new_kwargs['tbone'] = True
            _new_kwargs['wings'] = 'np'
            _new_kwargs['bacon'] = 1
            _new_kwargs['sausage'] = False
            _new_kwargs['hambone'] = [1, 1]
        else:
            raise Exception

        # TopLevelObject can be before fit or after fit
        TopLevelObject.set_params(**_new_kwargs)

        # assert new values set correctly
        for _param, _value in _new_kwargs.items():
            assert getattr(TopLevelObject, _param) == _value


@pytest.mark.parametrize('junk_estimator',
    (0, 1, True, None, 'junk', [0,1], min, lambda x: x)
)
class TestGetParams__Embedded__JunkEstimator:


    def test_gscv_junk_estimator(self, DummyGridSearch, junk_estimator, _gscv_kwargs):

        # GSCV_est instantiated, junk estimator

        gscv = DummyGridSearch(
            estimator=junk_estimator,
            param_grid={
                'bananas': [0, 1],
                'fries': [0, 1],
                'ethanol': [0, 1],
                'apples': [0, 1]
            }
        )

        # these are actually raising WHEN TRYING TO FILL 'ALLOWED_SUB_PARAMS':list
        # IN GetParamsMixin.get_params because junk_estimator doesnt have
        # get_params. so this error message has a get_params reference instead
        # of a set_params reference. (remember that if SetParamsMixin in being
        # used, then the child must also have the GetParamsMixin)
        err_msg = (
            f"'estimator' must be an instance (not class) of a valid "
            f"estimator or transformer that has a get_params method."
        )

        if inspect.isclass(junk_estimator):
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.set_params(**_gscv_kwargs)
        else:
            # then it must not have set_params(), because all of these are junk
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.set_params(**_gscv_kwargs)


@pytest.mark.parametrize('state', ('pre-fit', 'post-fit'))
class TestSetParams__Embedded:


    @staticmethod
    @pytest.fixture(scope='function')
    def TopLevelObject(DummyGridSearch, state, _X_np, _gscv_kwargs):

        foo = DummyGridSearch(**_gscv_kwargs)

        if state == 'post-fit':
            foo.fit(_X_np)

        return foo


    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def test_init_was_correctly_applied(self, TopLevelObject, _gscv_kwargs):

        # assert TestCls initiated correctly
        for _param, _value in _gscv_kwargs.items():
            assert getattr(TopLevelObject, _param) == _value


    def test_positional_arguments_rejected(self, TopLevelObject, _gscv_kwargs):

        a, b, c = 1, 2, 3

        with pytest.raises(TypeError):
            TopLevelObject.set_params(a, b, c)


    def test_rejects_unknown_param(self, TopLevelObject):

        with pytest.raises(ValueError):
            TopLevelObject.set_params(garbage=True)

        with pytest.raises(ValueError):
            TopLevelObject.set_params(estimator__trash=True)


    def test_set_params_correctly_applies(
        self, TopLevelObject, _gscv_kwargs):

        _new_gscv_kwargs = deepcopy(_gscv_kwargs)

        # set top-level params
        _new_gscv_kwargs['param_grid'] = {
                'fries': [1, 2, 3],
                'ethanol': [11, 12, 13],
                'apples': [71, 72, 73]
        }
        _new_gscv_kwargs['refit'] = False
        _new_gscv_kwargs['scoring'] = 'accuracy'

        # set estimator_params (must be prefixed with 'estimator__')
        # only testing DummyEstimator, not DummyTransformer inside GSCV
        _new_gscv_kwargs['estimator__bananas'] = 8
        _new_gscv_kwargs['estimator__fries'] = 1000
        _new_gscv_kwargs['estimator__ethanol'] = float('inf')
        _new_gscv_kwargs['estimator__apples'] = [0, 1]   # <==== no change

        TopLevelObject.set_params(**_new_gscv_kwargs)

        # assert new values set correctly
        for _param, _value in _new_gscv_kwargs.items():
            if 'estimator__' in _param:
                # if we were allowed to set params with an 'estimator__'
                # prefix, then that means that there was an 'estimator'
                # attribute, and this getattr must work
                _actual = getattr(
                    TopLevelObject.estimator,
                    _param.replace('estimator__', '')
                )
                assert _actual == _value
            else:
                _actual = getattr(TopLevelObject, _param)
                assert _actual == _value


@pytest.mark.parametrize('top_level_object',
    ('single_est', 'single_trfm', 'GSCV_est')
)
@pytest.mark.parametrize('state', ('prefit', 'postfit'))
class TestDisallowedSetUnderscoreParams:


    @staticmethod
    @pytest.fixture(scope='function')
    def TopLevelObject(
        top_level_object, state, DummyEstimator, DummyTransformer,
        DummyGridSearch, _X_np
    ):

        if top_level_object == 'single_est':
            foo = DummyEstimator()
        elif top_level_object == 'single_trfm':
            foo = DummyTransformer()
        elif top_level_object == 'GSCV_est':
            foo = DummyGridSearch(
                estimator=DummyEstimator(),
                param_grid={
                    'fries': [7, 8, 9],
                    'ethanol': [5, 6, 7],
                    'apples': [3, 4, 5]
                }
            )
        else:
            raise Exception

        if state == 'postfit':
            foo.fit(_X_np)

        return foo


    def test_setting_underscore_params_disallowed(self, TopLevelObject):

        with pytest.raises(ValueError) as exc:
            TopLevelObject.set_params(_is_fitted=True)

        _expedted_str = re.escape(f"Invalid parameter '_is_fitted' for ")
        _actual_str = re.escape(str(exc))

        assert _expedted_str in _actual_str






