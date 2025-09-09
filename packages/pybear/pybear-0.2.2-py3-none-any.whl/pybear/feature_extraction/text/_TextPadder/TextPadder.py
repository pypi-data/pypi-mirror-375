# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
from ._type_aliases import (
    XContainer,
    XWipContainer
)

import numpy as np

from ._partial_fit._partial_fit import _partial_fit

from ._transform._transform import _transform

from ._validation import _validation

from ..__shared._transform._map_X_to_list import _map_X_to_list

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin,
    check_is_fitted
)

from ....base._copy_X import copy_X



class TextPadder(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin
):
    """Map ragged text data to a shaped array, using a fill value to
    fill out any ragged area.

    Why not just use `itertools.zip_longest`? `TextPadder` has 2 benefits
    not available with `zip_longest`.

    First, `TextPadder` (TP) can be fit on multiple batches of data and
    keeps track of which example had the most strings. TP sets that
    value as the minimum possible feature axis length for the output
    during transform, and will default to returning output with that
    exact dimensionality unless overridden by the user to a longer
    dimension.

    Second, TP can pad beyond the maximum number of features seen in the
    training data through `n_features`, whereas `zip_longest` will always
    return the tightest shape possible for the data passed.

    TP is a scikit-style transformer and has the following methods:
    `get_params`, `set_params`, `set_output`, `partial_fit`, `fit`,
    `transform`, `fit_transform`, and `score`.

    TP's methods require that data be passed as (possibly ragged) 2D
    array-like containers of string data. Accepted containers include
    Python sequences of sequences, numpy arrays, pandas dataframes, and
    polars dataframes. You may not need to use this transformer if your
    data already fits comfortably in shaped containers like dataframes!
    If you pass dataframes with feature names, the original feature
    names are not preserved.

    The :meth:`partial_fit` and :meth:`fit` methods find the length
    of the example with the most strings in it and keeps that number.
    This is the minimum length that can be set for the feature axis of
    the output at transform time. `partial_fit` method can fit data
    batch-wise and does not reset TP when called, meaning that TP can
    remember the longest example it has seen across many batches of
    data. `fit` resets the TP instance, causing it to forget any
    previously seen data, and records the maximum length anew with
    every call to it.

    During transform, TP will always force the `n_features` value to be
    at least the maximum number of strings seen in a single example
    during fitting. This is the tightest possible wrap on the data
    without truncating, what `zip_longest` would do, and what TP does
    when `n_features` is set to the default value of None. If data that
    is shorter than `n_features` is passed to :meth:`transform`, then
    all examples will be padded with the fill value to the `n_features`
    dimension. If data to be transformed has an example that is longer
    than any example seen during fitting (which means that TP was not
    fitted on this example), and is also longer than the `n_features`
    value, then an error is raised.

    By default, `transform` returns output as a Python list of Python
    lists of strings. There is some control over the output container
    via :meth:`set_output`, which allows the user to set some common
    output containers for the shaped array. `set_output` can be set to
    None which returns the default python list, 'default' which returns
    a numpy array, 'pandas' which returns a pandas dataframe, and
    'polars', which returns a polars dataframe.

    Other methods, such as :meth:`fit_transform`, :meth:`set_params`,
    and :meth:`get_params`, behave as expected for scikit-style
    transformers.

    The :meth:`score` method is a no-op that allows TP to be wrapped by
    dask_ml ParallelPostFit and Incremental wrappers.

    Parameters
    ----------
    fill : str, default = ""
        The character string to pad text sequences with.
    n_features : int | None, default = None
        The number of features to create when padding the data, i.e.,
        the length of the feature axis. When None, TP pads all examples
        to match the number of strings in the example with the most
        strings. If the user enters a number that is less than the
        number of strings in the longest example, TP will increment this
        parameter back to that value. The length of the feature axis of
        the outputted array is always the greater of this parameter or
        the number of strings in the example with the most strings.

    Attributes
    ----------
    n_features_

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[Sequence[str]]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.DataFrame

    PolarsTypes:
        polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[list[str]]

    See Also
    --------
    itertools.zip_longest

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextPadder as TP
    >>> Trfm = TP(fill='-', n_features=5)
    >>> Trfm.set_output(transform='default')
    TextPadder(fill='-', n_features=5)
    >>> X = [
    ...     ['Seven', 'ate', 'nine.'],
    ...     ['You', 'eight', 'one', 'two.']
    ... ]
    >>> Trfm.fit(X)
    TextPadder(fill='-', n_features=5)
    >>> Trfm.transform(X)
    array([['Seven', 'ate', 'nine.', '-', '-'],
           ['You', 'eight', 'one', 'two.', '-']], dtype='<U5')

    """


    def __init__(
        self,
        *,
        fill:str = '',
        n_features:int | None = None
    ) -> None:
        """Initialize the `TextPadder` instance."""

        self.fill = fill
        self.n_features = n_features


    # handled by GetParamsMixin
    # def get_params(self, deep:bool = True):

    # handled by SetParamsMixin
    # def set_params(self, **params):

    # handled by FitTransformMixin
    # def fit_transform(self, X):

    # handled by SetOutputMixin
    # def set_output(
    #     self,
    #     transform: Literal['default', 'pandas', 'polars'] | None = None
    # )


    def __pybear_is_fitted__(self) -> bool:
        return hasattr(self, '_n_features')


    def _reset(self) -> Self:
        """Reset the internal state of the `TextPadder` instance.

        Returns
        -------
        self : object
            The reset `TextPadder` instance.

        """

        if hasattr(self, '_n_features'):
            delattr(self, '_n_features')
        if hasattr(self, '_hard_n_features'):
            delattr(self, '_hard_n_features')

        return self


    @property
    def n_features_(self) -> int:
        """Get the `n_features_` attribute.

        The number of features to pad the data to during transform; the
        number of features in the outputted array. This number is the
        greater of `n_features` or the maximum number of strings seen in
        a single example during fitting.

        Returns
        -------
        n_features : int
            The number of features in the outputted shaped array.

        """

        check_is_fitted(self)

        return self._n_features


    def get_metadata_routing(self):
        """metadata routing is not implemented in TextPadder."""
        raise NotImplementedError(
            f"metadata routing is not implemented in TextPadder"
        )


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Batch-wise fitting operation.

        Find the largest number of strings in any single example across
        multiple batches of data. Update the target number of features
        for transform.

        Parameters
        ----------
        X : XContainer, (possibly ragged) shape (n_samples, n_features)
            The data.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextPadder` instance.

        """


        _validation(
            X,
            self.fill,
            self.n_features or 0
        )

        _current_n_features: int = _partial_fit(X)

        self._hard_n_features: int = max(
            _current_n_features,
            getattr(self, '_hard_n_features', 0)
        )

        self._n_features: int = max(
            self._hard_n_features,
            self.n_features or 0
        )


        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """One-shot fitting operation.

        Find the largest number of strings in any single example of the
        passed data.

        Parameters
        ----------
        X : XContainer, (possibly ragged) shape (n_samples, n_features)
            The data.
        y : Any, default = None.
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextPadder` instance.

        """

        self._reset()

        return self.partial_fit(X, y)


    @SetOutputMixin._set_output_for_transform
    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ):
        """Map ragged text data to a shaped array.

        Parameters
        ----------
        X : XContainer, (possibly ragged) shape (n_samples, n_features)
            The data to be transformed.
        copy : bool, default = False
            Whether to perform the transformation directly on `X` or on
            a deepcopy of `X`.

        Returns
        -------
        X_tr : XWipContainer
            The padded data.

        """

        check_is_fitted(self)

        _validation(
            X,
            self.fill,
            self.n_features or 0
        )

        self._n_features: int = max(
            self._hard_n_features,
            self.n_features or 0
        )


        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr : XWipContainer = _map_X_to_list(X_tr)

        X_tr = _transform(X_tr, self.fill, self._n_features)

        # the SetOutputMixin cant take python list when it actually has
        # to change the container, but when not changing the container
        # X just passes thru. so if set_output is None, just return, but
        # otherwise need to convert the list to a numpy array beforehand
        # going into the wrapper's operations.
        if getattr(self, '_output_transform', None) is None:
            return X_tr
        else:
            return np.array(X_tr)


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """No-op score method.

        Parameters
        ----------
        X : Any
            The data. Ignored
        y : Any, default = None
            The target for the data. Ignored.

        Returns
        -------
        None


        """


        check_is_fitted(self)


        return








