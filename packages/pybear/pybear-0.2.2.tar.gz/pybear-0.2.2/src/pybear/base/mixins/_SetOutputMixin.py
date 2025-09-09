# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
)

import inspect
from functools import wraps

import numpy as np
import pandas as pd
import polars as pl

from pybear.utilities._nan_masking import nan_mask



class SetOutputMixin:
    """This mixin provides the `set_output` method to pybear transformers.

    Use `set_output` to set the container of the output for `transform`
    and `fit_transform` (when the FitTransformMixin is used.) Use the
    `_set_output_for_transform` method to decorate `transform` in
    the child class. This rendition of `set_output` does not require
    that the `get_feature_names_out` method exist. If there is no
    `get_feature_names_out` method, range(X.shape[1]) is passed to
    pandas/polars for column names.

    """

    def set_output(
        self,
        transform: Literal['default', 'pandas', 'polars'] | None = None
    ):
        """Set the output container when the `transform` and
        `fit_transform` methods of the transformer are called.

        Parameters
        ----------
        transform : Literal['default', 'pandas', 'polars'] | None,

            The default value for the `transform` parameter is None.

            Configure the output of `transform` and `fit_transform`.

            'default': Default output format (numpy array)

            'pandas': pandas dataframe output

            'polars': polars dataframe output

            None: The output container is the same as the given container.

        Returns
        -------
        self : object
            The transformer instance.

        """

        # validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        ALLOWED = [None, "default", "pandas", "polars"]

        err_msg = (
            f":param: 'transform' must be in {', '.join(map(str, ALLOWED))}. "
            f"got '{transform}'."
        )

        if not isinstance(transform, (str, type(None))):
            raise TypeError(err_msg)

        if transform not in ALLOWED:
            raise ValueError(err_msg)

        del err_msg, ALLOWED

        # END validation ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        self._output_transform = transform

        return self


    def _set_output_for_transform(foo):
        """This method decorates `transform` in pybear transformers.

        When `SetOutputMixin` is passed to a child transformer, decorate the
        `transform` method with @SetOutputMixin._set_output_for_transform.

        """


        foo_signature = inspect.signature(foo)

        @wraps(foo)
        def bar(self, *args, **kwargs):

            # Bind the arguments passed to bar to foo's signature
            bound_args = foo_signature.bind(self, *args, **kwargs)
            bound_args.apply_defaults() # Apply default values where needed

            # Call the original function with the bound arguments
            out = foo(*bound_args.args, **bound_args.kwargs)

            if not isinstance(out, tuple):
                X = out
                y = None
            elif len(out) == 2:
                X, y = out
            else:
                _name = {self.__class__.__name__}
                raise ValueError(
                    f"unexpected return from {_name}.transform(). expected "
                    f"1 output (X) or 2 outputs (X, y), but got {len(out)}."
                )

            # if 'set_output' has not been called on the instance of the
            # child, '_output_transform' will not exist.
            output_container = getattr(self, '_output_transform', None)

            # dont worry about 'copy' here. the child transform took care
            # of that, 'out' is the output of transform after the 'copy'
            # setting has been applied. OK to act directly on X.

            if output_container is None:
                pass
            elif output_container == 'default':
                if isinstance(X, np.ndarray):
                    pass
                elif isinstance(X, pd.DataFrame):
                    X = X.to_numpy()
                elif isinstance(X, pl.DataFrame):
                    X = X.to_numpy()
                elif hasattr(X, 'toarray'):
                    X = X.toarray()
                else:
                    raise TypeError(f"unsupported X container {type(X)}")
            elif output_container == 'pandas':
                if hasattr(self, 'get_feature_names_out'):
                    _columns = self.get_feature_names_out().tolist()
                else:
                    _columns = range(X.shape[1])
                if isinstance(X, np.ndarray):
                    X = pd.DataFrame(X, columns=_columns)
                elif isinstance(X, pd.DataFrame):
                    pass
                elif isinstance(X, pl.DataFrame):
                    X = X.to_pandas()
                elif hasattr(X, 'toarray'):
                    # as of 25_01_24, pandas can only convert csc & csr directly
                    # map all ss to csr then make dataframe
                    # # 25_01_26 with .tocsr() is excepting on py3.9.
                    X = pd.DataFrame(X.toarray(), columns=_columns)
                else:
                    raise TypeError(f"unsupported X container {type(X)}")
            elif output_container == 'polars':
                if hasattr(self, 'get_feature_names_out'):
                    _columns = self.get_feature_names_out().tolist()
                else:
                    _columns = range(X.shape[1])
                # polars PyString really hates numpy.nan, but loves None.
                # all polars dtypes love None! cast all nan-likes to None
                # before converting numpy and scipy to polars.
                if isinstance(X, np.ndarray):
                    # trying to assign None to an int array will except,
                    # even with an empty mask, so conditionally assign
                    _NAN_MASK = nan_mask(X)
                    if np.any(_NAN_MASK):
                        X[_NAN_MASK] = None
                    del _NAN_MASK
                    X = pl.DataFrame(X, orient='row')
                elif isinstance(X, pd.DataFrame):
                    X = pl.from_pandas(X)
                elif isinstance(X, pl.DataFrame):
                    pass
                elif hasattr(X, 'toarray'):
                    # unfortunately X must have a .data attribute to
                    # recast the nans. we are allowing all scipy but at
                    # least dok doesnt have a .data attr. so convert and
                    # convert back.
                    _og_dtype = type(X)
                    X = X.tocsr()
                    # trying to assign None to an int array will except,
                    # even with an empty mask, so conditionally assign
                    _NAN_MASK = nan_mask(X.data)
                    if np.any(_NAN_MASK):
                        X.data[_NAN_MASK] = None
                    del _NAN_MASK
                    X = _og_dtype(X)
                    del _og_dtype
                    X = pl.DataFrame(X.toarray(), schema=_columns, orient='row')
                else:
                    raise TypeError(f"unsupported X container {type(X)}")
            else:
                raise ValueError(
                    f"unexpected 'set_output' value '{output_container}'."
                )

            if y is not None:
                return X, y
            else:
                return X

        bar.__signature__ = foo_signature

        return bar





