# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np



"""

estimator is a pipeline with sk OneHotEncoder & sk LogisticRegression

deep = False
        skgscv_params        gstcv_params
0                  cv                  cv
1         error_score         error_score
2           estimator           estimator
3              n_jobs              n_jobs
4          param_grid          param_grid
5        pre_dispatch                   -
6               refit               refit
7  return_train_score  return_train_score          
8             scoring             scoring
9                   -          thresholds
10            verbose             verbose

deep = True
                               skgscv_params                              gstcv_params
0                                         cv                                        cv
1                                error_score                               error_score
2                          estimator__memory                         estimator__memory
3                           estimator__steps                          estimator__steps
4                         estimator__verbose                        estimator__verbose
5                          estimator__onehot                         estimator__onehot
6                        estimator__logistic                       estimator__logistic
7              estimator__onehot__categories             estimator__onehot__categories
8                    estimator__onehot__drop                   estimator__onehot__drop
9                   estimator__onehot__dtype                  estimator__onehot__dtype
10  estimator__onehot__feature_name_combiner  estimator__onehot__feature_name_combiner
11         estimator__onehot__handle_unknown         estimator__onehot__handle_unknown
12         estimator__onehot__max_categories         estimator__onehot__max_categories
13          estimator__onehot__min_frequency          estimator__onehot__min_frequency
14          estimator__onehot__sparse_output          estimator__onehot__sparse_output
15                    estimator__logistic__C                    estimator__logistic__C
16         estimator__logistic__class_weight         estimator__logistic__class_weight
17                 estimator__logistic__dual                 estimator__logistic__dual
18        estimator__logistic__fit_intercept        estimator__logistic__fit_intercept
19    estimator__logistic__intercept_scaling    estimator__logistic__intercept_scaling
20             estimator__logistic__l1_ratio             estimator__logistic__l1_ratio
21             estimator__logistic__max_iter             estimator__logistic__max_iter
22          estimator__logistic__multi_class          estimator__logistic__multi_class
23               estimator__logistic__n_jobs               estimator__logistic__n_jobs
24              estimator__logistic__penalty              estimator__logistic__penalty
25         estimator__logistic__random_state         estimator__logistic__random_state
26               estimator__logistic__solver               estimator__logistic__solver
27                  estimator__logistic__tol                  estimator__logistic__tol
28              estimator__logistic__verbose              estimator__logistic__verbose
29           estimator__logistic__warm_start           estimator__logistic__warm_start
30                                 estimator                                 estimator
31                                    n_jobs                                    n_jobs
32                                param_grid                                param_grid
33                              pre_dispatch                                         -
34                                     refit                                     refit
35                        return_train_score                        return_train_score
36                                   scoring                                   scoring
37                                         -                                thresholds
38                                   verbose                                   verbose


# the takeaways from sklearn get_params:
# params are always sorted asc alphabetical (vars does not do this itself)
# leading and trailing underscores are removed
# those 2 simple rules explain get_params on single estimators and 
# transformers. :param: 'deep' only matters if the top-level object (the 
# object whose get_params() method is being called) has an 'estimator' 
# attribute. 'deep'==False on a top-level object with an embedded 
# estimator returns only the params of the top-level object, subject to 
# the same 2 rules that are applied to single estimators and transformers. 
# when 'deep'==True, get_params is called on the embedded object also. 
# the shallow params for the top-level object are split right before 
# 'estimator', and the deep params for the embedded object are inserted 
# in between.

"""




# things tested for single estimator, single transformer, est wrapped in a mock GSCV:
# builtin vars() returns attrs in alphabetical order (doesnt!)
# calling get_params on not instantiated - single est, single trfm,
#       GSCV not instantiated, GSCV instantiated estimator not instantiated
# junk estimator in GSCV (does not have get_params method) is rejected
# rejects non-bool deep
# accepts bool deep
# the basic sklearn get_params strategy, that the get_params paramsdict:
# - has correct params
# - does not have params/attrs/keys with leading or trailing underscore
# - has params/attrs/keys sorted alphabetically, and that when deep=True,
#   on an embedded object, the embedded's params are prefixed with
#   'estimator__'.
#
# params should be the same before and after fit for all sklearn-style
# objects.


class TestVarsDoesNotReturnAlphabetical:

    # originally this test intended to prove that the 'vars' builtin
    # sorts attributes asc alphabetical.... but it turns out that it doesnt.
    # ostensibly they are in the order they are initialized.
    # so the sort must be done manually in GetParamsMixin.get_params()

    def test_vars_returns_alphabetized__est(self, DummyEstimator):

        clf = DummyEstimator()

        out = vars(clf)

        assert isinstance(out, dict)

        assert not np.array_equal(list(out.keys()), set(out.keys()))


    def test_vars_returns_alphabetized__trfm(self, DummyTransformer):

        trfm = DummyTransformer()

        out = vars(trfm)

        assert isinstance(out, dict)

        assert not np.array_equal(list(out.keys()), set(out.keys()))


@pytest.mark.parametrize('deep', (True, False))
class TestGetParams__NotInstantiated:

    # single_est not instantiated
    # single_trfm not instantiated
    # GSCV_est is not instantiated
    # GSCV_est instantiated, estimator not instantiated


    @staticmethod
    @pytest.fixture()
    def err_msg():

        return (
            f":meth: 'get_params' is being called on the class, not an "
            f"instance. Instantiate the class, then call get_params."
        )


    def test_single_est(self, DummyEstimator, err_msg, deep):

        # call on class not instance, thinks 'deep' is self -- -- -- --
        # this type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyEstimator.get_params(deep)
        # END call on class not instance, thinks 'deep' is self -- -- --

        # call on class not instance, self is not passed -- -- -- -- --
        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyEstimator.get_params()

        with pytest.raises(Exception):
            DummyEstimator.get_params(deep=deep)
        # END call on class not instance, self is not passed -- -- -- --


    def test_single_trfm(self, DummyTransformer, err_msg, deep):

        # call on class not instance, thinks 'deep' is self -- -- --
        # this type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyTransformer.get_params(deep)
        # END call on class not instance, thinks 'deep' is self -- -- --

        # call on class not instance, self is not passed -- -- -- -- --
        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyTransformer.get_params()

        with pytest.raises(Exception):
            DummyTransformer.get_params(deep=deep)
        # END call on class not instance, self is not passed -- -- -- --


    def test_gscv_est_part1(self, DummyGridSearch, DummyEstimator, err_msg, deep):
        # GSCV_est is not instantiated

        # call on class not instance, thinks 'deep' is self -- -- --
        # this type/message is controlled by pybear
        with pytest.raises(TypeError, match=re.escape(err_msg)):
            DummyGridSearch.get_params(deep)
        # END call on class not instance, thinks 'deep' is self -- -- --

        # call on class not instance, self is not passed -- -- -- -- --
        # this error type/message is controlled by python, let it raise whatever
        with pytest.raises(Exception):
            DummyGridSearch.get_params()

        with pytest.raises(Exception):
            DummyGridSearch.get_params(deep=deep)
        # END call on class not instance, self is not passed -- -- -- --


    def test_gscv_est_part2(self, DummyGridSearch, DummyEstimator, deep):
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

        # this deep=False should not fail, because the top-level (gscv) is
        # instantiated. deep=True should fail because estimator is a class

        err_msg = (
            f"'estimator' must be an instance (not class) of a valid "
            f"estimator or transformer that has a get_params method."
        )

        if deep is False:
            assert isinstance(gscv.get_params(deep), dict)
            assert isinstance(gscv.get_params(deep=deep), dict)
        else:
            # call on class not instance, thinks 'deep' is self -- -- --
            # this type/message is controlled by pybear
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.get_params(deep)
            # END call on class not instance, thinks 'deep' is self -- --

            # call on class not instance, self is not passed -- -- -- --
            # this error type/message is controlled by python, let it raise whatever
            with pytest.raises(Exception):
                gscv.get_params()

            with pytest.raises(Exception):
                gscv.get_params(deep=deep)
            # END call on class not instance, self is not passed -- -- --


@pytest.mark.parametrize('junk_estimator',
    (0, 1, True, None, 'junk', [0,1], min, lambda x: x)
)
@pytest.mark.parametrize('deep', (True, False))
class TestGetParams__Embedded__JunkEstimator:


    def test_gscv_junk_estimator(
        self, DummyGridSearch, junk_estimator, deep
    ):

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

        if deep is False:
            # if deep is False, it will only look in the top-level and not even
            # see that the estimator is junk
            assert isinstance(gscv.get_params(deep), dict)
        else:
            # but if deep is True, it should try to do get_params on the
            # estimator which will raise

            err_msg = (
                f"'estimator' must be an instance (not class) of a valid "
                f"estimator or transformer that has a get_params method."
            )

            # if inspect.isclass(junk_estimator):
            # thinks deep is self
            # all of these error types/messages are controlled by pybear
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.get_params(deep)
            # self is not passed
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.get_params()
            # self is not passed
            with pytest.raises(TypeError, match=re.escape(err_msg)):
                gscv.get_params(deep=deep)


@pytest.mark.parametrize('top_level_object',
    ('single_est', 'single_trfm', 'GSCV_est')
)
@pytest.mark.parametrize('state', ('prefit', 'postfit'))
class TestGetParams__Embedded__NonEmbedded:

    # fortunately it is easy to test simple est/trfm and nested gscv under
    # the same test for get_params. in set_params, the tests are split up.

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


    @pytest.mark.parametrize('bad_deep',
        (0, 1, 3.14, None, 'trash', min, [0,1], (0,1), {'a':1}, lambda x: x)
    )
    def test_rejects_non_bool_deep(self, TopLevelObject, bad_deep):

        with pytest.raises(ValueError):
            TopLevelObject.get_params(bad_deep)


    @pytest.mark.parametrize('bool_deep', (True, False))
    def test_accepts_bool_deep(self, TopLevelObject, bool_deep):

        out = TopLevelObject.get_params(bool_deep)

        assert isinstance(out, dict)


    @pytest.mark.parametrize('_deep', (True, False))
    def test_accuracy(self, top_level_object, TopLevelObject, _deep):

        out = TopLevelObject.get_params(deep=_deep)

        assert isinstance(out, dict)

        # proves out leading/trailing underscore removed, alphabetized

        if top_level_object == 'single_est':
            # doesnt matter what 'deep' is, shouldnt matter for est
            assert np.array_equal(
                list(out.keys()),
                ['apples', 'bananas', 'ethanol', 'fries']
            )

        elif top_level_object == 'single_trfm':
            # doesnt matter what 'deep' is, shouldnt matter for trfm
            assert np.array_equal(
                list(out.keys()),
                ['bacon', 'hambone', 'sausage', 'tbone', 'wings']
            )

        elif top_level_object == 'GSCV_est':
            if _deep is False:
                # should be just the gscv params
                assert np.array_equal(
                    list(out.keys()),
                    ['estimator', 'param_grid', 'refit', 'scoring']
                )

            elif _deep is True:
                # should be in this order:
                # all of the alphabetized outer object shallow params up
                # to but not including 'estimator'
                exp_params = []
                # all of the deep params for the estimator. for a pipe,
                # it would be the deep params for the pipe, but in this
                # case we are only testing a single estimator, so it is
                # all the params from the estimator, as returned by
                # get_params() (leading and trailing underscores removed,
                # alphabetized). but with a 'estimator__' prefix.
                exp_params += [
                    'estimator__apples',
                    'estimator__bananas',
                    'estimator__ethanol',
                    'estimator__fries'
                ]
                # then all of the alphabetized top level object shallow
                # params from 'estimator' (inclusive) to the end
                exp_params += ['estimator', 'param_grid', 'refit', 'scoring']

                assert np.array_equal(
                    list(out.keys()),
                    exp_params
                )

        else:
            raise Exception






