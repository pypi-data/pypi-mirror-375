# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Literal,
    Sequence
)
from typing_extensions import Self
from ._type_aliases import (
    KeepType,
    ConstantColumnsType,
    InstructionType,
    KeptColumnsType,
    RemovedColumnsType,
    ColumnMaskType,
    FeatureNamesInType
)
from ..__shared._type_aliases import XContainer

import numbers

import numpy as np

from ._validation._validation import _validation
from ._validation._keep_and_columns import _val_keep_and_columns
from ._partial_fit._find_constants import _find_constants
from ._partial_fit._merge_constants import _merge_constants
from ._shared._make_instructions import _make_instructions
from ._shared._set_attributes import _set_attributes
from ._shared._manage_keep import _manage_keep
from ._inverse_transform._inverse_transform import _inverse_transform
from ._inverse_transform._remove_intercept import _remove_intercept
from ._transform._transform import _transform

from ..__shared._validation._X import _val_X

from ...base import (
    FeatureMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin,
    check_is_fitted,
    get_feature_names_out,
    validate_data
)



class InterceptManager(
    FeatureMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin
):
    """A scikit-style transformer that identifies and manages the
    constant columns in a dataset.

    A dataset may contain columns with constant values for a variety of
    reasons, some intentional, some circumstantial. The use of a column
    of constants in a dataset may be a design consideration for some
    data analytics algorithms, such as multiple linear regression.
    Therefore, the presence of one such column may be desirable.

    The presence of multiple constant columns is generally a degenerate
    condition. In many data analytics learning algorithms, such a
    condition can cause convergence problems, inversion problems, or
    other undesirable effects. The analyst is often forced to address
    the issue to perform a meaningful analysis of the data.

    `InterceptManager` (IM) has several key characteristics that make it
    a versatile and powerful tool that can help fix this condition.

    IM...

    1) handles numerical and non-numerical data

    2) accepts nan-like values, and has flexibility in dealing with them

    3) has a partial fit method for batch-wise fitting and transforming

    4) has parameters that give flexibility to how 'constant' is defined

    5) can remove all, keep one, or append a column of constants to data

    The methodology that IM uses to identify a constant column is
    different for numerical and non-numerical data.

    In the simplest situation with non-numerical data where nan-like
    values are not involved, the computation is simply to determine the
    number of unique values in the column. If there is only one unique
    value, then the column is constant.

    The computation for numerical columns is slightly more complex.
    IM calculates the mean of the column then compares it against the
    individual values via `numpy.allclose`. allclose has 'rtol' and
    'atol' parameters that give latitude to the definition of 'equal'.
    They provide a tolerance window whereby numerical data that are not
    exactly equal are considered equal if their difference falls within
    the tolerance. IM affords some flexibility in defining 'equal'
    when identifying constants by providing direct access to the
    `numpy.allclose` 'rtol' and 'atol' parameters via its own, identically
    named, `rtol` and `atol` parameters. IM requires that `rtol` and
    `atol` be non-boolean, non-negative real numbers, in addition to any
    other restrictions enforced by `numpy.allclose`. See the numpy docs
    for clarification of the technical details.

    The `equal_nan` parameter controls how IM handles nan-like values.
    If `equal_nan` is True, exclude any nan-like values from the allclose
    comparison. This essentially assumes that the nan values are equal
    to the mean of the non-nan values within their column. nan-like
    values will not in and of themselves cause a column to be considered
    non-constant when `equal_nan` is True. If `equal_nan` is False, IM
    does not make the same assumption that the nan values are implicitly
    equal to the mean of the non-nan values, thus making the column not
    constant. This is in line with the normal numpy handling of nan-like
    values. See the Notes section below for a discussion on the handling
    of nan-like values.

    IM also has a `keep` parameter that allows the user to manage
    the constant columns that are identified. `keep` accepts several
    types of arguments. The 'Keep' discussion section has a list of all
    the options that can be passed to `keep`, what they do, and how to
    use them.

    The :meth:`partial_fit`, :meth:`fit`, and :meth:`inverse_transform`
    methods of IM accept data as numpy arrays, pandas dataframes, polars
    dataframes, and scipy sparse matrices/arrays. :meth:`transform`
    and :meth:`fit_transform` also accept these containers, but the
    type of output container for these methods can be controlled by
    the :meth:`set_output` method. The user can set the type of
    output container regardless of the type of input container. Output
    containers available via `set_output` are numpy arrays, pandas
    dataframes, and polars dataframes. When `set_output` is None, the
    output container is the same as the input, that is, numpy array,
    pandas or polars dataframe, or scipy sparse matrix/array.

    The `partial_fit` method allows for incremental fitting of data.
    This makes IM suitable for use with packages that do batch-wise
    fitting and transforming, such as dask_ml via the Incremental and
    ParallelPostFit wrappers.

    There are no safeguards in place to prevent the user from changing
    the `rtol`, `atol`, or `equal_nan` values between calls to
    `partial_fit`. These 3 parameters have strong influence over whether
    IM classifies a column as constant, and therefore is instrumental in
    dictating what IM learns during fitting. Changes to these parameters
    between partial fits can drastically change IM's understanding of
    the constant columns in the data versus what would otherwise be
    learned under constant settings. pybear recommends against this
    practice, however, it is not strictly blocked.

    When performing multiple batch-wise transformations of data, that
    is, making sequential calls to `transform`, it is critical that the
    same column indices be kept / removed at each call. This issue
    manifests when `keep` is set to 'random'; the random index to keep
    must be the same at all calls to `transform`, and cannot be
    dynamically randomized within `transform`. IM handles this by
    generating a static random column index to keep at fit time, and
    does not change this number during transform time. This number is
    dynamic with each call to `partial_fit`, and will likely change at
    each call. Fits performed after calls to `transform` will change
    the random index away from that used in the previous transforms,
    causing IM to perform entirely different transformations than those
    previously being done. IM cannot block calls to `partial_fit` after
    `transform` has been called, but pybear strongly discourages this
    practice because the output will be nonsensical. pybear recommends
    doing all partial fits consecutively, then doing all transformations
    consecutively.

    **The 'keep' Parameter**

    IM learns which columns are constant during fitting. At the time
    of transform, IM applies the instruction given to it via the `keep`
    parameter. The `keep` parameter takes several types of arguments,
    providing various ways to manage the columns of constants within a
    dataset. Below is a comprehensive list of all the arguments that can
    be passed to `keep`.

    Literal 'first':
        Retains the constant column left-most in the data (if any) and
        deletes any others. Must be lower case. Does not except if there
        are no constant columns.
    Literal 'last':
        The default setting, keeps the constant column right-most in the
        data (if any) and deletes any others. Must be lower case. Does
        not except if there are no constant columns.
    Literal 'random':
        Keeps a single randomly-selected constant column (if any) and
        deletes any others. Must be lower case. Does not except if there
        are no constant columns.
    Literal 'none':
        Removes all constant columns (if any). Must be lower case. Does
        not except if there are no constant columns.
    integer:
        An integer indicating the column index in the original data to
        keep, while removing all other columns of constants. IM will
        raise an exception if this passed index is not a column of
        constants.
    string:
        A string indicating feature name to keep if a container with
        a header is passed, while deleting all other constant columns.
        Case sensitive. IM will except if 1) a string is passed that
        is not an allowed string literal ('first', 'last', 'random',
        'none') but a valid container is not passed to `fit`, 2) a valid
        container is passed to `fit` but the given feature name is not
        valid, 3) the feature name is valid but the column is not
        constant.
    callable(X):
        a callable that returns a valid column index when the data is
        passed to it, indicating the index of the column of constants to
        keep while deleting all other columns of constants. This enables
        the analyst to use characteristics of the data being transformed
        to determine which column of constants to keep. IM passes the
        data as-is directly to the callable without any preprocessing.
        The callable needs to operate on the data object directly.
        IM will except if 1) the callable does not return an integer,
        2) the integer returned is out of the range of columns in the
        passed data, 3) the integer that is returned does not correspond
        to a constant column.
        IM does not retain state information about what indices have
        been returned from the callable during transform. IM cannot catch
        if the callable is returning different indices for different
        batches of data within a sequence of calls to `transform`. When
        doing multiple batch-wise transforms, it is up to the user to
        ensure that the callable returns the same index for each call to
        `transform`. If the callable returns a different index for any
        of the batches of data passed in a sequence of transforms then
        the results will be nonsensical.
    dictionary[str, Any]:
        dictionary of {feature name:str, constant value:Any}. A column
        of constants is appended to the right end of the data, with the
        constant being the value in the dictionary. The `keep` dictionary
        requires a single key:value pair. The key must be a string
        indicating feature name. This applies to any format of data that
        is transformed. If the data is a pandas or polars dataframe,
        then this string will become the feature name of the new constant
        feature. If the fitted data is a numpy array or scipy sparse,
        then this column name is ignored. The dictionary value is the
        constant value for the new feature. This value has only two
        restrictions: it cannot be a non-string sequence (e.g. list,
        tuple, etc.) and it cannot be a callable. Essentially, the
        constant value is restricted to being integer, float, string, or
        boolean.

        When appending a constant value to a pandas dataframe, if the
        constant is numeric it is appended as numpy.float64; if it is
        not numeric it is appended as Python object. When appending a
        constant value to a polars dataframe, if the constant is numeric
        it is appended as polars.Float64; if it is not numeric it is
        appended as polars.Object. Otherwise, if the constant is being
        appended to a numpy array or scipy sparse it will be forced to
        the dtype of the transformed data (with some caveats.)

        When transforming a pandas dataframe or polars dataframe and
        the new feature name is already a feature in the data, there
        are two possible outcomes. 1) If the original feature is not
        constant, the new constant values will overwrite in the old
        column (generally an undesirable outcome.) 2) If the original
        feature is constant, the original column will be removed and a
        new column with the same name will be appended with the new
        constant values. IM will warn about this condition but not
        terminate the program. It is up to the user to manage the
        feature names in this situation.

        The :attr:`column_mask_` attribute is not adjusted for the new
        feature appended by the `keep` dictionary (see the discussion on
        `column_mask_`.) But the `keep` dictionary does make adjustment
        to :meth:`get_feature_names_out`. Because `get_feature_names_out`
        reflects the state of transformed data, and the `keep` dictionary
        modifies the data at transform time, `get_feature_names_out`
        reflects this modification. `column_mask_` is intended to be
        applied to pre-transform data, therefore that dimensionality is
        preserved.

    To access the `keep` literals ('first', 'last', 'random', 'none'),
    these MUST be passed as lower-case. If a pandas or polars dataframe
    is fitted and there is a conflict between a literal that has been
    passed to `keep` and a feature name, IM will raise because it is not
    clear to IM whether you want to indicate the literal or the feature
    name. To afford a little more flexibility with feature names, IM
    does not normalize case for this parameter. This means that if
    `keep` is passed as 'first',  feature names such as 'First', 'FIRST',
    'FiRsT', etc. will not raise, only 'first' will.

    The only value that removes all constant columns is 'none'. All other
    valid arguments for `keep` leave one column of constants behind and
    all other constant columns are removed from the dataset. If IM does
    not find any constant columns, 'first', 'last', 'random', and 'none'
    will not raise an exception. It is like telling IM: "I don't know if
    there are any constant columns, but if you find some, then apply
    this rule." However, if using an integer, feature name, or callable,
    IM will raise an exception if it does not find a constant column at
    that index. It is like telling IM: "I know that this column is
    constant, and you need to keep it and remove any others." If IM
    finds that it is not constant, it will raise an exception because
    you lied to it.

    Parameters
    ----------
    keep : KeepType, default='last'
        The strategy for handling the constant columns. See 'The keep
        Parameter' section for a lengthy explanation of the 'keep'
        parameter.
    equal_nan : bool, default=True
        If `equal_nan` is True, exclude nan-likes from computations that
        discover constant columns. This essentially assumes that the nan
        value would otherwise be equal to the mean of the non-nan values
        in the same column. If `equal_nan` is False and any value in a
        column is nan, do not assume that the nan value is equal to the
        mean of the non-nan values in the same column, thus making the
        column non-constant. This is in line with the normal numpy
        handling of nan values.
    rtol : numbers.Real, default=1e-5
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See `numpy.allclose`.
    atol : numbers.Real, default=1e-8
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See `numpy.allclose`.

    Attributes
    ----------
    n_features_in_ : int
        Number of features in the fitted data before transform.
    feature_names_in_ : numpy.ndarray[object]
        The feature names seen during fitting. Only accessible if `X`
        is passed to :meth:`partial_fit` or :meth:`fit` as a pandas or
        polars dataframe that has a header.
    constant_columns_
    kept_columns_
    removed_columns_
    column_mask_

    Notes
    -----
    Concerning the handling of nan-like representations. While IM
    accepts data in the form of numpy arrays, pandas dataframes, polars
    dataframes, and scipy sparse matrices/arrays, internally copies are
    extracted from the source data as numpy arrays (see below for more
    detail about how scipy sparse is handled.) After the conversion
    to numpy array and prior to calculating the mean and applying
    `numpy.allclose`, IM identifies any nan-like representations in the
    numpy array and standardizes all of them to numpy.nan. The user
    needs to be wary that whatever is used to indicate 'not-a-number'
    in the original data must first survive the conversion to numpy
    array, then be recognizable by IM as nan-like, so that IM can
    standardize it to numpy.nan. nan-like representations that are
    recognized by IM include, at least, numpy.nan, pandas.NA, None (of
    type None, not string 'None'), and string representations of 'nan'
    (not case sensitive).

    Concerning the handling of infinity. IM has no special handling for
    the various infinity-types, e.g, numpy.inf, -numpy.inf, float('inf'),
    float('-inf'), etc. This is a design decision to not force infinity
    values to numpy.nan. IM falls back to the native handling of these
    values for Python and numpy. Specifically, numpy.inf==numpy.inf and
    float('inf')==float('inf').

    Concerning the handling of scipy sparse arrays. When searching for
    constant columns, chunks of columns are converted to dense numpy
    arrays one chunk at a time. Each chunk is sliced from the data in
    sparse form and is converted to numpy ndarray via the 'toarray'
    method. This a compromise that causes some memory expansion but
    allows for efficient handling of constant column calculations that
    would otherwise involve implicit non-dense values.

    **Type Aliases**

    XContainer:
        numpy.ndarray | pandas.DataFrame | polars.DataFrame
        | ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._lil.lil_matrix | ss._dok.dok_matrix
        | ss._bsr.bsr_matrix | ss._csr.csr_array | ss._csc.csc_array
        | ss._coo.coo_array | ss._dia.dia_array |ss._lil.lil_array
        | ss._dok.dok_array | ss._bsr.bsr_array

    KeepType:
        Literal['first', 'last', 'random', 'none'] | dict[str, Any]
        | int | str | Callable[[XContainer], int]

    ConstantColumnsType:
        dict[int, Any]

    KeptColumnsType:
        dict[int, Any]

    RemovedColumnsType:
        dict[int, Any]

    ColumnMaskType:
        numpy.ndarray[bool]

    NFeaturesInType:
        int

    FeatureNamesInType:
        numpy.ndarray[str]

    See Also
    --------
    numpy.ndarray
    pandas.DataFrame
    polars.DataFrame
    scipy.sparse
    numpy.allclose
    numpy.isclose
    numpy.unique

    Examples
    --------
    >>> from pybear.preprocessing import InterceptManager as IM
    >>> import numpy as np
    >>> np.random.seed(99)
    >>> X = np.random.randint(0, 10, (5, 5))
    >>> X[:, 1] = 0
    >>> X[:, 2] = 1
    >>> print(X)
    [[1 0 1 8 9]
     [8 0 1 5 4]
     [1 0 1 7 1]
     [1 0 1 4 7]
     [2 0 1 8 4]]
    >>> trf = IM(keep='first', equal_nan=True)
    >>> trf.fit(X)
    InterceptManager(keep='first')
    >>> out = trf.transform(X)
    >>> print(out)
    [[1 0 8 9]
     [8 0 5 4]
     [1 0 7 1]
     [1 0 4 7]
     [2 0 8 4]]
    >>> print(trf.n_features_in_)
    5
    >>> print(trf.constant_columns_)
    {1: np.float64(0.0), 2: np.float64(1.0)}
    >>> print(trf.removed_columns_)
    {2: np.float64(1.0)}
    >>> print(trf.column_mask_)
    [ True  True False  True  True]

    """


    def __init__(
        self,
        *,
        keep:KeepType = 'last',
        equal_nan:bool = True,
        rtol:numbers.Real = 1e-5,
        atol:numbers.Real = 1e-8
    ) -> None:
        """Initialize the InterceptManager instance."""

        self.keep = keep
        self.equal_nan = equal_nan
        self.rtol = rtol
        self.atol = atol


    # properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @property
    def constant_columns_(self) -> ConstantColumnsType:
        """Get the `constant_columns_` attribute.

        A dictionary whose keys are the indices of the constant columns
        found during fit, indexed by their column location in the
        original data. The dictionary values are the constant values in
        those columns. For example, if a dataset has two constant columns,
        the first in the third index and the constant value is 1, and
        the other is in the tenth index and the constant value is 0,
        then `constant_columns_` will be {3:1, 10:0}. If there are no
        constant columns, then `constant_columns_` is an empty dictionary.

        Returns
        -------
        constant_columns_ : dict[int, Any]
            A dictionary whose keys are the indices of the constant
            columns found during fit, indexed by their column location
            in the original data.

        """

        check_is_fitted(self)

        return self._constant_columns


    @property
    def kept_columns_(self) -> KeptColumnsType:
        """Get the `kept_columns_` attribute.

        A subset of the :attr:`constant_columns_` dictionary, constructed
        with the same format. This holds the subset of constant columns
        that are retained in the data. If a constant column is kept, then
        this contains one key:value pair from `constant_columns_`. If
        there are no constant columns or no columns are kept, then this
        is an empty dictionary. When `keep` is a dictionary, all the
        original constant columns are removed and a new constant column
        is appended to the data. That column is NOT included in
        `kept_columns_`.

        Returns
        -------
        kept_columns_ : dict[int, Any]
            A subset of the `constant_columns_` dictionary, constructed
            with the same format.

        """

        check_is_fitted(self)

        return self._kept_columns


    @property
    def removed_columns_(self) -> RemovedColumnsType:
        """Get the `removed_columns_` attribute.

        A subset of the :attr:`constant_columns_` dictionary, constructed
        with the same format. This holds the subset of constant columns
        that are removed from the data. If there are no constant columns
        or no constant columns are removed, then this is an empty
        dictionary.

        Returns
        -------
        removed_columns_ : dict[int, Any]
            A subset of the `constant_columns_` dictionary, constructed
            with the same format.

        """

        check_is_fitted(self)

        return self._removed_columns


    @property
    def column_mask_(self) -> ColumnMaskType:
        """Get the `column_mask_` attribute.

        Indicates which columns of the fitted data are kept (True) and
        which are removed (False) during transform. When `keep` is a
        dictionary, all original constant columns are removed and a new
        column of constants is appended to the data. This new column is
        NOT appended to `column_mask_`. This mask is intended to be
        applied to data of the same dimension as that seen during fit,
        and the new column of constants is a feature added after
        transform.

        Returns
        -------
        column_mask_ : numpy.ndarray[bool] of shape (n_features,)
            Indicates which columns of the fitted data are kept (True)
            and which are removed (False) during transform.

        """

        check_is_fitted(self)

        return self._column_mask
    # END properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def _reset(self) -> Self:
        """Reset the internal data-dependent state of `InterceptManager`.

        __init__ parameters are not changed.

        Returns
        -------
        self : object
            The `InterceptManager` instance.

        """

        if hasattr(self, '_constant_columns'):
            delattr(self, '_constant_columns')

        if hasattr(self, '_kept_columns'):
            delattr(self, '_kept_columns')

        if hasattr(self, '_removed_columns'):
            delattr(self, '_removed_columns')

        if hasattr(self, '_column_mask'):
            delattr(self, '_column_mask')

        if hasattr(self, 'n_features_in_'):
            delattr(self, 'n_features_in_')

        if hasattr(self, 'feature_names_in_'):
            delattr(self, 'feature_names_in_')

        return self


    def get_feature_names_out(
        self,
        input_features:Sequence[str] | None = None
    ) -> FeatureNamesInType:
        """Get the feature names for the output of `transform`.

        When `keep` is a dictionary, the appended column of constants is
        included in the outputted feature name vector.

        Parameters
        ----------
        input_features : Sequence[str] | None, default=None
            Externally provided feature names for the fitted data, not
            the transformed data.

            If `input_features` is None:
                if `feature_names_in_` is defined, then `feature_names_in_`
                is used as the input features.

                if `feature_names_in_` is not defined, then the following
                input feature names are generated:
                ["x0", "x1", ..., "x(`n_features_in_` - 1)"].

            If `input_features` is not None:
                if `feature_names_in_` is not defined, then `input_features`
                is used as the input features.

                if `feature_names_in_` is defined, then `input_features`
                must exactly match the features in `feature_names_in_`.

        Returns
        -------
        feature_names_out : FeatureNamesInType
            The feature names of the transformed data.

        """

        # get_feature_names_out() would otherwise be provided by
        # pybear.base.FeatureMixin, but since this transformer deletes
        # and/or adds columns, must build a one-off.

        # when there is a {'Intercept': 1} in :param: keep, need to make
        # sure that that column is accounted for here, and the dropped
        # columns are also accounted for.

        check_is_fitted(self)

        feature_names_out = get_feature_names_out(
            input_features,
            getattr(self, 'feature_names_in_', None),
            self.n_features_in_
        )

        feature_names_out = feature_names_out[self._column_mask]

        if isinstance(self.keep, dict):
            feature_names_out = np.hstack((
                feature_names_out,
                list(self.keep.keys())[0]
            )).astype(object)

        return feature_names_out


    def get_metadata_routing(self):
        """Get metadata routing is not implemented."""

        __ = type(self).__name__
        raise NotImplementedError(
            f"get_metadata_routing is not implemented in {__}"
        )


    # def get_params - inherited from GetParamsMixin


    def partial_fit(
        self,
        X: XContainer,
        y: Any=None
    ) -> Self:
        """Perform incremental fitting on one or more batches of data.

        Determine the constant columns in the data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. Data to find constant columns in.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `InterceptManager` instance.

        """


        X = validate_data(
            X,
            copy_X=False,
            cast_to_ndarray=False,
            accept_sparse=("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(2,),
            ensure_2d=False,
            order='F',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )


        # reset – Whether to reset the n_features_in_ attribute. If False,
        # the input will be checked for consistency with data provided
        # when reset was last True.
        # It is recommended to call reset=True in fit and in the first
        # call to partial_fit. All other methods that validate X should
        # set reset=False.

        # do not make an assignment! let the function handle it.
        self._check_n_features(
            X,
            reset=not hasattr(self, "_constant_columns")
        )

        # do not make an assignment! let the function handle it.
        self._check_feature_names(
            X,
            reset=not hasattr(self, "_constant_columns")
        )

        # this must be after _check_feature_names()
        _validation(
            X,
            getattr(self, 'feature_names_in_', None),
            self.keep,
            self.equal_nan,
            self.rtol,
            self.atol
        )

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


        # ss sparse that cant be sliced
        # avoid copies of X, do not mutate X. if X is coo, dia, bsr, it
        # cannot be sliced. must convert to another ss. so just convert
        # all of them to csc for faster column slicing. need to change
        # it back later.
        if hasattr(X, 'toarray'):
            _og_dtype = type(X)
            X = X.tocsc()


        # if IM has already been fitted and _constant_columns is empty
        # (meaning there are no constant columns) dont even bother to
        # scan more data, cant possibly have constant columns
        if getattr(self, '_constant_columns', None) == {}:
            self._constant_columns = {}
        else:
            # dictionary of column indices and respective constant values
            _current_constant_columns: ConstantColumnsType = \
                _find_constants(
                    X,
                    self.equal_nan,
                    self.rtol,
                    self.atol
                )

            # Use _merge_constants() to combine constants found in the
            # current partial fit with those found in previous partial
            # fits.
            self._constant_columns: ConstantColumnsType = \
                _merge_constants(
                    getattr(self, '_constant_columns', None),
                    _current_constant_columns,
                    self.rtol,
                    self.atol
                )

            del _current_constant_columns

        # Create an instance attribute that specifies the random column
        # index to keep when 'keep' is 'random'. This value must be
        # static on calls to :meth: transform (meaning sequential calls
        # to transform get the same random index every time.) This value
        # is generated and retained even if :param: 'keep' != 'random',
        # in case :param: 'keep' should be set to 'random' at any point
        # via set_params().
        if len(self._constant_columns):
            self._rand_idx = int(np.random.choice(list(self._constant_columns)))
        else:
            self._rand_idx = None


        # all scipy sparse were converted to csc near the top of this
        # method. change it back to original state. do not mutate X!
        # change this back before _manage_keep, a keep callable might
        # depend on characteristics of the original X's container.
        if hasattr(X, 'toarray'):
            X = _og_dtype(X)
            del _og_dtype


        _keep: Literal['none'] | dict[str, Any] | int = _manage_keep(
            self.keep,
            X,
            self._constant_columns,
            self.n_features_in_,
            getattr(self, 'feature_names_in_', None),
            self._rand_idx
        )

        self._instructions: InstructionType = _make_instructions(
            _keep,
            self._constant_columns,
            self.n_features_in_
        )

        out = _set_attributes(
            self._constant_columns,
            self._instructions,
            self.n_features_in_
        )

        self._kept_columns: KeptColumnsType = out[0]
        self._removed_columns: RemovedColumnsType = out[1]
        self._column_mask: ColumnMaskType = out[2]
        del out


        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """Perform a single fitting on a dataset.

        Determine the constant columns in the data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data to find constant columns in.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `InterceptManager` instance.

        """

        self._reset()

        return self.partial_fit(X, y=y)


    # def fit_transform(self, X, y=None, **fit_params):
    # inherited from FitTransformMixin

    # def set_params(self)
    # inherited from SetParamsMixin

    # def set_output(self)
    # inherited from SetOutputMixin

    def inverse_transform(
        self,
        X:XContainer,
        copy:bool | None = None
    ) -> XContainer:
        """Revert transformed data back to its original state.

        This operation cannot restore any nan-like values that may have
        been in the original untransformed data. :meth:`set_output` does
        not control the output container here, the output container is
        always the same as passed.

        Very little validation is possible to ensure that the passed
        data is valid for the current state of IM. It is only possible
        to ensure that the number of columns in the passed data match
        the number of columns that are expected to be outputted
        by :meth:`transform` for the current state of IM. It is up to
        the user to ensure the state of IM aligns with the state of the
        data that is to undergo inverse transform. Otherwise, the output
        will be nonsensical.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_transformed_features)
            A transformed data set.
        copy : bool | None, default=None
            Whether to make a deepcopy of `X` before the inverse
            transform.

        Returns
        -------
        X_inv : XContainer of shape (n_samples, n_features)
            Transformed data reverted to its original untransformed
            state.

        """

        check_is_fitted(self)

        if not isinstance(copy, (bool, type(None))):
            raise TypeError(f"'copy' must be boolean or None")

        X_inv = validate_data(
            X,
            copy_X=copy or False,
            cast_to_ndarray=False,
            accept_sparse=("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(2,),
            ensure_2d=False,
            order='F',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        _val_X(X_inv)

        _val_keep_and_columns(self.keep, None, 'spoof_X')

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # ss sparse that cant be sliced
        # if X_inv is coo, dia, bsr, it cannot be sliced. must convert
        # to another ss. so just convert all of them to csc for faster
        # column slicing. need to change it back later.
        if hasattr(X_inv, 'toarray'):
            _og_format = type(X_inv)
            X_inv = X_inv.tocsc()

        # if _keep is a dict ** * ** * ** * ** * ** * ** * ** * ** * **
        # a column of constants was stacked to the right side of the data.
        # check that 'keep' is valid (may have changed via set_params()),
        # the passed data matches against 'keep', and remove the column
        if isinstance(self.keep, dict):
            X_inv = _remove_intercept(X_inv, self.keep)
        # END _keep is a dict ** * ** * ** * ** * ** * ** * ** * ** * **

        # the number of columns in X_inv must be equal to the number of
        # features remaining in _column_mask
        if X_inv.shape[1] != np.sum(self._column_mask):
            raise ValueError(
                f"the number of columns in X_inv must be equal to the "
                f"number of columns kept in the fitted data after removing "
                f"constants. \nexpected {np.sum(self._column_mask)}, got "
                f"{X_inv.shape[1]}."
            )

        X_inv = _inverse_transform(
            X_inv,
            self._removed_columns,
            getattr(self, 'feature_names_in_', None)
        )

        # all scipy sparse were converted to csc near the top of this
        # method. change it back to original state.
        if hasattr(X_inv, 'toarray'):
            X_inv = _og_format(X_inv)
            del _og_format

        if isinstance(X_inv, np.ndarray):
            X_inv = np.ascontiguousarray(X_inv)


        return X_inv


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """Dummy method to spoof dask Incremental and ParallelPostFit
        wrappers.

        Verified must be here for dask wrappers.

        Parameters
        ----------
        X:Any
            The data. Ignored.
        y:Any, default = None
            THe target for the data. Ignored.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        return


    @SetOutputMixin._set_output_for_transform
    def transform(
        self,
        X:XContainer,
        copy:bool | None = None
    ) -> XContainer:
        """Manage the constant columns in `X`.

        Apply the removal criteria given by `keep` to the constant
        columns found during fit.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data to be transformed.
        copy : bool | None, default=None
            Whether to make a deepcopy of `X` before the transform.

        Returns
        -------
        X_tr : XContainer of shape (n_samples, n_transformed_features)
            The transformed data.

        """


        check_is_fitted(self)

        if not isinstance(copy, (bool, type(None))):
            raise TypeError(f"'copy' must be boolean or None")

        X_tr = validate_data(
            X,
            copy_X=copy or False,
            cast_to_ndarray=False,
            accept_sparse=("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
            dtype='any',
            require_all_finite=False,
            cast_inf_to_nan=False,
            standardize_nan=False,
            allowed_dimensionality=(2,),
            ensure_2d=False,
            order='F',
            ensure_min_features=1,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        _validation(
            X_tr,
            getattr(self, 'feature_names_in_', None),
            self.keep,
            self.equal_nan,
            self.rtol,
            self.atol
        )

        # do not make an assignment!
        self._check_n_features(X_tr, reset=False)

        # do not make an assignment!
        self._check_feature_names(X_tr, reset=False)

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


        # everything below needs to be redone every transform in case
        # 'keep' was changed via set params after fit

        # validation should not have caused X_tr to be different than X
        # when X is scipy sparse. but just to be safe, pass the original
        # X to _manage_keep instead of X_tr.
        _keep = _manage_keep(
            self.keep,
            X,
            self._constant_columns,
            self.n_features_in_,
            self.feature_names_in_ if \
                hasattr(self, 'feature_names_in_') else None,
            self._rand_idx
        )

        self._instructions: InstructionType = _make_instructions(
            _keep,
            self._constant_columns,
            self.n_features_in_
        )

        out = _set_attributes(
            self._constant_columns,
            self._instructions,
            self.n_features_in_
        )

        self._kept_columns: KeptColumnsType = out[0]
        self._removed_columns: RemovedColumnsType = out[1]
        self._column_mask: ColumnMaskType = out[2]
        del out

        # ss sparse that cant be sliced
        # if X is coo, dia, bsr, it cannot be sliced. must convert to
        # another ss. so just convert all of them to csc for faster
        # column slicing. need to change it back later.
        if hasattr(X_tr, 'toarray'):
            _og_format = type(X_tr)
            X_tr = X_tr.tocsc()

        X_tr = _transform(X_tr, self._instructions)

        # all scipy sparse were converted to csc right before the
        # _transform function. change it back to original state.
        if hasattr(X_tr, 'toarray'):
            X_tr = _og_format(X_tr)
            del _og_format

        if isinstance(X_tr, np.ndarray):
            X_tr = np.ascontiguousarray(X_tr)


        return X_tr





