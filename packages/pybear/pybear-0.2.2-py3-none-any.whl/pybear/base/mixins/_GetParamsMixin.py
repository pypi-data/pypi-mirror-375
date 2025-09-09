# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)

from copy import deepcopy
import inspect



class GetParamsMixin:
    """Provides the `get_params` method to estimators, transformers,
    and GridSearch modules.
    """


    def get_params(self, deep:bool = True) -> dict[str, Any]:
        """Get parameters for this instance.

        The 'instance' may be a pybear estimator, transformer, or a
        gridsearch module that wraps a nested estimator or pipeline.

        Parameters
        ----------
        deep : bool, default = True
            For instances that do not have nested instances in an
            `estimator` attribute (such as estimators or transformers),
            this parameter is ignored and the same (full) set of
            parameters for the instance is returned regardless of the
            value of this parameter.

            For instances that have nested instances (such as a
            GridSearch instance with a nested estimator or pipeline) in
            the `estimator` attribute, `deep=False` will only return the
            parameters for the wrapping instance. For example, a
            GridSearch module wrapping an estimator will only return
            parameters for the GridSearch instance, ignoring the
            parameters of the nested instance. When `deep=True`, this
            method returns the parameters of the wrapping instance as
            well as the parameters of the nested instance. When the
            nested instance is a single estimator, the full set of
            parameters for the single estimator are returned in addition
            to the parameters of the wrapping instance. If the nested
            object is a pipeline, the parameters of the pipeline and the
            parameters of each of the steps in the pipeline are returned
            in addition to the parameters of the wrapping instance. The
            estimator's parameters are prefixed with `estimator__`.

        Returns
        -------
        params : dict[str, Any]
            Parameter names mapped to their values.

        """

        # this module attempts to replicate the behavior of sklearn
        # get_params() exactly, for single estimators, grid search, and
        # pipelines, for deep==True/False.

        # sklearn 1.5.2 extracts parameter names from the signature of
        # the class. This modules uses the python builtin 'vars' to get
        # all the params of a class, whether it be a single estimator,
        # GSCV, or pipeline. get_params presents all params in
        # alphabetical order, which is not native vars behavior, there
        # must be a sort step. All params with leading and trailing
        # underscores are removed. This is what is returned in paramsdict
        # for single estimators whether deep == True or False. This is
        # also what is returned when deep is False for GSCV and pipelines.
        # When deep==True for GSCV & pipeline wrappers, the shallow
        # params of the wrapper are returned as well as
        # get_params(deep=True) for the estimator; deep=True on the
        # embedded does not matter if it is a simple estimator, but it
        # does matter if the embedded is a pipeline. For deep=True, and
        # sorting the params in ascending alphabetical order, paramsdict
        # is split before the estimator param, and all the deep
        # parameters of the estimator are inserted before the estimator
        # param.

        # validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # catch child of GetParamsMixin is class (not instance)

        # this catches if trying to make get_params calls on a top-level
        # that isnt instantiated when 'deep' is passed like get_params(deep),
        # not get_params(deep=deep). get_params() and get_params(deep=deep)
        # are caught by python signature related errors when the top-level
        # is a class.

        if not hasattr(self, 'get_params'):
            raise TypeError(
                f":meth: 'get_params' is being called on the class, not an "
                f"instance. Instantiate the class, then call get_params."
            )

        # END catch invalid estimator/transformer or class (not instance)

        if not isinstance(deep, bool):
            raise ValueError(f"'deep' must be boolean")
        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


        paramsdict = {}
        for attr in sorted(vars(self)):
            # after fit, take out all the attrs with leading or trailing '_'
            if attr[0] == '_' or attr[-1] == '_':
                continue

            if attr == 'scheduler': # cant pickle asyncio object
                paramsdict[attr] = vars(self)[attr]
            else:
                paramsdict[attr] = deepcopy(vars(self)[attr])


        # gymnastics to get param order the same as sklearn. this splits
        # paramsdict into 2 separate dictionaries. The first holds
        # everything in paramsdict up until estimator. The second
        # holds estimator and every param after that. this requires that
        # the output of vars (the parameter names) is sorted into asc
        # alphabetical order.
        paramsdict1 = {}
        paramsdict2 = {}
        key = 0
        for k in sorted(paramsdict):
            if k == 'estimator':
                key = 1
            if key == 0:
                paramsdict1[k] = paramsdict.pop(k)
            else:
                paramsdict2[k] = paramsdict.pop(k)
        del key, paramsdict


        # if getting the params of an embedded estimator, append those
        # to the end of the first dict. when the two dicts are combined,
        # the 'estimator' param will be after all the params of that
        # estimator.
        if deep and 'estimator' in paramsdict2:

            # if 'estimator' is not a valid estimator/transformer with a
            # get_params method, or is a class not an insstance
            if inspect.isclass(paramsdict2['estimator']) or \
                    not hasattr(paramsdict2['estimator'], 'get_params'):
                raise TypeError(
                    f"'estimator' must be an instance (not class) of a valid "
                    f"estimator or transformer that has a get_params method."
                )

            estimator_params = {}
            for k, v in deepcopy(self.estimator.get_params(deep)).items():
                estimator_params[f'estimator__{k}'] = v

            paramsdict1 = paramsdict1 | estimator_params


        paramsdict = paramsdict1 | paramsdict2

        del paramsdict1, paramsdict2

        return paramsdict




