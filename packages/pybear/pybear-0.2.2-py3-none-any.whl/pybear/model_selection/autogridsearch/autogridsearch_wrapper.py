# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
from ._autogridsearch_wrapper._type_aliases import (
    ParamsType,
    GridsType,
    ResultsType
)

import numbers
from copy import deepcopy

from . import autogridsearch_docs

from ._autogridsearch_wrapper._type_aliases import BestParamsType

from ._autogridsearch_wrapper._print_results import _print_results

from ._autogridsearch_wrapper._validation._validation import _validation
from ._autogridsearch_wrapper._param_conditioning._conditioning import _conditioning

from ._autogridsearch_wrapper._build_first_grid_from_params import _build
from ._autogridsearch_wrapper._build_is_logspace import _build_is_logspace

from ._autogridsearch_wrapper._get_next_param_grid._get_next_param_grid \
    import _get_next_param_grid

from ._autogridsearch_wrapper._refit_can_be_skipped import _refit_can_be_skipped

from ._autogridsearch_wrapper._demo._demo import _demo

from ...base._check_is_fitted import check_is_fitted



def autogridsearch_wrapper(GridSearchParent):
    """Wrap a scikit-learn, pybear, or dask_ml `GridSearchCV` class with
    a class that overwrites the `fit` method of that `GridSearchCV`.

    The superseding fit method automates multiple calls to the parent
    `fit` method with progressively more precise search grids based on
    previous search results. See the scikit, pybear, and dask_ml
    documentation for more information about the available `GridSearchCV`
    modules.

    Parameters
    ----------
    GridSearchParent : object
        Sci-kit, pybear, or dask_ml `GridSearchCV` CLASS, not instance.

    Returns
    -------
    AutoGridSearch : object
        Wrapped `GridSearchCV` class. The original `fit` method is
        replaced with a new `fit` method that can make multiple calls to
        the original `fit` method with increasingly precise search grids.

    See Also
    --------
    sklearn.model_selection.GridSearchCV
    pybear.model_selection.GSTCV
    pybear-dask.model_selection.GSTCVDask

    Examples
    --------
    >>> from pybear.model_selection import autogridsearch_wrapper
    >>> from sklearn.model_selection import GridSearchCV as sk_GSCV
    >>> from sklearn.linear_model import Ridge as sk_RR
    >>> from sklearn.datasets import make_regression
    >>>
    >>> AGSCV = autogridsearch_wrapper(sk_GSCV)
    >>> _params = {
    ...     'alpha': [[0, 0.1, 0.2], 3, 'soft_float'],
    ...     'fit_intercept': [[True, False], [2, 1, 1], 'fixed_bool']
    ... }
    >>> agscv = AGSCV(estimator=sk_RR(), params=_params, total_passes=3)
    >>> X, y = make_regression(n_samples=20, n_features=2, n_informative=2)
    >>> agscv.fit(X, y)   #doctest:+SKIP
    AutoGridSearch(
        estimator=Ridge(),
        params={
            'alpha': [[0.0, 0.1, 0.2], [3, 3, 3], 'soft_float'],
            'fit_intercept': [[True, False], [2, 1, 1], 'fixed_bool']
        },
        total_passes=3
    )
    >>> print(agscv.RESULTS_[1])   #doctest:+SKIP
    {'alpha': 0.025, 'fit_intercept': True}

    """

    from ...base.mixins._GetParamsMixin import GetParamsMixin
    from ...base.mixins._SetParamsMixin import SetParamsMixin


    class AutoGridSearch(GridSearchParent):

        def __init__(
            self,
            estimator,
            params:ParamsType,
            *,
            total_passes:int = 5,
            total_passes_is_hard:bool = False,
            max_shifts:int | None = None,
            agscv_verbose:bool = False,
            **parent_gscv_kwargs
        ) -> None:
            """Initialize the `AutoGridSearch` instance."""

            self.estimator = estimator
            self.params = params
            self.total_passes = total_passes
            self.total_passes_is_hard = total_passes_is_hard
            self.max_shifts = max_shifts
            self.agscv_verbose = agscv_verbose

            super().__init__(self.estimator, {}, **parent_gscv_kwargs)

        # END __init__() ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        @property
        def GRIDS_(self) -> GridsType:
            """Get the `GRIDS_` attribute.

            Dictionary of search grids used on each pass of agscv. As
            `AutoGridSearch` builds search grids for each pass, they are
            stored in this attribute. The keys of the dictionary are the
            zero-indexed pass number, i.e., external pass number 2 is
            key 1 in this dictionary.

            Returns
            -------
            GRIDS_ : GridsType
                Dictionary of param_grids run on each pass.

            """
            check_is_fitted(self)
            return self._GRIDS


        @property
        def RESULTS_(self) -> ResultsType:
            """Get the `RESULTS_` attribute.

            Dictionary of `best_params_` for each agscv pass. The keys
            of the dictionary are the zero-indexed pass number, i.e.,
            external pass number 2 is key 1 in this dictionary. The
            final key holds the most precise estimates of the best
            hyperparameter values for the given estimator and data.

            Returns
            -------
            RESULTS_ : dict[int, dict[str, Any]]
                Dictionary of `best_params_` for each pass.

            """

            check_is_fitted(self)
            return self._RESULTS


        @property
        def params_(self) -> ParamsType:
            """Get the `params_` attribute.

            If the `params` parameter is modified during the
            `AutoGridSearch` session, the changes are captured in this
            work-in-process object. This is the version of `params` that
            was actually used during the `AutoGridSearch` session. Events
            that alter the originally-passed `params` include the initial
            conversion of integer 'points' to a list of points, and shift
            passes, which always extend the list of points.

            Returns
            -------
            params_ : ParamsType
                The version of `params` that was actually used during the
                `AutoGridSearch` session.

            """

            check_is_fitted(self)
            return self._params


        def __pybear_is_fitted__(self) -> bool:
            return hasattr(self, '_GRIDS')


        def demo(
            self,
            *,
            true_best_params:BestParamsType | None = None,
            mock_gscv_pause_time:numbers.Real = 5
        ):
            """Simulated trials of this `AutoGridSearch` instance.

            Assess AutoGridSearch's ability to generate appropriate
            grids with the given parameters (`params`) against mocked
            true best values. Visually inspect the generated grids and
            performance of the `AutoGridSearch` instance in converging
            to the mock targets provided in `true_best_params`. If no
            true best values are provided via `true_best_params`, random
            true best values are generated from the set of first search
            grids provided in `params`.

            Parameters
            ----------
            true_best_params : BestParamsType | None, default = None
                Python dictionary of mocked true best values for an
                estimator's hyperparameters, as provided by the user.
                If not passed, random true best values are generated
                based on the first round grids made from the instructions
                in `params`.
            mock_gscv_pause_time : numbers.Real, default = 5
                Time in seconds to pause, simulating work being done by
                the parent GridSearch.

            Returns
            -------
            _DemoCls : object
                The AutoGridSearch instance created to run simulations,
                not the instance created by the user. This return is
                integral for tests of the demo functionality, but has no
                other internal use.

            """

            _validation(
                self.params,
                self.total_passes,
                self.total_passes_is_hard,
                self.max_shifts,
                self.agscv_verbose
            )

            _params, _total_passes, _max_shifts = _conditioning(
                self.params,
                self.total_passes,
                self.max_shifts,
                _inf_max_shifts=1_000_000
            )

            _DemoCls = AutoGridSearch(
                # must pass est to init parent GSCV even tho not used
                self.estimator,
                params=_params,
                total_passes=_total_passes,
                total_passes_is_hard=self.total_passes_is_hard,
                max_shifts=_max_shifts,
                agscv_verbose=False
            )

            _demo(
                _DemoCls,
                _true_best=true_best_params,
                _mock_gscv_pause_time=mock_gscv_pause_time
            )

            return _DemoCls   # for tests purposes only


        def print_results(self) -> None:
            """Print search grids and best values to the screen for all
            parameters in all passes.

            Returns
            -------
            None

            """

            check_is_fitted(self)

            _print_results(self._GRIDS, self._RESULTS)


        def get_params(self, deep:bool = True) -> dict[str, Any]:
            """Get parameters for this `AutoGridSearch` instance.

            Parameters
            ----------
            deep : bool, default = True
                `deep=False` will only return the parameters for the
                wrapping `AutoGridSearch` class not the nested
                estimator. When `deep=True`, this method returns the
                parameters of the `AutoGridSearch` instance as well
                as the parameters of the nested estimator. If the nested
                estimator is a pipeline, the parameters of the pipeline
                and the parameters of each of the steps in the pipeline
                are returned in addition to the parameters of the
                `AutoGridSearch` instance. The estimator's parameters
                are prefixed with `estimator__`.

            Returns
            -------
            params : dict[str, Any]
                Parameter names mapped to their values.

            """

            # pybear get_params must be used because the parent GSCVs
            # get_params only looks at the signature of the wrapper, it
            # does not see the parameters exposed by super().__init__().
            # so calls to the parent get_params will only show the params
            # for the agscv wrapper, not the parent GridSearchCV also.
            # serendipitous windfall that the pybear get_params can see
            # all the params for both the wrapper and the parent.

            return GetParamsMixin.get_params(self, deep=deep)


        def set_params(self, **params):
            """Set the parameters of the `AutoGridSearch` instance or
            the nested estimator.

            Setting the parameters of the GridSearch instance (but not
            the nested estimator) is straightforward. Pass the exact
            parameter name and its value as a keyword argument to the
            `set_params` method call. Or use ** dictionary unpacking on
            a dictionary keyed with exact parameter names and the new
            parameter values as the dictionary values. Valid parameter
            keys can be listed with :meth:`get_params`.

            The parameters of nested estimators can be updated using
            prefixes on the parameter names. Simple estimators can be
            updated by prefixing the estimator's parameters with
            'estimator__'. For example, if some estimator has a 'depth'
            parameter, then setting the value of that parameter to 3
            would be accomplished by passing estimator__depth=3 as a
            keyword argument to the `set_params` method call.

            The parameters of a nested pipeline can be updated using
            the form estimator__<pipe_parameter>. The parameters of
            the steps of a pipeline have the form <step>__<parameter>
            so that it’s also possible to update a step's parameters
            through the `set_params` method interface. The parameters
            of steps in the pipeline can be updated using
            'estimator__<step>__<parameter>'.

            Parameters
            ----------
            **params : dict[str: Any]
                The parameters to be updated and their new values.

            Returns
            -------
            self : object
                The `AutoGridSearch` instance with new parameter values.

            """

            # it is not absolutely necessary to use the pybear set_params
            # method to set parameters for the wrapper and the nested
            # estimator like it is for get_params, the parent GSCV
            # set_params works (at least for sklearn.GridSearchCV.) Using
            # pybear here to hedge bets on the future and use as much
            # pybear-native as possible (which means less dependence on
            # 3rd party.)

            SetParamsMixin.set_params(self, **params)

            return self


        def fit(
            self,
            X,
            y:Any | None = None,
            groups:Any = None,
            **fit_params
        ) -> Self:
            """Run the parent's `fit` method at least `total_passes`
            number of times with increasingly precise search grids.

            Supersedes the parent `GridSearchCV` fit method.

            Parameters
            ----------
            X : array_like
                The training data.
            y: Any, default = None
                Target for the training data.
            groups : Any | None, default = None
                Group labels for the samples used while splitting the
                dataset into train/tests sets. agscv exposes this for
                parent GridSearch classes that have this keyword argument
                in their fit method. See the docs of GridSearch classes
                that expose this keyword argument for more information.

            Returns
            -------
            self : object
                The `AutoGridSearch` instance.

            """

            _validation(
                self.params,
                self.total_passes,
                self.total_passes_is_hard,
                self.max_shifts,
                self.agscv_verbose
            )

            self._params, _total_passes, _max_shifts = _conditioning(
                self.params,
                self.total_passes,
                self.max_shifts,
                _inf_max_shifts=1_000_000
            )

            _shift_ctr = 0

            # IS_LOGSPACE IS DYNAMIC, WILL CHANGE WHEN A PARAM'S LOGSPACE
            # SEARCH GRID INTERVAL IS REGAPPED TO 1 OR TRANSITIONS FROM
            # LOGSPACE TO LINSPACE
            _IS_LOGSPACE = _build_is_logspace(self._params)

            # ONLY POPULATE PHLITE WITH numerical_params WITH "soft"
            # BOUNDARY AND START AS FALSE
            _PHLITE = {}
            for hprmtr in self._params:
                if 'soft' in self._params[hprmtr][-1].lower():
                    _PHLITE[hprmtr] = False

            # skip refits before the last pass if possible to save time.
            # see the notes in _refit_can_be_skipped()
            _early_refits_can_be_skipped = _refit_can_be_skipped(
                GridSearchParent,
                getattr(self, 'scoring', False),
                _total_passes
            )

            _pass = 0
            while _pass < _total_passes:

                # Assignments to self._GRIDS will be made in
                # _get_next_param_grid()
                if _pass == 0:
                    # build the first search grid here
                    self._GRIDS = _build(self._params)
                else:
                    # build all other search grids here
                    self._GRIDS, self._params, _PHLITE, _IS_LOGSPACE, _shift_ctr, \
                    _total_passes = _get_next_param_grid(
                        self._GRIDS,   #  should have been made on pass 0
                        self._params,
                        _PHLITE,
                        _IS_LOGSPACE,
                        _best_params_from_previous_pass,
                        _pass,
                        _total_passes,
                        self.total_passes_is_hard,
                        _shift_ctr,
                        _max_shifts
                    )

                if self.agscv_verbose:
                    print(f"\nPass {_pass+1} starting grids:")
                    for k, v in self._GRIDS[_pass].items():
                        try:
                            _fgrid = list(map(round, v, (4 for _ in v)))
                            print(f'{k[:15]}'.ljust(20), _fgrid)
                            del _fgrid
                        except:
                            print(f'{k[:15]}'.ljust(20), v)

                # Should GridSearchCV param_grid format ever change, code
                # would go here to adapt the _get_next_param_grid() output
                # to the required GridSearchCV.param_grid format
                _ADAPTED_GRIDS = deepcopy(self._GRIDS)

                # (the param_grid/param_distributions/parameters attribute
                # of the parent GSCV is overwritten and GSCV is fit())
                # total_passes times. After a run of AutoGSCV, the final
                # results held in the final pass attrs and methods of
                # GSCV are exposed by AutoGridSearch.

                self.param_grid = _ADAPTED_GRIDS[_pass]
                self.param_distributions = _ADAPTED_GRIDS[_pass]
                self.parameters = _ADAPTED_GRIDS[_pass]

                del _ADAPTED_GRIDS

                # ******************************************************
                # ONLY REFIT ON THE LAST PASS TO SAVE TIME WHEN POSSIBLE
                if _early_refits_can_be_skipped:
                    if _pass == 0:
                        _original_refit = self.refit
                        self.refit = False
                    elif _pass == _total_passes - 1:
                        self.refit = _original_refit
                        del _original_refit
                # **** END ONLY REFIT ON THE LAST PASS TO SAVE TIME ****
                # ******************************************************

                if self.agscv_verbose:
                    print(f'Running GridSearch... ', end='')

                try:
                    super().fit(X, y=y, groups=groups, **fit_params)
                except:
                    super().fit(X, y=y, **fit_params)

                if self.agscv_verbose:
                    print(f'Done.')

                # added 25_04_19. no longer conditioning gscv params to
                # coddle the gscvs into exposing best_params_. the user
                # gets the exact output that the gscv gives for the given
                # inputs. no longer using custom code for sk & other
                # gscvs to block settings that (perhaps at one point in
                # time) did not expose best_params_. just ask the horse
                # itself if best_params_ was exposed for the given params
                # and raise if not.
                if not hasattr(self, 'best_params_'):
                    raise ValueError(
                        f"The parent gridsearch did not expose a "
                        f"'best_params_' attribute after the first fit. "
                        f"\n'best_params_' must be exposed for agscv to "
                        f"calculate search grids. \nConfigure the parent "
                        f"gridsearch to expose 'best_params_'. \nSee the "
                        f"documentation for {GridSearchParent.__name__} "
                        f"to configure your gridsearch settings to expose "
                        f"'best_params_."
                    )

                _best_params = self.best_params_

                if self.agscv_verbose:
                    print(f"Pass {_pass + 1} best params: ")
                    for k,v in _best_params.items():
                        try:
                            print(f'{k[:15]}'.ljust(20), f'{v:,.4f}')
                        except:
                            print(f'{k[:15]}'.ljust(20), v)

                # Should GridSearchCV best_params_ format ever change,
                # code would go here to adapt the GridSearchCV.best_params_
                # output to the required self._RESULTS format
                adapted_best_params = deepcopy(_best_params)

                # best_params_ IS ASSIGNED TO THE pass/idx IN
                # self._RESULTS WITHOUT MODIFICATION
                self._RESULTS = getattr(self, '_RESULTS', {})
                self._RESULTS[_pass] = adapted_best_params
                _best_params_from_previous_pass = adapted_best_params
                # _bpfpp GOES BACK INTO self.get_next_param_grid

                del adapted_best_params

                _pass += 1

            del _early_refits_can_be_skipped, _best_params_from_previous_pass

            if self.agscv_verbose:
                print(
                    f"\nfit successfully completed {_total_passes} "
                    f"pass(es) with {_shift_ctr} shift pass(es)."
                )


            return self


    # this is likely being correctly assigned but pycharm tool tip
    # does not show it
    AutoGridSearch.__doc__ = autogridsearch_docs.__doc__
    AutoGridSearch.__init__.__doc__ = autogridsearch_docs.__doc__


    return AutoGridSearch







