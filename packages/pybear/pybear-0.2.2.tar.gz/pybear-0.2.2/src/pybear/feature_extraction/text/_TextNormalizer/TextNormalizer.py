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
    XWipContainer,
    UpperType
)

from ._validation import _validation
from ._transform import _transform

from ..__shared._transform._map_X_to_list import _map_X_to_list

from ....base import (
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin,
    check_is_fitted
)

from ....base._copy_X import copy_X



class TextNormalizer(
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetParamsMixin
):
    """Normalize all text in a dataset to upper-case, lower-case, or
    leave unchanged.

    The data can only contain strings.

    `TextNormalizer` (TN) accepts 1D list-like vectors of strings, such
    as Python lists, tuples, and sets, numpy vectors, pandas series, and
    polars series. TN also accepts 2D array-like containers such as
    (possibly ragged) nested 2D Python objects, numpy arrays, pandas
    dataframes, and polars dataframes. If you pass dataframes that have
    feature names, TN does not retain them. The returned objects are
    always constructed with Python lists, and have shape identical to
    the shape of the inputted data.

    TN is a scikit-style transformer with `partial_fit`, `fit`,
    `transform`, `fit_transform`, `get_params`, `set_params`, and `score`
    methods. An instance is always in a 'fitted' state, and checks for
    fittedness will always return True. This is because TN technically
    does not need to be fit; it already knows everything it needs to
    know to do transforms from the single parameter. The `partial_fit`,
    `fit`, and `score` methods are no-op; they exist to fulfill the API
    and to enable TN to be incorporated into workflows such as scikit
    pipelines and dask_ml wrappers.

    Parameters
    ----------
    upper : bool | None
        If True, convert all text in X to upper-case; if False, convert
        to lower-case; if None, do a no-op.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    XWipContainer:
        list[str] | list[list[str]]

    UpperType:
        bool | None

    See Also
    --------
    str.lower
    str.upper

    Examples
    --------
    >>> from pybear.feature_extraction.text import TextNormalizer as TN
    >>> trfm = TN(upper=False)
    >>> X1 = ['ThE', 'cAt', 'In', 'ThE', 'hAt']
    >>> trfm.fit_transform(X1)
    ['the', 'cat', 'in', 'the', 'hat']
    >>> trfm.set_params(upper=True)
    TextNormalizer()
    >>> X2 = [['One', 'Two', 'Three'], ['Ichi', 'Ni', 'Sa']]
    >>> trfm.fit_transform(X2)
    [['ONE', 'TWO', 'THREE'], ['ICHI', 'NI', 'SA']]

    """


    def __init__(
        self,
        *,
        upper: UpperType = True
    ) -> None:
        """Initialize the `TextNormalizer` instance."""
        self.upper = upper



    def __pybear_is_fitted__(self) -> bool:
        return True


    def get_metadata_routing(self):
        """get_metadata_routing is not implemented in `TextNormalizer`."""
        raise NotImplementedError(
            f"'get_metadata_routing' is not implemented in TextNormalizer"
        )


    # def get_params
    # handled by GetParamsMixin


    # def set_params
    # handled by SetParamsMixin


    # def fit_transform
    # handled by FitTransformMixin


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """No-op batch-wise fit.

        Parameters
        ----------
        X : XContainer
            The text data to normalize.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextNormalizer` instance.

        """


        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """ No-op one-shot fit.

        Parameters
        ----------
        X : XContainer
            The text data to normalize.
        y : Any, default = None
            The target for the data. Always ignored.

        Returns
        -------
        self : object
            The `TextNormalizer` instance.

        """


        return self.partial_fit(X, y)


    def transform(
        self,
        X:XContainer,
        copy:bool = False
    ) -> XWipContainer:
        """Normalize the text in a dataset.

        Parameters
        ----------
        X : XContainer
            The text data to normalize.
        copy : bool, default = False
            Whether to normalize the text in the original `X` object or
            a deepcopy of `X`.

        Returns
        -------
        X_tr : list[str] | list[list[str]]
            The data with normalized text.

        """

        check_is_fitted(self)

        _validation(X, self.upper)

        if copy:
            X_tr = copy_X(X)
        else:
            X_tr = X

        X_tr: XWipContainer = _map_X_to_list(X_tr)

        if all(map(isinstance, X_tr, (str for _ in X_tr))):
            return _transform(X_tr, self.upper)
        else:
            # USE RECURSION ON 1D TO DO 2D
            for _row_idx in range(len(X_tr)):
                X_tr[_row_idx] = self.transform(X_tr[_row_idx], copy=False)

            return X_tr


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """No-op score method.

        Parameters
        ----------
        X : Any
            The data. Ignored.
        y : Any, default = None
            The target for the data. Ignored.

        Returns
        -------
        None

        """


        check_is_fitted(self)

        return




