# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Callable,
    Iterable
)
from ._type_aliases import (
    PreDispatchType,
    SKXType,
    SKYType,
    SKKFoldType,
    SKSchedulerType
)
from .._type_aliases import (
    ClassifierProtocol,
    ErrorScoreType,
    ParamGridInputType,
    ParamGridsInputType,
    ScorerInputType,
    ThresholdsInputType,
    ThresholdsWIPType,
    MaskedHolderType,
    NDArrayHolderType
)

from contextlib import nullcontext
from copy import deepcopy
import numbers

import joblib
import numpy as np

from ._validation._validation import _validation
from ._validation._y import _val_y



from .._GSTCV._fit._get_kfold import _get_kfold as _sk_get_kfold
from .._GSTCV._fit._fold_splitter import _fold_splitter as _sk_fold_splitter
from .._GSTCV._fit._estimator_fit_params_helper import \
    _estimator_fit_params_helper as _sk_estimator_fit_params_helper
from .._GSTCV._fit._parallelized_fit import _parallelized_fit
from .._GSTCV._fit._parallelized_scorer import _parallelized_scorer
from .._GSTCV._fit._parallelized_train_scorer import _parallelized_train_scorer
from .._GSTCVMixin._GSTCVMixin import _GSTCVMixin



class GSTCV(_GSTCVMixin):
    """Exhaustive cross-validated search over a grid of hyperparameter
    values and decision thresholds for a binary classifier.

    The optimal hyperparameters and decision threshold selected are
    those that maximize the average score (and minimize the average
    loss) of the held-out data (test sets).

    pybear `GSTCV` (grid search threshold CV) is intended to closely
    parallel the interface and user-experience of scikit-learn
    `GridSearchCV`. Users who are familiar with that GridSearch
    implementation should find that `GSTCV` differs with respect to 4
    things:

    1) the init parameter `thresholds` (which can also be passed as a
    parameter to `param_grid`)

    2) additional columns in the :attr:`cv_results_` attribute to report
    the best thresholds for each scorer

    3) a new post-run attribute, :attr:`best_threshold_`, which informs
    about the overall best threshold

    4) callables passed to `scoring` SHOULD NOT be wrapped in
    'make_scorer' as would be done with `GridSearchCV`. Pass scoring
    callables in raw metric form. See the scikit-learn docs and the
    'Parameters' section of the `GSTCV` docs for more information about
    'make_scorer' and 'metrics'.

    Users who are familiar with the scikit implementation of GridSearch
    should focus on the above 4 areas in the `GSTCV` 'Parameters' and
    'Attributes' sections of the docs for mastery of `GSTCV`.

    `GSTCV` implements `fit`, `predict_proba`, `predict`, `score`,
    `get_params`, and `set_params` methods. It also implements
    `decision_function`, `predict_log_proba`, `score_samples`,
    `transform` and `inverse_transform` if they are exposed by the
    classifier passed to `estimator`.

    Parameters
    ----------
    estimator : object
        Required. Must be a binary classifier that conforms to the
        scikit-learn estimator API interface. The classifier must have
        the `fit`, `set_params`, `get_params`, and `predict_proba`
        methods. If the classifier does not have `predict_proba`, try
        to wrap with `CalibratedClassifierCV`. The classifier does not
        need a `score` method, as `GSTCV` never accesses the estimator
        `score` method because it always uses a 0.5 threshold.

        `GSTCV` deliberately blocks dask classifiers (including, but not
        limited to, dask_ml, xgboost, and lightGBM dask classifiers.) To
        use dask classifiers, use pybear-dask`GSTCVDask`.
    param_grid : ParamGridInputType | ParamGridsInputType
        Required. A dictionary with hyperparameters names (str) as keys
        and list-likes of respective settings to try as values. Can also
        be a list-like of such dictionaries, and the grids spanned by
        each are explored. This enables searching over any combination
        of hyperparameter settings.
    thresholds : ThresholdsInputType, default=None
        The decision threshold search grid to use when performing the
        hyperparameter search. Other `GridSearchCV` modules only use the
        conventional decision threshold for binary classifiers, which is
        0.5. This module can search over any set of decision threshold
        values in the 0 to 1 interval (inclusive) in the same manner as
        any other hyperparameter while performing the grid search.

        The thresholds value passed via the init parameter can be None,
        a single number from 0 to 1 (inclusive) or a list-like of such
        numbers. If None, (and thresholds are not passed directly inside
        the param grid(s)), the default threshold grid is used,
        `numpy.linspace(0, 1, 21)`.

        Thresholds may also be passed to individual param grids via a
        'thresholds' key. However, when passed directly to a param grid,
        'thresholds' cannot be None or a single number, it must be a
        list-like of numbers as is normally done with param grids.

        Because `thresholds` can be passed in 2 different ways, there
        is a hierarchy that dictates which thresholds are used during
        searching and scoring. Any threshold values passed directly
        within a param grid always supersede any passed (or not passed)
        to the `thresholds` init parameter. When a param grid does not
        have any thresholds passed inside it, the value passed to the
        init parameter is used -- if a value was not passed to the init
        parameter, then the `GSTCV` default value is used.

        When one scorer is used, the best threshold is always exposed
        and is accessible via the :attr:`best_threshold_` attribute.
        When multiple scorers are used, the `best_threshold_` attribute
        is only exposed when a string value is passed to `refit`. The
        best threshold is never reported in the :attr:`best_params_`
        attribute, even if thresholds were passed via a param grid; the
        best threshold is only available via the `best_threshold_`
        attribute. Another way to discover the best threshold for each
        scorer is by inspection of the :attr:`cv_results_` attribute.

        The scores reported for test data in `cv_results_` are those for
        the best threshold. Also note that when `return_train_score` is
        True, the scores returned for the train data are only for the
        best threshold found for the test data. That is, every threshold
        is scored on the test data, the best score is found, and the
        best threshold is the threshold corresponding to the best score.
        That best score and best threshold is reported for the test data.
        Then when scoring train data, only the best threshold is scored
        and reported in `cv_results_`.
    scoring : ScorerInputType, default='accuracy'
        Strategy to evaluate the performance of the cross-validated model
        on the test set (and also train set, if `return_train_score` is
        True.)

        For any number of scorers, scoring can be a dictionary with
        user-assigned scorer names as keys and callables as values. See
        below for clarification on allowed callables.

        For a single scoring metric, a single string or a single callable
        is also allowed. Valid strings that can be passed are 'accuracy',
        'balanced_accuracy', 'average_precision', 'f1', 'precision', and
        'recall'.

        For evaluating multiple metrics, scoring can be a vector-like of
        unique strings, containing a combination of the allowed strings.

        The default scorer of the estimator cannot be used by this module
        because the decision threshold cannot be manipulated. Therefore,
        `scoring` cannot accept a None argument.

        About the scorer callable:
        This module's scorers differ from other GSCV implementations
        in an important way. Some of those implementations accept
        'make_scorer' functions, e.g. `sklearn.metrics.make_scorer`, but
        this module cannot accept this. 'make_scorer' implicitly assumes
        a decision threshold of 0.5, but this module needs to be able to
        calculate predictions based on any user-entered threshold.
        Therefore, in place of 'make_scorer' functions, this module uses
        scoring metrics directly (whereas they would otherwise be passed
        to 'make_scorer'.) An example of a valid scoring metric is
        `sklearn.metrics.accuracy_score`.

        Additionally, this module can accept any scoring function that
        has signature (y_true, y_pred) and returns a single number. Note
        that, when using a custom scorer, the scorer should return a
        single value. Metric functions returning a list/array of values
        can be wrapped in multiple scorers that return one value each.

        This module cannot directly accept scorer kwargs and pass them
        to scorers. To pass kwargs to your scoring metric, create a
        wrapper with signature (y_true, y_pred) around the metric and
        hard-code the kwargs into the metric, e.g.,

        def your_metric_wrapper(y_true, y_pred):
            return your_metric(y_true, y_pred, \\**hard_coded_kwargs)
    n_jobs : int | None, default=None
        Number of jobs to run in parallel. -1 means using all processors.
        For best speed benefit, pybear recommends setting `n_jobs` in
        both `GSTCV` and the wrapped estimator to None, whether under a
        joblib context manager or standing alone. When under a joblib
        context manager, also set `n_jobs` in the context manager to None.
    refit : bool | str | Callable, default=True
        After the grid search is done, fit the whole dataset on the
        estimator using the best found hyperparameters and expose this
        fitted estimator via the :attr:`best_estimator_` attribute. Also,
        when the estimator is refit on the best hyperparameters, the
        `GSTCV` instance itself becomes the best estimator, exposing
        the :meth:`predict_proba`, :meth:`predict`, and :meth:`score`
        methods (and possibly others.) When refit is not performed, the
        search simply finds the best hyperparameters and exposes them via
        the `best_params_` attribute (unless there are multiple scorers
        and `refit` is False, in which case information about the grid
        search is only available via the `cv_results_` attribute.)

        The values accepted by `refit` depend on the scoring scheme, that
        is, whether a single or multiple scorers are used. In all cases,
        `refit` can be boolean False (to disable refit), a string that
        indicates the name of the scorer to use (when there is only one
        scorer there is only one possible string value), or a callable.
        See below for more information about the refit callable. When
        one scorer is used, `refit` can be boolean True or False, but
        boolean True cannot be used when there is more than one scorer.

        Where there are considerations other than maximum score in
        choosing a best estimator, `refit` can be set to a function that
        takes in `cv_results_` and returns :attr:`best_index_` (an
        integer). In that case, the returned `best_index_` sets both the
        `best_estimator_` and `best_params_` attributes. When more than
        one scorer is used, the :attr:`best_score_` and `best_threshold_`
        attributes will not be available, but are available if there is
        only one scorer.

        See the `scoring` parameter to know more about multiple metric
        evaluation.
    cv : int | Iterable | None, default=None
        Sets the cross-validation splitting strategy.

        Possible inputs for cv are:
            None, to use the default 5-fold cross validation,

            an integer, must be 2 or greater, to specify the number of
            folds in a StratifiedKFold split,

            an iterable yielding pairs of (train, test) split indices as
            arrays.

        For passed iterables:
        This module will convert generators to lists. No validation is
        done beyond verifying that it is an iterable that contains pairs
        of iterables. `GSTCV` will catch out of range indices and raise
        an error but any validation beyond that is up to the user outside
        of `GSTCV`.
    verbose : numbers.Real, default=0
        The amount of verbosity to display to screen during the grid
        search. Accepts integers from 0 to 10. 0 means no information
        displayed to the screen, 10 means full verbosity. Non-numbers
        are rejected. Boolean False is set to 0, boolean True is set to
        10. Negative numbers are rejected. Numbers greater than 10 are
        set to 10. Floats are rounded to integers.
    pre_dispatch : PreDispatchType, default='2*n_jobs'
        The number of batches (of tasks) to be pre-dispatched. Default
        is '2*n_jobs'. See the joblib.Parallel docs for more information.
    error_score : ErrorScoreType, default='raise'
        Score to assign if the estimator raises an error while fitting
        on a train fold. If set to ‘raise’, the error is raised. If a
        numeric value is given, a warning is raised and the error score
        value is inserted into the subsequent calculations in place of
        the missing value(s). This parameter does not affect the refit
        step, which will always raise the error.
    return_train_score : bool
        If False, the `cv_results_` attribute will not include training
        scores. If True, the train data is scored using all the scorers
        at the best respective threshold(s) found for the test data.
        Computing training scores is used to assess conditions of under-
        or over-fittedness. However, computing the scores on the training
        set can be computationally expensive and is not required to
        select the hyperparameters that yield the best performance.

    Attributes
    ----------
    cv_results_ : CVResultsType
        A dictionary with column headers as keys and results as values,
        that can be conveniently converted into a pandas DataFrame.
        Always exposed after fit.

        Below is an example of `cv_results_` for a logistic classifier,
        with:

        cv=3,

        param_grid={'C': [1e-5, 1e-4]},

        thresholds=np.linspace(0,1,21),

        scoring=['accuracy', 'balanced_accuracy']

        return_train_score=False

        on random data.

        {
            'mean_fit_time':                    [1.227847, 0.341168]

            'std_fit_time':                     [0.374309, 0.445982]

            'mean_score_time':                  [0.001638, 0.001676]

            'std_score_time':                   [0.000551, 0.000647]

            'param_C':                             [0.00001, 0.0001]

            'params':                  [{'C': 1e-05}, {'C': 0.0001}]

            'best_threshold_accuracy':                   [0.5, 0.51]

            'split0_test_accuracy':              [0.785243, 0.79844]

            'split1_test_accuracy':              [0.80228, 0.814281]

            'split2_test_accuracy':             [0.805881, 0.813381]

            'mean_test_accuracy':               [0.797801, 0.808701]

            'std_test_accuracy':                [0.009001, 0.007265]

            'rank_test_accuracy':                             [2, 1]

            'best_threshold_balanced_accuracy':          [0.5, 0.51]

            'split0_test_balanced_accuracy':    [0.785164, 0.798407]

            'split1_test_balanced_accuracy':    [0.802188, 0.814252]

            'split2_test_balanced_accuracy':    [0.805791, 0.813341]

            'mean_test_balanced_accuracy':      [0.797714, 0.808667]

            'std_test_balanced_accuracy':       [0.008995, 0.007264]

            'rank_test_balanced_accuracy':                    [2, 1]
        }

        Slicing across the dictionary values gives the results for a
        single permutation of grid search. That is, indexing into all of
        the masked arrays at position zero gives the result for the
        first permutation of the grid search, index 1 contains the
        results for the second permutation, and so forth.

        The key 'params' is used to store a list of parameter settings
        dictionaries for all the hyperparameter candidates. That is,
        the 'params' key holds all the possible permutations of
        hyperparameters for the given search grid(s).

        'mean_fit_time', 'std_fit_time', 'mean_score_time' and
        'std_score_time' are all in seconds.

        For single-metric evaluation, the scores for the single scorer
        are available in the `cv_results_` dict at the keys ending with
        '_score'. For multi-metric evaluation, the scores for all the
        scorers are available in the `cv_results_` dict at the keys
        ending with that scorer’s name ('_<scorer_name>'). E.g.,
        ‘split0_test_precision’, ‘mean_train_precision’, etc.
    best_estimator_ : object
        The estimator that was chosen by the search, i.e. the estimator
        which gave the highest score (or smallest loss) on the held-out
        (test) data. Only exposed when `refit` is not False; see the
        `refit` parameter for more information on allowed values.
    best_score_ : float
        The mean of the scores of the hold out (test) cv folds for the
        best estimator with the best threshold applied. Always exposed
        when there is one scorer, or when `refit` is specified as a
        string for 2+ scorers.
    best_params_ : dict[str, Any]
        The dictionary found in the :attr:`cv_results_` 'params'
        column in the :attr:`best_index_` position, which gives the
        hyperparameter settings that resulted in the highest mean score
        (`best_score_`) on the hold out (test) data with the best
        threshold applied.

        `best_params_` never holds the best threshold. Access the
        best threshold via the :attr:`best_threshold_` attribute (if
        available) or the `cv_results_` attribute.

        `best_params_` is always exposed when there is one scorer, or
        when `refit` is not False for 2+ scorers.
    best_index_ : int
        The index of the `cv_results_` arrays which corresponds to the
        best hyperparameter settings. Always exposed when there is one
        scorer, or when `refit` is not False for 2+ scorers.
    scorer_ : dict
        Scorer metric(s) used on the held out data to choose the best
        hyperparameters for the model. Always exposed after fit.

        This attribute holds the validated scoring dictionary which maps
        the scorer key to the scorer metric callable, i.e., a dictionary
        of {scorer_name: scorer_metric}.
    n_splits_ : int
        The number of cross-validation splits (folds). Always exposed
        after fit.
    refit_time_ : float
        Seconds elapsed when refitting the best model on the whole
        dataset. Only exposed when `refit` is not False.
    multimetric_ : bool
        Whether several scoring metrics were used. False if one scorer
        was used, otherwise True. Always exposed after fit.
    classes_
    n_features_in_
    feature_names_in_
    best_threshold_ : float
        The threshold that, along with the hyperparameter values found
        in `best_params_`, yields the highest score for the given
        estimator and data.

        The best threshold is only available conditionally via the
        `best_threshold_` attribute. When one scorer is used, the best
        threshold found is always exposed. When multiple scorers are
        used, the `best_threshold_` attribute is only exposed when a
        string value is passed to `refit`. Another way to find the best
        threshold for each scorer and overall is by inspection of
        `cv_results_`.

    Notes
    -----

    **Type Aliases**

    class ClassifierProtocol(Protocol):
        def fit(self, X: Any, y: Any) -> Self

        def get_params(self, **kwargs) -> dict[str, Any]

        def set_params(self, **kwargs) -> Self

        def predict_proba(self, X: Any) -> Any

    ParamGridInputType:
        dict[str, Sequence[Any]]

    ParamGridsInputType:
        Sequence[ParamGridInputType]

    ThresholdsInputType:
        None | numbers.Real | Sequence[numbers.Real]

    SKSlicerType:
        Sequence[int]

    SKKFoldType:
        tuple[SKSlicerType, SKSlicerType]

    ScorerNameTypes:
        Literal[
            'accuracy',
            'balanced_accuracy',
            'average_precision',
            'f1',
            'precision',
            'recall'
        ]

    ScorerCallableType:
        Callable[[Iterable, Iterable], numbers.Real]

    ScorerInputType:
        ScorerNameTypes | Sequence[ScorerNameTypes] | ScorerCallableType
        | dict[str, ScorerCallableType]

    RefitCallableType:
        Callable[[CVResultsType], int]

    RefitType:
        bool | ScorerNameTypes | RefitCallableType

    PreDispatchType:
        Literal['all'] | str | int

    SKXType:
        Iterable

    SKYType:
        Sequence[int]

    CVResultsType:
        dict[str, np.ma.masked_array[Any]]

    FeatureNamesInType:
        npt.NDArray[str]

    Examples
    --------
    >>> import numpy as np
    >>> from pybear.model_selection import GSTCV
    >>> from sklearn.linear_model import LogisticRegression
    >>> from sklearn.datasets import make_classification
    >>>
    >>> clf = LogisticRegression(
    ...     solver='saga',
    ...     penalty='elasticnet'
    ... )
    >>> X, y = make_classification(n_samples=1000, n_features=5, random_state=19)
    >>> param_grid = {
    ...     'C': np.logspace(-6, -3, 4),
    ...     'l1_ratio': np.linspace(0, 1, 5)
    ... }
    >>> gstcv = GSTCV(
    ...     estimator=clf,
    ...     param_grid=param_grid,
    ...     thresholds=np.linspace(0, 1, 5),
    ...     scoring='balanced_accuracy',
    ...     n_jobs=-1,
    ...     refit=False,
    ...     cv=5,
    ...     verbose=0,
    ...     pre_dispatch='2*n_jobs',
    ...     error_score='raise',
    ...     return_train_score=False
    ... )
    >>> gstcv.fit(X, y)
    GSTCV(cv=5, estimator=LogisticRegression(penalty='elasticnet', solver='saga'),
          n_jobs=-1,
          param_grid={'C': array([1.e-06, 1.e-05, 1.e-04, 1.e-03]),
                      'l1_ratio': array([0.  , 0.25, 0.5 , 0.75, 1.  ])},
          refit=False, scoring='balanced_accuracy',
          thresholds=array([0.  , 0.25, 0.5 , 0.75, 1.  ]))
    >>>
    >>> gstcv.best_params_
    {'C': 0.001, 'l1_ratio': 0.25}
    >>>
    >>> gstcv.best_threshold_
    0.5

    """


    def __init__(
        self,
        estimator:ClassifierProtocol,
        param_grid:ParamGridInputType | ParamGridsInputType,
        *,
        thresholds:ThresholdsInputType = None,
        scoring:ScorerInputType = 'accuracy',
        n_jobs:int | None = None,
        refit:bool | str | Callable = True,
        cv:int | Iterable | None = None,
        verbose:numbers.Real = 0,
        pre_dispatch:PreDispatchType = '2*n_jobs',
        error_score:ErrorScoreType = 'raise',
        return_train_score:bool = False
    ) -> None:
        """Initialize the `GSTCV` instance."""

        self.estimator = estimator
        self.param_grid = param_grid
        self.thresholds = thresholds
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.cv = cv
        self.refit = refit
        self.verbose = verbose
        self.pre_dispatch = pre_dispatch
        self.error_score = error_score
        self.return_train_score = return_train_score


    def _val_y(self, _y: SKYType) -> None:
        """Implements `GSTCV` _val_y in methods in `_GSTCVMixin`.

        See the docs for `GSTCV` _val_y.

        Parameters
        ----------
        _y : SKYType
            The target for the data.

        Returns
        -------
        None

        """

        # KEEP val of y separate
        _val_y(_y)


    def _val_params(self) -> None:
        """Validate init params that are unique to `GSTCV`.

        Returns
        -------
        None

        """

        # KEEP val of y separate
        _validation(self.estimator, self.pre_dispatch)


    def _condition_params(
        self,
        _X: SKXType,
        _y: SKYType
    ) -> None:
        """Condition GSTCV-only init params into format for internal
        processing.

        Parameters
        ----------
        _X : SKXType
            The data.
        _y : SKYType
            The target for the data.

        Returns
        -------
        None

        """

        # this is needed for GSTCV for compatibility with GSTCVMixin
        # nullcontext needs to stay. _GSTCVMixin.fit, which serves both
        # GSTCV & GSTCVDask, is mostly under a scheduler context manager.
        self._scheduler: SKSchedulerType = nullcontext()

        self._KFOLD: list[SKKFoldType]
        if isinstance(self._cv, numbers.Integral):
            self._KFOLD = list(_sk_get_kfold(_X, _y, self.n_splits_, self._verbose))
        else:  # _cv is an iterable, _cond_cv should have made list[tuple]
            self._KFOLD = self._cv


    def _fit_all_folds(
        self,
        _X:SKXType,
        _y:SKYType,
        _grid:dict[str, Any],
        _fit_params
    ) -> list[tuple[ClassifierProtocol, float, bool], ...]:
        """Fit on each train/test split for one single set of
        hyperparameter values (one permutation of GSCV).

        Parameters
        ----------
        _X : SKXType
            The data.
        _y : SKYType
            The target for the data.
        _grid : dict[str, Any]
            The values for the hyperparameters for this permutation of
            grid search.

        Returns
        -------
        FIT_OUTPUT : list[tuple[ClassifierProtocol, float, bool], ...]
            A list of tuples, one tuple for each fold, with each tuple
            holding the respective fitted estimator for that fold of
            train/test data, the fit time, and a bool indicating whether
            the fit raised an error.

        """

        # **** IMPORTANT NOTES ABOUT estimator & n_jobs ****
        # there was a (sometimes large, >> 0.10) anomaly in scores
        # when n_jobs was set to (1, None) vs. (-1, 2, 3, 4) when using
        # SK Logistic. While running the fits under a regular for-loop,
        # the SK estimator itself was found to be the cause, from being
        # fit on repeatedly without reconstruct. There appears be some
        # form of state information being retained in the estimator that
        # is altered with fit and alters subsequent fits slightly. there
        # is very little on google and ChatGPT about this (ChatGPT also
        # thinks that 'state' is the problem.) Locking random_state made
        # no difference, and locking other things with randomness (KFold,
        # etc.) made no difference. There was no experimentation done to
        # see if that problem extends beyond SK Logistic or SK. joblib
        # with n_jobs (1, None) behaves exactly the same as a regular
        # for-loop. The solution is to reconstruct the estimator with each
        # fit and fit it once - then the results agree exactly with the
        # results when n_jobs > 1 and with SK gscv. 'estimator' is being
        # rebuilt at each call with the class constructor
        # type(_estimator)(**_estimator.get_params(deep=True)).

        # must use shallow params to construct estimator
        s_p = self._estimator.get_params(deep=False)  # shallow_params
        # must use deep params for pipeline to set GSCV params (depth
        # doesnt matter for an estimator when not pipeline.)
        d_p = self._estimator.get_params(deep=True)  # deep_params

        _fold_fit_params = _sk_estimator_fit_params_helper(
            np.array(list(_y)).ravel().shape[0],  # n_samples
            _fit_params,
            self._KFOLD
        )

        with joblib.parallel_config(prefer='processes', n_jobs=self.n_jobs):
            FIT_OUTPUT = joblib.Parallel(
                return_as='list', pre_dispatch=self.pre_dispatch
            )(
                joblib.delayed(_parallelized_fit)(
                    f_idx,
                    # train only!
                    *list(zip(*_sk_fold_splitter(train_idxs, test_idxs, _X, _y)))[0],
                    type(self._estimator)(**s_p).set_params(**deepcopy(d_p)),
                    _grid,
                    self.error_score,
                    **_fold_fit_params[f_idx]
                ) for f_idx, (train_idxs, test_idxs) in enumerate(self._KFOLD)
            )

        del s_p, d_p, _fold_fit_params

        return FIT_OUTPUT


    def _score_all_folds_and_thresholds(
        self,
        _X:SKXType,
        _y:SKYType,
        _FIT_OUTPUT:list[tuple[ClassifierProtocol, float, bool], ...],
        _THRESHOLDS:ThresholdsWIPType
    ) -> list[tuple[MaskedHolderType, MaskedHolderType], ...]:
        """For each fitted estimator associated with each fold, produce
        the y_pred vector for that fold's test data and score it against
        the actual y.

        Parameters
        ----------
        _X : SKXType
            The data.
        _y : SKYType
            The target for the data.
        _FIT_OUTPUT : list[tuple[ClassifierProtocol, float, bool], ...]
            A list of tuples, one tuple for each fold, with each tuple
            holding the respective fitted estimator for that fold of
            train/test data, the fit time, and a bool indicating whether
            the fit raised an error.
        _THRESHOLDS : ThresholdsWIPType
            The thresholds for which to calculate scores.

        Returns
        -------
        TEST_SCORER_OUT : list[tuple[MaskedHolderType, MaskedHolderType], ...]
            TEST_THRESHOLD_x_SCORER__SCORE_LAYER : MaskedHolderType
                Masked array of shape (n_thresholds, n_scorers) holding
                the scores for each scorer on each threshold for one
                fold of test data.
            TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER : MaskedHolderType
                Masked array of shape (n_thresholds, n_scorers) holding
                the times to score each scorer on each threshold for one
                fold of test data.

        """

        with joblib.parallel_config(prefer='processes', n_jobs=self.n_jobs):
            TEST_SCORER_OUT = joblib.Parallel(
                return_as='list', pre_dispatch=self.pre_dispatch
            )(
                joblib.delayed(_parallelized_scorer)(
                    # test only!
                    *list(zip(*_sk_fold_splitter(train_idxs, test_idxs, _X, _y)))[1],
                    _FIT_OUTPUT[f_idx],
                    f_idx,
                    self.scorer_,
                    _THRESHOLDS,
                    self.error_score,
                    self._verbose
                ) for f_idx, (train_idxs, test_idxs) in enumerate(self._KFOLD)
            )


        return TEST_SCORER_OUT
        # END SCORE ALL FOLDS & THRESHOLDS #################################


    def _score_train(
        self,
        _X:SKXType,
        _y:SKYType,
        _FIT_OUTPUT:list[tuple[ClassifierProtocol, float, bool], ...],
        _BEST_THRESHOLDS_BY_SCORER:NDArrayHolderType
    ) -> list[MaskedHolderType]:
        # TRAIN_SCORER_OUT is TRAIN_SCORER__SCORE_LAYER
        """Using the fitted estimator for each fold, all the scorers,
        and the best thresholds for each scorer, score the train data
        for each fold using all the scorers and the single best threshold
        for the respective scorer.

        Parameters
        ----------
        _X : SKXType
            The data.
        _y : SKYType
            The target for the data.
        _FIT_OUTPUT : list[tuple[ClassifierProtocol, float, bool], ...]
            A list of tuples, one tuple for each fold, with each tuple
            holding the respective fitted estimator for that fold of
            train/test data, the fit time, and a bool indicating whether
            the fit raised an error.
        _BEST_THRESHOLDS_BY_SCORER : NDArrayHolderType
            The best threshold for each scorer as found by averaging the
            scores across each fold of test data.

        Returns
        -------
        TRAIN_SCORER_OUT : list[MaskedHolderType]
            List of masked arrays where each masked array holds the
            scores for a fold of train data using every scorer and the
            best threshold associated with that scorer.

        """

        with joblib.parallel_config(prefer='processes', n_jobs=self.n_jobs):
            TRAIN_SCORER_OUT = joblib.Parallel(
                return_as='list', pre_dispatch=self.pre_dispatch
            )(
                joblib.delayed(_parallelized_train_scorer)(
                    # train only!
                    *list(zip(*_sk_fold_splitter(train_idxs, test_idxs, _X, _y)))[0],
                    _FIT_OUTPUT[f_idx],
                    f_idx,
                    self.scorer_,
                    _BEST_THRESHOLDS_BY_SCORER,
                    self.error_score,
                    self._verbose
                ) for f_idx, (train_idxs, test_idxs) in enumerate(self._KFOLD)
            )


        return TRAIN_SCORER_OUT









