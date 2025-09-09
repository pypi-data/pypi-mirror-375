# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
)
from typing_extensions import Self
from ._type_aliases import XContainer

import numpy as np

from ._validation._X import _val_X
from ._transform._transform import _transform

from ...base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)

from ...base._copy_X import copy_X



class NanStandardizer(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Convert all nan-like representations in a dataset to the same value.

    Standardize different nan-likes to the same nan-like value, or change
    them to a non-nan-like value. "nan-like representations" recognized
    by this transformer include, at least, np.nan, pandas.NA, None (of
    type None, not string "None"), and string representations of "nan".

    For details, see the docs for `nan_mask_numerical` and
    `nan_mask_string`.

    This transformer accepts Python built-ins, numpy arrays, pandas
    dataframes/series, and polars dataframes/series of shape (n_samples,
    n_features) or (n_samples, ) and returns the same container with the
    value specified by the `new_value` parameter in the former positions
    of nan-like values. Also, when passing numerical data, this
    transformer accepts scipy sparse matrices / arrays of all formats
    except dok and lil. In that case, the original container is returned
    with the replacements made in the `data` attribute.

    NanStandardizer (NS) is a full-fledged scikit-style transformer with
    `partial_fit`, `fit`, `transform`, `fit_transform`, `get_params`,
    `set_params`, and `score` methods. The `partial_fit`, `fit`, and
    `score` methods are no-ops that are available so that NS can be
    incorporated into larger workflows like scikit pipelines and dask_ml
    wrappers. NS is technically always in a fitted state because it does
    not to need to learn anything from data to do transformations, it
    knows everything it needs to know from its parameters. Tests for
    fittedness of a NS instance will always return True.

    NS does not track the number of features in the data or the feature
    names. Attributes like `n_features_in_`, `feature_names_in_` and
    methods like `get_feature_names_out` are not available. You should
    be able to pass any valid container at any time, regardless of what
    containers NS has seen previously.

    Parameters
    ----------
    new_value : Any, default=np.nan
        The new value to put in place of the nan-like values. There is
        no validation for this value, the user is free to enter whatever
        they like. If there is a casting problem, i.e., the receiving
        object, the data, will not receive the given value, then any
        exceptions would be raised by the receiving object.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence | Sequence[Sequence]

    NumpyTypes:
        numpy.ndarray

    PandasTypes:
        pandas.DataFrame | pandas.Series

    PolarsTypes:
        polars.DataFrame | polars.Series

    SparseTypes: (
        ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
        | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
        | ss._bsr.bsr_array
    )

    XContainer:
        PythonTypes | NumpyTypes | PandasType | PolarsType | SparseTypes

    See Also
    --------
    pybear.utilities.nan_mask_numerical
    pybear.utilities.nan_mask_string
    numpy.nan
    pandas.NA

    Examples
    --------
    >>> from pybear.preprocessing import NanStandardizer as NS
    >>> import pandas as pd
    >>>
    >>> trfm = NS(new_value=99)
    >>> X1 = np.array([[0, 1, np.nan], [np.nan, 4, 5]], dtype=np.float64)
    >>> trfm.fit_transform(X1)
    array([[ 0.,  1., 99.],
           [99.,  4.,  5.]])
    >>> trfm.set_params(new_value=pd.NA)
    NanStandardizer(new_value=<NA>)
    >>> X2 = pd.DataFrame([['a', 'b', np.nan], ['c', None, 'd']], dtype='O')
    >>> X2.columns = list('xyz')
    >>> trfm.fit_transform(X2)
       x     y     z
    0  a     b  <NA>
    1  c  <NA>     d

    """


    def __init__(
        self,
        *,
        new_value: Any = np.nan
    ):
        """Instantiate the `NanStandardizer` instance."""

        self.new_value = new_value


    def __pybear_is_fitted__(self) -> bool:
        return True


    def get_metadata_routing(self):
        """Get metadata routing is not implemented in NanStandardizer."""

        __ = type(self).__name__
        raise NotImplementedError(
            f"get_metadata_routing is not implemented in {__}"
        )


    # def get_params() - handled by GetParamsMixin


    # def set_params() - handled by SetParamsMixin


    # def fit_transform() - handled by FitTransformMixin


    def partial_fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """No-op batch-wise fit of the `NanStandardizer` instance.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features) or (n_samples,)
            The object for which to replace nan-like representations.
            Ignored.
        y : Any, default=None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """No-op one-shot fit of the NanStandardizer instance.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features) or (n_samples,)
            The object for which to replace nan-like representations.
            Ignored.
        y : Any, default=None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool=False
    ) -> XContainer:
        """Map the nan-like representations in `X` to new values.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features) or (n_samples,)
            The object for which to replace nan-like representations.
        copy : bool, default=False
            Whether to replace the values directly in the original `X`
            or in a deepcopy of `X`.

        Returns
        -------
        X_tr : XContainer of shape (n_samples, n_features), (n_samples,)
            The data with new values in the locations previously occupied
            by nan-like values.

        """

        # do not use pybear validate_data() here. there may end up being
        # circular dependency. Let nan_mask handle the validation.

        check_is_fitted(self)

        _val_X(X)

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X


        return _transform(X_tr, self.new_value)


    def score(
        self,
        X: Any,
        y: Any = None
    ) -> None:
        """No-op score method.

        Needs to be here for dask_ml wrappers.

        Parameters
        ----------
        X : Any
            The data. Ignored.
        y : Any, default=None
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        return






