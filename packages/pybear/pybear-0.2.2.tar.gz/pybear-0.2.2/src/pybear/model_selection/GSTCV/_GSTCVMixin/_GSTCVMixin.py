# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
import numpy.typing as npt
from .._type_aliases import (
    ClassifierProtocol,
    ParamGridsWIPType,
    ThresholdsWIPType,
    ScorerWIPType,
    RefitType,
    GenericKFoldType,
    MaskedHolderType,
    NDArrayHolderType,
    FeatureNamesInType
)

from copy import deepcopy
import numbers
import time

import numpy as np

from ._validation._validation import _validation
from ._validation._holders._f_t_s import _val_f_t_s
from ._validation._holders._f_s import _val_f_s

from ._param_conditioning._param_grid import _cond_param_grid
from ._param_conditioning._scoring import _cond_scoring
from ._param_conditioning._refit import _cond_refit
from ._param_conditioning._cv import _cond_cv
from ._param_conditioning._verbose import _cond_verbose

from ._fit._cv_results._cv_results_builder import _cv_results_builder
from ._fit._verify_refit_callable import _verify_refit_callable
from ._fit._get_best_thresholds import _get_best_thresholds
from ._fit._cv_results._cv_results_update import _cv_results_update
from ._fit._cv_results._cv_results_rank_update import _cv_results_rank_update

from ....base import (
    check_is_fitted,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
)



class _GSTCVMixin(
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Mixin for `GSTCV` and `GSTCVDask`."""


    # PROPERTIES v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    @property
    def classes_(self) ->  npt.NDArray[np.int64]:
        """Class labels.

        Only exposed when `refit` is not False. Because `GSTCV` imposes
        a restriction that y must be binary in [0, 1], this must always
        return [0, 1].

        Returns
        -------
        classes_ : numpy.ndarray[np.int64]
            The class labels for the target.

        """

        return self._best_estimator_getattr('classes_')


    @property
    def feature_names_in_(self) -> FeatureNamesInType:
        """Feature names seen during fit.

        Only available when `refit` is not False and `GSTCV` was fit on
        data that exposes feature names.

        Returns
        -------
        feature_names_in_ : FeatureNamesInType
            The feature names seen at first fit if the data was passed
            in a container that has a header with valid feature names.

        """

        return self._best_estimator_getattr('feature_names_in_')


    @property
    def n_features_in_(self) -> int:
        """Number of features seen during `fit`.

        Only available when `refit` is not False.

        Returns
        -------
        n_features_in_ : int
            The number of features seen in the data at first fit.

        """

        return self._best_estimator_getattr('n_features_in_')


    def _best_estimator_getattr(self, _attr: str) -> Any:
        """Get an attribute from `best_estimator_`.

        Check if `GSTCV` is fitted.

        Check if `refit` is not False.

        Check  if the best estimator has the attribute.

        If all checks pass, return the attribute.

        Parameters
        ----------
        _attr : str
            The attribute to look for in the best estimator.

        Returns
        -------
        attr_value : Any
            The attribute from the best estimator.

        """

        check_is_fitted(self)
        if not self.refit:   # must be the init refit, not _refit.
            raise AttributeError(
                f"This {type(self).__name__} instance was initialized "
                f"with `refit=False`. \n{_attr} is available only after "
                f"refitting on the best parameters."
            )
        if not hasattr(self.best_estimator_, _attr):
            raise AttributeError(
                f"This '{type(self).__name__}' has no attribute '{_attr}'"
            )

        return getattr(self.best_estimator_, _attr)

    # END PROPERTIES v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

    # SUPPORT METHODS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    def __pybear_is_fitted__(self) -> bool:
        return hasattr(self, '_refit')


    def _method_caller(
        self,
        method_name: str,
        method_to_call: str,
        X
    ) -> Any:
        """Check whether the estimator has the method, check that `refit`
        is not False, and check that `GSTCV` is fitted.

        Then call the method on `best_estimator_`, pass X to it, and
        return the output.

        Parameters
        ----------
        method_name : str
            The `GSTCV` method being called.
        method_to_call : str
            The actual method to call on the best estimator.
        X : array_like of shape (n_samples, n_features)
            The data passed to the method.

        Returns
        -------
        out : Any
            The best estimator method result for X.

        """

        if not hasattr(self.estimator, method_name):
            __ = type(self).__name__
            raise AttributeError(f"This '{__}' has no attribute '{method_name}'")
        if not self.refit:   # must be the init refit, not _refit.
            raise AttributeError(
                f"This {type(self).__name__} instance was initialized "
                f"with `refit=False`. \n{method_name} is available only "
                f"after refitting on the best parameters."
            )
        check_is_fitted(self)

        with self._scheduler:  # could be Sk or Dask SchedulerType
            return getattr(self.best_estimator_, method_to_call)(X)

    # END SUPPORT METHODS v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    ####################################################################
    # GSTCV Methods ####################################################

    def get_metadata_routing(self):
        """get_metadata_routing is not implemented in `GSTCV`."""

        # sklearn only --- always available, before and after fit()

        raise NotImplementedError(
            f"get_metadata_routing is not implemented in {type(self).__name__}."
        )


    def fit(self, X, y, **fit_params
    ) -> Self:
        """Perform the grid search with the hyperparameter settings in
        `param_grid` to find the unique hyperparameter values that
        maximize score (minimize loss) for the estimator and data being
        used.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            The data on which to perform the grid search. Must fulfill
            the input assumptions of the underlying estimator.
        y : vector-like, shape (n_samples,) or (n_samples, 1)
            The target relative to X. Must be binary in [0, 1]. Must
            fulfill the input assumptions of the underlying estimator.
        **fit_params : dict[str, Any]
            Parameters passed to the fit method of the estimator. If a
            fit parameter is an array-like whose length is equal to
            n_samples, then it will be split across CV groups along with
            X and y. For example, the sample_weight parameter is split
            because len(sample_weights) = len(X). For array-likes
            intended to be subject to CV splits, care must be taken to
            ensure that any such vector is shaped (n_samples, ) or
            (n_samples, 1), otherwise it will not be split.

            For pipelines, fit parameters can be passed to the fit method
            of any of the steps. Prefix the parameter name with the name
            of the step, such that parameter p for step s has key s__p.

        Returns
        -------
        self : object
            The fitted `GSTCV` instance.

        """


        # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # for params that serve both GSTCV & GSTCVDask
        _validation(
            self.estimator,
            self.param_grid,
            self.thresholds,
            self.scoring,
            self.n_jobs,
            self.refit,
            self.cv,
            self.verbose,
            self.error_score,
            self.return_train_score
        )

        # for either GSTCV or GSTCVDask params
        self._val_params()

        self._val_y(y)

        # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # conditioning ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        self._estimator: ClassifierProtocol = type(self.estimator)(
            **deepcopy(self.estimator.get_params(deep=False))
        )
        self._estimator.set_params(
            **deepcopy(self.estimator.get_params(deep=True))
        )

        _param_grid: ParamGridsWIPType = \
            _cond_param_grid(self.param_grid, self.thresholds)

        # by sklearn design, name convention changes from 'scoring' to
        # 'scorer_' after conversion to dictionary
        self.scorer_: ScorerWIPType = _cond_scoring(self.scoring)

        self._refit: RefitType = _cond_refit(self.refit, self.scorer_)

        # an iterable _cv is turned to list(tuple, tuple,...)
        # int stays int
        self._cv: int | list[GenericKFoldType] = _cond_cv(self.cv, _cv_default=5)

        self._verbose: int = _cond_verbose(self.verbose)

        self.multimetric_: bool = len(self.scorer_) > 1

        # n_splits_ is only available after fit. n_splits_ is always
        # returned as a number
        self.n_splits_: int = \
            self._cv if isinstance(self._cv, numbers.Real) else len(self._cv)

        # for either GSTCV or GSTCVDask params
        self._condition_params(X, y)

        # END conditioning ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # declare types after conditioning
        # THIS IS JUST TO HAVE A REFERENCE TO LOOK AT
        # self.estimator: ClassifierProtocol
        # self._estimator: ClassifierProtocol
        # self.param_grid: ParamGridInputType | ParamGridsInputType
        # _param_grid: ParamGridsWIPType
        # self.thresholds: ThresholdsInputType
        # self._THRESHOLD_DICT: dict[int, ThresholdsWIPType]
        # self.scoring: ScorerInputType
        # self.scorer_: ScorerWIPType
        # self.multimetric_: bool
        # self.n_jobs: int | None
        # self.refit: RefitType
        # self._refit: RefitType
        # self.cv: None | int | Iterable[GenericKFoldType]
        # self._cv: int | list[GenericKFoldType]
        # self.n_splits_: int
        # self.verbose: numbers.Real
        # self._verbose: int
        # self.error_score: Literal['raise'] | numbers.Real
        # self.return_train_score: bool

        # IF GSTCV:
        # self.pre_dispatch: Literal['all'] | str | int
        # self._scheduler: SKSchedulerType (ContextManager)

        # IF GSTCVDask:
        # self.cache_cv: bool
        # self.iid: bool
        # self.scheduler = DaskSchedulerType | None
        # self._scheduler = DaskSchedulerType (Client, Scheduler, ContextManager)
        # END declare types after conditioning
        # # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # BEFORE RUNNING cv_results_builder, THE THRESHOLDS MUST BE
        # REMOVED FROM EACH PARAM GRID IN _param_grid BUT THEY NEED TO
        # BE RETAINED FOR CORE GRID SEARCH.
        # pop IS INTENTIONALLY USED HERE TO REMOVE 'thresholds' FROM
        # PARAM GRIDS.
        # 'thresholds' MUST BE REMOVED FROM PARAM GRIDS BEFORE GOING
        # TO _cv_results_builder OR THRESHOLDS WILL BECOME PART OF THE
        # GRID SEARCH, AND ALSO CANT BE PASSED TO estimator.
        _THRESHOLD_DICT: dict[int, ThresholdsWIPType] = {}
        for i in range(len(_param_grid)):
            _THRESHOLD_DICT[i] = _param_grid[i].pop('thresholds')


        # this needs to be before validate the refit callable
        self.cv_results_, _PARAM_GRID_KEY = \
            _cv_results_builder(
                _param_grid,
                self.n_splits_,
                self.scorer_,
                self.return_train_score
        )

        # USE A DUMMIED-UP cv_results TO TEST IF THE refit CALLABLE RETURNS
        # A GOOD INDEX NUMBER, BEFORE RUNNING THE WHOLE GRIDSEARCH
        if callable(self._refit):
            _verify_refit_callable(self._refit, deepcopy(self.cv_results_))


        _original_params = self._estimator.get_params(deep=True)

        with self._scheduler:     # could be Sk or Dask SchedulerType

            # CORE FIT v v v v v v v v v v v v v v v v v v v v v v v v v

            for _trial_idx, _grid in enumerate(self.cv_results_['params']):

                if self._verbose >= 3:
                    print(f'\nparam grid {_trial_idx + 1} of '
                          f'{len(self.cv_results_["params"])}: {_grid}')

                _THRESHOLDS: list[float] = \
                    _THRESHOLD_DICT[int(_PARAM_GRID_KEY[_trial_idx])]

                # reset the estimator to the first-seen params at every
                # transition to a new param grid, and then set the new
                # params as called out in cv_results_. in that way, the
                # user can assume that params not explicitly declared in
                # a param grid are running at their defaults (or whatever
                # values they were hard-coded in when the estimator was
                # instantiated.)
                if _trial_idx != 0:
                    # at transition to the next param grid...
                    if _PARAM_GRID_KEY[_trial_idx] != _PARAM_GRID_KEY[_trial_idx - 1]:
                        # ...put in the first-seen params...
                        self._estimator.set_params(**_original_params)

                # ...then set the new params for the first search on the new grid
                self._estimator.set_params(**_grid)

                ###############################################################
                # CORE GRID SEARCH ############################################

                _FIT_OUTPUT: list[tuple[ClassifierProtocol, float, bool], ...]
                _FIT_OUTPUT = self._fit_all_folds(X, y, _grid, fit_params)

                # terminate if all folds excepted, display & compile fit times ** * **
                _FOLD_FIT_TIMES_VECTOR: MaskedHolderType = \
                    np.ma.empty(self.n_splits_, dtype=np.float64)
                _FOLD_FIT_TIMES_VECTOR.mask = True
                _num_failed_fits = 0

                # _FIT_OUTPUT IS (_estimator, _fit_time, fit_excepted)
                for _idx, (_, _fit_time, _fit_excepted) in enumerate(_FIT_OUTPUT):
                    _num_failed_fits += _fit_excepted

                    if _fit_excepted:
                        _FOLD_FIT_TIMES_VECTOR[_idx] = np.ma.masked
                    else:
                        _FOLD_FIT_TIMES_VECTOR[_idx] = _fit_time

                    if self._verbose >= 5:
                        print(f'fold {_idx + 1} train fit time = {_fit_time: ,.3g} s')

                if _num_failed_fits == self.n_splits_:
                    raise ValueError(f"all {self.n_splits_} folds failed during fit.")

                del _idx, _, _fit_time, _fit_excepted, _num_failed_fits
                # END terminate if all folds excepted, display & compile fit times ** *

                # SCORE ALL FOLDS & THRESHOLDS ################################

                if self._verbose >= 5:
                    print(f'\nStart scoring test with different thresholds and scorers')

                _test_predict_and_score_t0 = time.perf_counter()

                # _TEST_SCORER_OUT IS:
                # TEST_THRESHOLD_x_SCORER__SCORE_LAYER,
                # TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER

                # SCORE ALL FOLDS & THRESHOLDS ################################

                _TEST_SCORER_OUT: list[
                    tuple[MaskedHolderType, MaskedHolderType], ...
                ]
                _TEST_SCORER_OUT = self._score_all_folds_and_thresholds(
                    X, y, _FIT_OUTPUT, _THRESHOLDS
                )

                _tpast = time.perf_counter() - _test_predict_and_score_t0
                del _test_predict_and_score_t0

                if self._verbose >= 5:
                    print(f'End scoring test with different thresholds and scorers')
                    print(f'total test predict & score wall time = {_tpast: ,.3g} s')

                del _tpast
                # END SCORE ALL FOLDS & THRESHOLDS #################################

                # 3D-ify scores and times from parallel scorer ** * ** * ** *
                _TEST_FOLD_x_THRESH_x_SCORER__SCORE: MaskedHolderType = \
                    np.ma.masked_array(np.dstack(
                        list(zip(*_TEST_SCORER_OUT))[0]
                    )).transpose((2, 0, 1))
                _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME: MaskedHolderType = \
                    np.ma.masked_array(np.dstack(
                        list(zip(*_TEST_SCORER_OUT))[1]
                    )).transpose((2, 0, 1))
                del _TEST_SCORER_OUT
                # END 3D-ify scores and times from parallel scorer ** * ** * ** *

                # END CORE GRID SEARCH ############################################
                ###################################################################

                # NEED TO GET BEST THRESHOLDS BEFORE IDENTIFYING BEST SCORES ######

                # THIS CANNOT BE MELDED INTO ANYTHING ABOVE BECAUSE ALL FOLDS MUST
                # BE COMPLETED TO DO THIS
                _TEST_BEST_THRESH_IDXS_BY_SCORER: MaskedHolderType = \
                    _get_best_thresholds(
                        _TEST_FOLD_x_THRESH_x_SCORER__SCORE,
                        _THRESHOLDS
                    )
                # END NEED TO GET BEST THRESHOLDS BEFORE IDENTIFYING BEST SCORES ##

                # PICK THE COLUMNS FROM _TEST_FOLD_x_THRESH_x_SCORER__SCORE
                # THAT MATCH RESPECTIVE _TEST_BEST_THRESH_IDXS_BY_SCORER
                # THIS NEEDS TO BE ma TO PRESERVE ANY MASKING DONE TO
                # _TEST_FOLD_x_THRESH_x_SCORER__SCORE

                _val_f_t_s(
                    _TEST_FOLD_x_THRESH_x_SCORER__SCORE,
                    '_TEST_FOLD_x_THRESH_x_SCORER__SCORE',
                    self.n_splits_, len(_THRESHOLDS), len(self.scorer_)
                )

                _TEST_FOLD_x_SCORER__SCORE: MaskedHolderType = \
                    np.ma.empty((self.n_splits_, len(self.scorer_)))
                _TEST_FOLD_x_SCORER__SCORE.mask = True

                for s_idx, t_idx in enumerate(_TEST_BEST_THRESH_IDXS_BY_SCORER):
                    _TEST_FOLD_x_SCORER__SCORE[:, s_idx] = \
                        _TEST_FOLD_x_THRESH_x_SCORER__SCORE[:, t_idx, s_idx]

                del _TEST_FOLD_x_THRESH_x_SCORER__SCORE

                # SCORE TRAIN FOR THE BEST THRESHOLDS ##########################

                # 24_02_21_13_57_00 ORIGINAL CONFIGURATION WAS TO DO BOTH TEST
                # SCORING AND TRAIN SCORING UNDER THE SAME FOLD LOOP FROM A
                # SINGLE FIT. BECAUSE FINAL THRESHOLD(S) CANT BE KNOWN YET,
                # IT IS IMPOSSIBLE TO SELECTIVELY GET BEST SCORES JUST FOR TRAIN
                # @ THRESHOLD, SO ALL OF TRAIN'S SCORES MUST BE GENERATED. AFTER
                # FILLING TEST AND FINDING THE BEST THRESHOLDS, THEN TRAIN SCORES
                # CAN BE PICKED OUT. CALCULATING TRAIN SCORE TAKES A LONG TIME
                # FOR MANY THRESHOLDS.
                # PERFORMANCE TESTS 24_02_21 INDICATE IT IS BETTER TO FIT AND
                # SCORE TEST ALONE, GET THE BEST THRESHOLD(S), THEN DO ANOTHER
                # LOOP FOR TRAIN WITH RETAINED COEFS FROM THE EARLIER FITS
                # TO ONLY GENERATE SCORES FOR THE SINGLE THRESHOLD(S).

                _TRAIN_FOLD_x_SCORER__SCORE: MaskedHolderType = \
                    np.ma.zeros((self.n_splits_, len(self.scorer_)), dtype=np.float64)
                _TRAIN_FOLD_x_SCORER__SCORE.mask = True

                if self.return_train_score:

                    _BEST_THRESHOLDS_BY_SCORER: NDArrayHolderType = \
                        np.array(_THRESHOLDS)[_TEST_BEST_THRESH_IDXS_BY_SCORER]

                    # SCORE ALL FOLDS ###########################################

                    if self._verbose >= 5:
                        print(f'\nStart scoring train with different scorers')

                    _train_predict_and_score_t0 = time.perf_counter()

                    # _TRAIN_SCORER_OUT is TRAIN_SCORER__SCORE_LAYER
                    _TRAIN_SCORER_OUT: list[MaskedHolderType] = \
                        self._score_train(
                            X, y, _FIT_OUTPUT, _BEST_THRESHOLDS_BY_SCORER
                        )

                    _tpast = time.perf_counter() - _train_predict_and_score_t0
                    del _train_predict_and_score_t0

                    if self._verbose >= 5:
                        print(f'End scoring train with different scorers')
                        print(f'total train predict & score wall time = {_tpast: ,.3g} s')

                    del _tpast

                    # END SCORE ALL FOLDS #########################################

                    del _BEST_THRESHOLDS_BY_SCORER

                    _TRAIN_FOLD_x_SCORER__SCORE: MaskedHolderType = (
                        np.ma.masked_array(np.vstack(_TRAIN_SCORER_OUT))
                    )

                    del _TRAIN_SCORER_OUT

                # END SCORE TRAIN FOR THE BEST THRESHOLDS #########################

                # UPDATE cv_results_ WITH RESULTS #################################
                if self._verbose >= 5:
                    print(f'\nStart filling cv_results_')
                    cv_t0 = time.perf_counter()

                # validate shape of holder objects before cv_results update ** * **
                assert _FOLD_FIT_TIMES_VECTOR.shape == (self.n_splits_,), \
                    "_FOLD_FIT_TIMES_VECTOR is misshapen"
                _val_f_s(
                    _TEST_FOLD_x_SCORER__SCORE,
                    '_TEST_FOLD_x_SCORER__SCORE',
                    self.n_splits_, len(self.scorer_)
                )
                _val_f_t_s(
                    _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME,
                    '_TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME',
                    self.n_splits_, len(_THRESHOLDS), len(self.scorer_)
                )
                _val_f_s(
                    _TRAIN_FOLD_x_SCORER__SCORE,
                    '_TRAIN_FOLD_x_SCORER__SCORE',
                    self.n_splits_, len(self.scorer_)
                )
                # END validate shape of holder objects before cv_results update **

                self.cv_results_ = _cv_results_update(
                    _trial_idx,
                    _THRESHOLDS,
                    _FOLD_FIT_TIMES_VECTOR,
                    _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME,
                    _TEST_BEST_THRESH_IDXS_BY_SCORER,
                    _TEST_FOLD_x_SCORER__SCORE,
                    _TRAIN_FOLD_x_SCORER__SCORE,
                    self.scorer_,
                    self.cv_results_,
                    self.return_train_score
                )

                if self._verbose >= 5:
                    cv_tf = time.perf_counter()
                    print(f'End filling cv_results_ = {cv_tf - cv_t0: ,.3g} s')
                    del cv_t0, cv_tf

                del _TEST_FOLD_x_SCORER__SCORE
                del _TRAIN_FOLD_x_SCORER__SCORE
                del _FOLD_FIT_TIMES_VECTOR
                del _TEST_FOLD_x_THRESH_x_SCORER__SCORE_TIME


            del _original_params


            # ONLY DO TEST COLUMNS, DONT DO TRAIN RANK
            self.cv_results_ = _cv_results_rank_update(
                self.scorer_, self.cv_results_
            )

            # END CORE FIT ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

            # EXPOSE PARAMS v v v v v v v v v v v v v v v v v v v v v v v v
            def _get_best(_column: str) -> Any:
                return self.cv_results_[_column][self.best_index_]

            def _get_best_index(_column: str) -> int:
                _index = np.arange(self.cv_results_['params'].shape[0])
                return int(_index[self.cv_results_[_column] == 1][0])

            # 'refit' can be a str, bool False, or callable

            if callable(self._refit):

                self.best_index_ = self._refit(deepcopy(self.cv_results_))

                try:
                    assert int(self.best_index_) == self.best_index_
                    assert self.best_index_ <= self.cv_results_['params'].shape[0]
                    self.best_index_ = int(self.best_index_)
                except Exception as e:
                    raise ValueError(
                        f"if a callable is passed to refit, it must yield or "
                        f"return an integer, and it must be within range of "
                        f"cv_results_ rows."
                    )

                self.best_params_ = _get_best('params')

                if len(self.scorer_) == 1:
                    self.best_threshold_ = float(_get_best('best_threshold'))
                    self.best_score_ = float(_get_best('mean_test_score'))
                elif len(self.scorer_) > 1:
                    # A WARNING IS RAISED DURING VALIDATION
                    # self.best_score_ NOT AVAILABLE
                    # self.best_threshold_ NOT AVAILABLE
                    pass

            elif self._refit is False:

                if len(self.scorer_) == 1:
                    self.best_index_ = int(_get_best_index('rank_test_score'))
                    self.best_params_ = _get_best('params')
                    self.best_threshold_ = float(_get_best('best_threshold'))
                    self.best_score_ = float(_get_best('mean_test_score'))
                    # 24_07_16 through various experiments verified best_score_
                    # really is mean_test_score for best_index
                elif len(self.scorer_) > 1:
                    # A WARNING IS RAISED DURING VALIDATION
                    # None of the 4 are exposed
                    pass

            elif isinstance(self._refit, str):
                # DOESNT MATTER WHAT len(self.scorer_) IS
                self.best_index_ = int(_get_best_index(f'rank_test_{self._refit}'))
                self.best_params_ = _get_best('params')
                self.best_score_ = float(_get_best(f'mean_test_{self._refit}'))
                _lookup = f'best_threshold'
                if len(self.scorer_) > 1:
                    _lookup += f'_{self._refit}'
                self.best_threshold_ = float(_get_best(_lookup))
                del _lookup

            else:
                raise Exception(f"invalid 'refit' value '{self._refit}'")

            del _get_best, _get_best_index
            # END EXPOSE PARAMS ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

            # DO THE REFIT v v v v v v v v v v v v v v v v v v v v v v v v v
            if self._refit is not False:

                if self._verbose >= 3:
                    print(f'\nStarting refit...')

                self.best_estimator_ = \
                    type(self._estimator)(**self._estimator.get_params(deep=False))
                self.best_estimator_.set_params(**self._estimator.get_params(deep=True))
                self.best_estimator_.set_params(**self.best_params_)

                t0 = time.perf_counter()

                self.best_estimator_.fit(X, y, **fit_params)

                self.refit_time_ = time.perf_counter() - t0
                del t0
                if self._verbose >= 3:
                    print(f'Finished refit. time = {self.refit_time_}')


        return self


    def decision_function(self, X) -> Any:
        """Call `decision_function` on the estimator with the best
        parameters.

        Only available if `refit` is not False and the underlying
        estimator supports `decision_function`.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            The `best_estimator_` `decision_function` method result for
            X.

        """

        return self._method_caller('decision_function', 'decision_function', X)


    def inverse_transform(self, X) -> Any:
        """Call `inverse_transform` on the estimator with the best
        parameters.

        Only available if `refit` is not False and the underlying
        estimator supports `inverse_transform`.

        Parameters
        ----------
        X : array_like
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            The `best_estimator_` `inverse_transform` method result for
            X.

        """

        return self._method_caller('inverse_transform', 'inverse_transform', X)


    def predict(self, X) -> Any:
        """Pass X to `predict_proba` on the estimator with the best
        parameters and apply the best threshold to predict the classes
        for X.

        When only one scorer is used, predict is available if `refit` is
        not False. When more than one scorer is used, predict is only
        available if `refit` is set to a string.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            A vector in [0,1] indicating the class label for the
            examples in X.

        """

        # this getattr is important. if 'scorer_' not available, then not
        # fitted so throw down to _method_caller to get the correct error
        if len(getattr(self, 'scorer_', [])) > 1 and callable(self._refit):
            raise AttributeError(
                f"'predict' is not available when there are multiple "
                f"scorers and refit is a callable because best_threshold_ "
                f"cannot be determined."
            )

        y_pred = self._method_caller('predict', 'predict_proba', X)

        return (y_pred[:, -1] >= self.best_threshold_).astype(np.uint8)


    def predict_log_proba(self, X) -> Any:
        """Call `predict_log_proba` on the estimator with the best
        parameters.

        Only available if `refit` is not False and the underlying
        estimator supports `predict_log_proba`.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            The `best_estimator_` `predict_log_proba` method result for
            X.

        """

        return self._method_caller('predict_log_proba', 'predict_log_proba', X)


    def predict_proba(self, X) -> Any:
        """Call `predict_proba` on the estimator with the best
        parameters.

        Only available if `refit` is not False. The underlying estimator
        must support this method, as it is a characteristic that is
        validated.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            The `best_estimator_` `predict_proba_` method result for X.

        """

        return self._method_caller('predict_proba', 'predict_proba', X)


    def score(self, X, y) -> numbers.Real:
        """Score the given X and y using the best estimator, best
        threshold, and the defined scorer.

        When there is only one scorer, that is the defined scorer, and
        if `refit` is not False, then the score method is available.
        When there are multiple scorers, the defined scorer is the
        scorer specified by `refit` only if `refit` is set to a string
        value.

        See the documentation for the `scoring` parameter for information
        about passing kwargs to the scorer.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.
        y : vector-like, shape (n_samples, ) or (n_samples, 1)
            The target relative to X. Must be binary in [0, 1].

        Returns
        -------
        score : float
            The score for X and y on the best estimator and best
            threshold using the defined scorer.

        """

        if not hasattr(self, 'scorer_'):
            # not fitted, throw to _method_caller to get the correct error.
            pass
        elif len(self.scorer_) > 1 and callable(self._refit):
            # a relic of nonsense in sk GSCV?
            return self._refit

        self._val_y(y)
        y_pred = self._method_caller('score', 'predict', X)
        if len(self.scorer_) == 1 and callable(self._refit):
            return self.scorer_['score'](y, y_pred)
        else:
            return self.scorer_[self._refit](y, y_pred)


    def score_samples(self, X) -> Any:
        """Call `score_samples` on the estimator with the best
        parameters.

        Only available if `refit` is not False and the underlying
        estimator supports `score_samples`.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        out : Any
            The `best_estimator_` `score_samples` method result for X.

        """

        return self._method_caller('score_samples', 'score_samples', X)


    def transform(self, X) -> Any:
        """Call transform on the estimator with the best parameters.

        Only available if `refit` is not False and the underlying
        estimator supports transform.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            Must fulfill the input assumptions of the underlying
            estimator.

        Returns
        -------
        X_tr : Any
            The `best_estimator_` `transform` method result for X.

        """

        return self._method_caller('transform', 'transform', X)


    def visualize(self, *args, **kwargs) -> Any:
        """Call `visualize` on the estimator with the best parameters.

        Only available if `refit` is not False and the underlying
        estimator supports visualize.

        Parameters
        ----------
        *args : list[Any]
            Positional arguments for the best estimator's visualize
            method.
        **kwargs : dict[str: Any]
            Keyword arguments for the best estimator's visualize method.

        Returns
        -------
        out : Any
            The `best_estimator_` `visualize` output.

        """

        _attr = 'visualize'
        if not hasattr(self.estimator, _attr):
            raise AttributeError(
                f"This '{type(self).__name__}' has no attribute '{_attr}'"
            )
        if not self.refit:   # must be the init refit, not _refit
            raise AttributeError(
                f"This {type(self).__name__} instance was initialized "
                f"with `refit=False`. \n{_attr} is available only after "
                f"refitting on the best parameters."
            )
        check_is_fitted(self)

        return getattr(self.best_estimator_, _attr)(*args, **kwargs)




