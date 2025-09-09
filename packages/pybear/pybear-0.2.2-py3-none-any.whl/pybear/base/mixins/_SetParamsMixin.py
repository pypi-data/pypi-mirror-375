# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing_extensions import Self

from copy import deepcopy



class SetParamsMixin:
    """Provides the `set_params` method to estimators, transformers,
    and GridSearch modules.
    """


    def set_params(self, **params) -> Self:
        """Set the parameters of an instance or a nested instance.

        This method works on simple estimator and transformer instances
        as well as on nested objects (such as GridSearch instances).

        Setting the parameters of simple estimators and transformers is
        straightforward. Pass the exact parameter name and its value
        as a keyword argument to the `set_params` method call. Or use
        ** dictionary unpacking on a dictionary keyed with exact
        parameter names and the new parameter values as the dictionary
        values. Valid parameter keys can be listed with :meth:`get_params`.

        Setting the parameters of a GridSearch instance (but not the
        nested instance) can be done in the same way as above. The
        parameters of nested instances can be updated using prefixes
        on the parameter names.

        Simple estimators in a GridSearch instance can be updated by
        prefixing the estimator's parameters with `estimator__`. For
        example, if some estimator has a 'depth' parameter, then setting
        the value of that parameter to 3 would be accomplished by passing
        `estimator__depth=3` as a keyword argument to the `set_params`
        method call.

        The parameters of a pipeline nested in a GridSearch instance
        can be updated using the form `estimator__<pipe_parameter>`.
        The parameters of the steps of a pipeline have the form
        `<step>__<parameter>` so that it’s also possible to update a
        step's parameters through the `set_params` method interface.
        The parameters of steps in the pipeline can be updated using
        `estimator__<step>__<parameter>`.

        Parameters
        ----------
        **params : dict[str: Any]
            The parameters to be updated and their new values.

        Returns
        -------
        self : object
            The instance with new parameter values.

        """

        # validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # catch invalid estimator/transformer or class (not instance)

        # this catches if trying to make set_params calls on a top-level
        # that isnt instantiated.
        if not hasattr(self, 'set_params'):
            raise TypeError(
                f":meth: 'set_params' is being called on the class, not an "
                f"instance. Instantiate the class, then call set_params."
            )
        # END catch invalid estimator/transformer or class (not instance)

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


        if not len(params):
            return self

        # estimators, pipelines, and gscv all raise exception for invalid
        # keys (parameters) passed

        # make lists of what parameters are valid
        # use shallow get_params to get valid params for top level instance
        ALLOWED_TOP_LEVEL_PARAMS = list(self.get_params(deep=False).keys())
        # use deep get_params to get valid sub params for nested
        # estimator/pipe (if applicable, ALLOWED_SUB_PARAMS could stay empty)
        ALLOWED_SUB_PARAMS = []
        for k in self.get_params(deep=True):
            # get_params() deep==False & deep==True must be equal for a simple
            # estimator / transformer. If they are not, then must be dealing
            # with a nested object, which must have an 'estimator' param.
            # the diff between deep==True and deep==False must be the params
            # that are associated with 'estimator', and all must be prefixed
            # with 'estimator__'.
            if k not in ALLOWED_TOP_LEVEL_PARAMS:

                if 'estimator__' not in k:
                    raise ValueError(
                        f"set_params algorithm failure: a 'deep' param that is "
                        f"not in 'shallow' params is not prefixed by 'estimator__'"
                    )

                ALLOWED_SUB_PARAMS.append(k.replace('estimator__', ''))


        # separate the GIVEN top-level and sub parameters
        GIVEN_TOP_LEVEL_PARAMS = {}
        GIVEN_SUB_PARAMS = {}
        # if top-level does not have an 'estimator' param, then
        # there shouldnt be any params with 'estimator__'. only collect
        # and parse 'estimator__' params if there is in estimator.
        if hasattr(self, 'estimator'):

            for k,v in params.items():
                if 'estimator__' in k:
                    GIVEN_SUB_PARAMS[k.replace('estimator__', '')] = v
                else:
                    GIVEN_TOP_LEVEL_PARAMS[k] = v
        else:
            GIVEN_TOP_LEVEL_PARAMS = deepcopy(params)
        # END separate the GIVEN top-level and sub parameters


        def _invalid_param(parameter: str, ALLOWED: list) -> None:
            raise ValueError(
                f"Invalid parameter '{parameter}' for estimator "
                f"{type(self).__name__}(). \nValid parameters are: "
                f"{ALLOWED}."
            )


        # set top-level params
        # must be validated & set the long way
        for top_level_param, value in GIVEN_TOP_LEVEL_PARAMS.items():
            if top_level_param not in ALLOWED_TOP_LEVEL_PARAMS:
                _invalid_param(top_level_param, ALLOWED_TOP_LEVEL_PARAMS)
            setattr(self, top_level_param, value)

        # if top-level is a simple estimator/transformer, then short
        # circuit out, bypassing everything that involves an 'estimator'
        # attr.
        if not hasattr(self, 'estimator'):

            return self

        # v v v v v EVERYTHING BELOW IS FOR A NESTED v v v v v v v v v

        # set sub params ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # there is no validation here for inspect.isclass(self.estimator)
        # or not hasattr(self.estimator, 'set_params') because whatever
        # would blow set_params up here would have blown up at
        # self.get_params(deep=True). remember that if using the
        # SetParamsMixin then the GetParamsMixin must also be used!

        # IF self.estimator is sklearn-like est/pipe, IT SHOULD
        # HANDLE EXCEPTIONS FOR INVALID PASSED PARAMS..... <continued>....

        self.estimator.set_params(**GIVEN_SUB_PARAMS)

        # BUT IN CASE IS DOESNT....
        # this is stop-gap validation in case a nested estimator
        # (of a makeshift sort, perhaps) does not block setting invalid
        # params.
        for sub_param in GIVEN_SUB_PARAMS:
            if sub_param not in ALLOWED_SUB_PARAMS:
                _invalid_param(sub_param, ALLOWED_SUB_PARAMS)
        # END set estimator params ** * ** * ** * ** * ** * ** * ** * **

        del ALLOWED_SUB_PARAMS, ALLOWED_TOP_LEVEL_PARAMS, _invalid_param

        return self





