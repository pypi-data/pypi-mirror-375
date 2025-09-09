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
import numpy.typing as npt
from ._type_aliases import (
    DuplicatesType,
    RemovedColumnsType,
    ColumnMaskType,
    FeatureNamesInType
)
from ..__shared._type_aliases import XContainer

import numbers

import numpy as np

from ._validation._validation import _validation
from ._partial_fit._find_duplicates import _find_duplicates
from ._partial_fit._merge_dupls import _merge_dupls
from ._partial_fit._lock_in_random_idxs import _lock_in_random_idxs
from ._partial_fit._identify_idxs_to_delete import _identify_idxs_to_delete
from ._inverse_transform._inverse_transform import _inverse_transform
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



class ColumnDeduplicator(
    FeatureMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin
):
    """`ColumnDeduplicator` (CDT) is a scikit-style transformer that
    removes duplicate columns from data, leaving behind one column out
    of a set of duplicate columns.

    Duplicate columns are a point of concern for analysts. In many data
    analytics learning algorithms, such a condition can cause convergence
    problems, inversion problems, or other undesirable effects. The
    analyst is often forced to address this issue to perform a meaningful
    analysis of the data.

    Columns with identical values within the same dataset may occur
    coincidentally in a sampling of data, during one-hot encoding of
    categorical data, or during polynomial feature expansion.

    CDT is a tool that can help fix this problem. CDT identifies
    duplicate columns and selectively keeps one from a group of
    duplicates based on the configuration set by the user.

    CDT affords parameters that give some flexibility to the definition
    of 'equal' for the sake of identifying duplicates. Namely,
    the `rtol`, `atol`, and `equal_nan` parameters.

    The `rtol` and `atol` parameters provide a tolerance window whereby
    numerical data that are not exactly equal are considered equal if
    their difference falls within the tolerance. See the numpy docs for
    clarification of the technical details. CDT requires that `rtol` and
    `atol` be non-boolean, non-negative real numbers, in addition to any
    other restrictions enforced by `numpy.allclose`.

    The `equal_nan` parameter controls how CDT handles nan-like
    representations during comparisons. If `equal_nan` is True, exclude
    from comparison any rows where one or both of the values is/are nan.
    If one value is nan, this essentially assumes that the nan value
    would otherwise be the same as its non-nan counterpart. When both
    are nan, this considers the nans as equal (contrary to the default
    numpy handling of nan, where numpy.nan does not equal numpy.nan) and
    will not in and of itself cause a pair of columns to be marked as
    unequal. If `equal_nan` is False and either one or both of the
    values in the compared pair of values is/are nan, consider the pair
    to be not equivalent, thus making the column pair not equal. This is
    in line with the normal numpy handling of nan values. See the Notes
    section below for a discussion on the handling of nan-like values.

    CDT has parameters that allow the user to control which column is
    retained out of a set of duplicates: `keep`, `do_not_drop`, and
    `conflict`.

    The `keep` parameter sets the strategy for keeping a single
    representative from a set of identical columns. It accepts one of
    three values: 'first', 'last', or 'random'. The default setting is
    'first'. 'first' retains the column left-most in the data; 'last'
    keeps the column right-most in the data; 'random' keeps a single
    randomly-selected column from the set of duplicates. All other
    columns in the set of duplicates are removed from the dataset.

    The `do_not_drop` parameter allows the user to indicate columns not
    to be removed from the data. This is to be given as a list-like of
    integers or strings. If fitting is done with a data container that
    has a header (such as pandas or polars dataframes), a list of
    feature names may be provided. The values within must exactly match
    the features as named in the dataframe header (case-sensitive.)
    Otherwise, a list of column indices must be provided. The
    `do_not_drop` instructions could conflict with the `keep`
    instructions. If a conflict arises, such as two columns specified
    in `do_not_drop` are duplicates of each other, the behavior is
    managed by `conflict`.

    `conflict` is ignored when `do_not_drop` is not passed. Otherwise,
    `conflict` accepts two possible values: 'raise' or 'ignore'. This
    parameter instructs CDT how to deal with conflict between `keep` and
    `do_not_drop`. A conflict arises when the instruction in `keep`
    ('first', 'last', 'random') is applied and a column in `do_not_drop`
    is found to be a member of the columns to be removed. In this case,
    an exception is raised when `conflict` is 'raise'. But when
    `conflict` is 'ignore', there are 2 possible scenarios:

        1) when only one column in `do_not_drop` is among the columns
        to be removed, the `keep` instruction is overruled and the
        do-not-drop column is kept.

        2) when multiple columns in `do_not_drop` are among the columns
        to be removed, the `keep` instruction ('first', 'last', 'random')
        is applied to that subset of do-not-drop columns --- this may
        not give the same result as applying the `keep` instruction to
        the entire set of duplicate columns. This also causes at least
        one member of the columns not to be dropped to be removed.

    The :meth:`partial_fit`, :meth:`fit`, and :meth:`inverse_transform`
    methods of CDT accept data as numpy arrays, pandas dataframes, polars
    dataframes, and scipy sparse matrices/arrays. `inverse_transform`
    always returns output in the same type of container as passed to
    it. The :meth:`transform` and :meth:`fit_transform` methods can take
    all the containers listed above but can return output in a variety
    of containers. CDT has a :meth:`set_output` method, whereby the user
    can set the type of output container for these two methods regardless
    of the type of container the data is in when passed. `set_output`
    can return transformed outputs as numpy arrays, pandas dataframes,
    or polars dataframes. When `set_output` is None, the output container
    is the same as the input, that is, numpy array, pandas or polars
    dataframe, or scipy sparse matrix/array.

    The `partial_fit` method allows for incremental fitting of data.
    This makes CDT suitable for use with packages that do batch-wise
    fitting and transforming, such as dask_ml via the Incremental and
    ParallelPostFit wrappers.

    There are no safeguards in place to prevent the user from changing
    the `rtol`, `atol`, or `equal_nan` parameters between calls to
    `partial_fit`. These 3 parameters have strong influence over whether
    CDT classifies two columns as equal, and therefore are instrumental
    in dictating what CDT learns during fitting. Changes to these
    parameters between partial fits can drastically change CDT's
    understanding of the duplicate columns in the data versus what would
    otherwise be learned under constant settings. pybear recommends
    against this practice, however, it is not strictly blocked.

    When performing multiple batch-wise transformations of data, that
    is, making sequential calls to `transform`, it is critical that the
    same column indices be kept / removed at each call. This issue
    manifests when `keep` is set to 'random'; the random indices to
    keep must be the same at all calls to `transform`, and cannot be
    dynamically randomized within `transform`. CDT handles this by
    generating a static list of random indices to keep at fit time,
    and does not mutate this list during transform time. This list is
    dynamic with each call to `partial_fit`, and will likely change at
    each call. Fits performed after calls to `transform` will change
    the random indices away from those used in the previous transforms,
    causing CDT to perform entirely different transformations than those
    previously being done. CDT cannot block calls to `partial_fit` after
    `transform` has been called, but pybear strongly discourages this
    practice because the output will be nonsensical. pybear recommends
    doing all partial fits consecutively, then doing all transformations
    consecutively.

    Parameters
    ----------
    keep : Literal['first', 'last', 'random'], default='first'
        The strategy for keeping a single representative from a set of
        identical columns. 'first' retains the column left-most in the
        data; 'last' keeps the column right-most in the data; 'random'
        keeps a single randomly-selected column of the set of duplicates.
    do_not_drop : Sequence[int] | Sequence[str] | None, default=None
        A list of columns not to be dropped. If fitting is done with a
        container that has a header, a list of feature names may be
        provided. Otherwise, a list of column indices must be given. If
        a conflict arises, such as when two columns specified in
        `do_not_drop` are duplicates of each other, the behavior is
        managed by `conflict`.
    conflict : Literal['raise', 'ignore'], default = 'raise'
        Ignored when `do_not_drop` is not passed. Instructs CDT how
        to deal with a conflict between the instructions in `keep`
        and `do_not_drop`. A conflict arises when the instruction in
        `keep` ('first', 'last', 'random') is applied and a column in
        `do_not_drop` is found to be a member of the columns to be
        removed. In this case, when `conflict` is 'raise', an exception
        is raised. When `conflict` is 'ignore', there are 2 possible
        scenarios:

        1) when only one column in `do_not_drop` is among the columns
        to be removed, the `keep` instruction is overruled and the
        do-not-drop column is kept.

        2) when multiple columns in `do_not_drop` are among the columns
        to be removed, the `keep` instruction ('first', 'last', 'random')
        is applied to the set of do-not-delete columns that are amongst
        the duplicates --- this may not give the same result as applying
        the `keep` instruction to the entire set of duplicate columns.
        This also causes at least one member of the columns not to be
        dropped to be removed.
    equal_nan : bool, default=False
        When comparing pairs of columns row by row:

        If `equal_nan` is True, exclude from comparison any rows where
        one or both of the values is/are nan. If one value is nan, this
        essentially assumes that the nan value would otherwise be the
        same as its non-nan counterpart. When both are nan, this
        considers the nans as equal (contrary to the default numpy
        handling of nan, where numpy.nan does not equal numpy.nan) and
        will not in and of itself cause a pair of columns to be marked
        as unequal. If `equal_nan` is False and either one or both of
        the values in the compared pair of values is/are nan, consider
        the pair to be not equivalent, thus making the column pair not
        equal. This is in line with the normal numpy handling of nan
        values.
    rtol : numbers.Real, default=1e-5
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See `numpy.allclose`.
    atol : numbers.Real, default=1e-8
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See `numpy.allclose`.
    n_jobs : int | None, default=None
        The number of joblib Parallel jobs to use when comparing columns.
        The default is to use processes, but can be overridden externally
        using a joblib `parallel_config` context manager. The default
        value for `n_jobs` is None, which uses the joblib default
        setting. To get maximum speed benefit, pybear recommends setting
        this to -1, which means use all processors.
    job_size : int, default=50
        The number of columns to send to a joblib job. Must be an integer
        greater than or equal to 2. This allows the user to optimize CPU
        utilization for their particular circumstance. Long, thin datasets
        should use fewer columns, and wide, flat datasets should use more
        columns. Bear in mind that the columns sent to joblib jobs are
        deep copies of the original data, and larger job sizes increase
        RAM usage. Also note that joblib is only engaged when the number
        of columns in the data is at least 2*job_size. For example, if
        job_size is 10, data with 20 or more columns will be processed
        with joblib, data with 19 or fewer columns will be processed
        linearly.

    Attributes
    ----------
    n_features_in_ : int
        The number of features in the fitted data before deduplication.

    feature_names_in_ : numpy.ndarray[object]
        The names of the features as seen during fitting. Only accessible
        if `X` is passed to :meth:`partial_fit` or :meth:`fit` in a
        container that has a header.

    duplicates_
    removed_columns_
    column_mask_

    Notes
    -----
    Concerning the handling of nan-like representations. While CDT
    accepts data in the form of numpy arrays, pandas dataframes, polars
    dataframes, and scipy sparse matrices/arrays, at comparison time the
    two columns of data to be compared are extracted from the passed data
    and converted to numpy arrays. After the conversion and prior to the
    comparison, CDT identifies any nan-like representations in both
    numpy arrays and standardizes all of them to numpy.nan. The user
    needs to be wary that whatever is used to indicate 'not-a-number' in
    the original data must first survive the conversion to numpy array,
    then be recognizable by CDT as nan-like, so that CDT can standardize
    it to numpy.nan. nan-like representations that are recognized by CDT
    include, at least, numpy.nan, pandas.NA, None (of type None, not
    string 'None'), and string representations of 'nan' (not case
    sensitive).

    Concerning the handling of infinity. CDT has no special handling for
    the various infinity-types, e.g, numpy.inf, -numpy.inf, float('inf'),
    float('-inf'), etc. This is a design decision to not force infinity
    values to numpy.nan. SPF falls back to the native handling of these
    values for Python and numpy. Specifically, numpy.inf==numpy.inf and
    float('inf')==float('inf').


    **Type Aliases**

    XContainer:
        numpy.ndarray | pandas.DataFrame | polars.DataFrame
        | ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._lil.lil_matrix | ss._dok.dok_matrix
        | ss._bsr.bsr_matrix | ss._csr.csr_array | ss._csc.csc_array
        | ss._coo.coo_array | ss._dia.dia_array | ss._lil.lil_array
        | ss._dok.dok_array | ss._bsr.bsr_array

    KeepType:
        Literal['first', 'last', 'random']

    DoNotDropType:
        Sequence[int] | Sequence[str] | None

    ConflictType:
        Literal['raise', 'ignore']

    DuplicatesType:
        list[list[int]]

    RemovedColumnsType:
        dict[int, int]

    ColumnMaskType:
        numpy.ndarray[bool]

    FeatureNamesInType:
        numpy.ndarray[str]

    See Also
    --------
    numpy.ndarray
    pandas.DataFrame
    polars.DataFrame
    scipy.sparse
    numpy.allclose
    numpy.array_equal

    Examples
    --------
    >>> from pybear.preprocessing import ColumnDeduplicator as CDT
    >>> import numpy as np
    >>> np.random.seed(99)
    >>> X = np.random.randint(0, 10, (5, 5))
    >>> X[:, 2] = X[:, 0]
    >>> X[:, 4] = X[:, 1]
    >>> print(X)
    [[1 3 1 8 3]
     [8 2 8 5 2]
     [1 7 1 7 7]
     [1 0 1 4 0]
     [2 0 2 8 0]]
    >>> trf = CDT(keep='first', do_not_drop=None)
    >>> trf.fit(X)
    ColumnDeduplicator()
    >>> out = trf.transform(X)
    >>> print(out)
    [[1 3 8]
     [8 2 5]
     [1 7 7]
     [1 0 4]
     [2 0 8]]
    >>> print(trf.n_features_in_)
    5
    >>> print(trf.duplicates_)
    [[0, 2], [1, 4]]
    >>> print(trf.removed_columns_)
    {2: 0, 4: 1}
    >>> print(trf.column_mask_)
    [ True  True False  True False]

    """


    def __init__(
        self,
        *,
        keep:Literal['first', 'last', 'random']='first',
        do_not_drop:Sequence[str] | Sequence[int] | None = None,
        conflict:Literal['raise', 'ignore'] = 'raise',
        equal_nan:bool = False,
        rtol:numbers.Real = 1e-5,
        atol:numbers.Real = 1e-8,
        n_jobs:int | None = None,
        job_size:int = 50
    ) -> None:
        """Initialize the `ColumnDeduplicator` instance."""

        self.keep = keep
        self.do_not_drop = do_not_drop
        self.conflict = conflict
        self.equal_nan = equal_nan
        self.rtol = rtol
        self.atol = atol
        self.n_jobs = n_jobs
        self.job_size = job_size


    # properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @property
    def duplicates_(self) -> DuplicatesType:
        """Get the `duplicates_` attribute.

        Returns
        -------
        duplicates_ : list[list[int]]
            a list of the groups of identical columns, indicated by their
            zero-based column index positions in the originally fit data.

        """

        check_is_fitted(self)

        return self._duplicates


    @property
    def removed_columns_(self) -> RemovedColumnsType:
        """Get the `removed_columns_` attribute.

        Returns
        -------
        removed_columns_ : dict[int, int]
            Dictionary whose keys are the indices of duplicate columns
            removed from the original data, indexed by their column
            location in the original data; the values are the column
            index in the original data of the respective duplicate that
            was kept.

        """

        check_is_fitted(self)

        return self._removed_columns


    @property
    def column_mask_(self) -> ColumnMaskType:
        """Get the `column_mask_` attribute.

        Returns
        -------
        column_mask_ : numpy.ndarray[bool] of shape (`n_features_in_`,)
            Indicates which columns of the fitted data are kept (True)
            and which are removed (False) during transform.

        """

        check_is_fitted(self)

        return self._column_mask
    # END properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def _reset(self) -> Self:
        """Reset the internal data-dependent state of CDT.

        __init__ parameters are not changed.

        Returns
        -------
        self : object
            The `ColumnDeduplicator` instance.

        """

        if hasattr(self, '_duplicates'):
            delattr(self, '_duplicates')

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
        # columns, must build a one-off.

        check_is_fitted(self)

        feature_names_out = get_feature_names_out(
            input_features,
            getattr(self, 'feature_names_in_', None),
            self.n_features_in_
        )

        return feature_names_out[self._column_mask]


    def get_metadata_routing(self):
        """Get metadata routing is not implemented."""

        __ = type(self).__name__
        raise NotImplementedError(
            f"get_metadata_routing is not implemented in {__}"
        )


    # def get_params - inherited from GetParamsMixin


    def partial_fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Perform incremental fitting on one or more batches of data.

        Determine the duplicate columns in the data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. Data to remove duplicate columns from.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `ColumnDeduplicator` instance.

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
            ensure_min_features=2,
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
            reset=not hasattr(self, "duplicates_")
        )

        # do not make an assignment! let the function handle it.
        self._check_feature_names(
            X,
            reset=not hasattr(self, "duplicates_")
        )


        # this must be after _check_feature_names() needs feature_names_in_
        # to be exposed, if available.
        _validation(
            X,
            getattr(self, 'feature_names_in_', None),
            self.conflict,
            self.do_not_drop,
            self.keep,
            self.rtol,
            self.atol,
            self.equal_nan,
            self.n_jobs,
            self.job_size
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

        _current_duplicates: DuplicatesType = \
            _find_duplicates(
                _X=X,
                _rtol=self.rtol,
                _atol=self.atol,
                _equal_nan=self.equal_nan,
                _n_jobs=self.n_jobs,
                _job_size=self.job_size
            )

        # merge the current duplicate columns with duplicates found on
        # previous partial fits
        self._duplicates: DuplicatesType = \
            _merge_dupls(
                getattr(self, '_duplicates', None),
                _current_duplicates
            )

        del _current_duplicates

        # all scipy sparse were converted to csc before _dupl_idxs.
        # change it back to original state. do not mutate X!
        if hasattr(X, 'toarray'):
            X = _og_dtype(X)
            del _og_dtype

        # if 'keep' == 'random', _transform() must pick the same random
        # columns every time. need to set an instance attribute here
        # that doesnt change when _transform() is called. must set a
        # random idx for every set of dupls.
        self._rand_idxs: tuple[int, ...] = _lock_in_random_idxs(
            _duplicates=self._duplicates,
            _do_not_drop=self.do_not_drop,
            _columns=self.feature_names_in_ if \
                hasattr(self, 'feature_names_in_') else None
        )

        self._removed_columns: dict[int, int] = \
            _identify_idxs_to_delete(
                self._duplicates,
                self.keep,
                self.do_not_drop,
                self.feature_names_in_ if \
                    hasattr(self, 'feature_names_in_') else None,
                self.conflict,
                self._rand_idxs
            )

        self._column_mask: npt.NDArray[bool] = \
            np.ones(self.n_features_in_).astype(bool)
        self._column_mask[list(self._removed_columns)] = False

        return self


    def fit(
        self,
        X: XContainer,
        y: Any = None
    ) -> Self:
        """Perform a single fitting on a dataset.

        Determine the duplicate columns in the data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data to remove duplicate columns from.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `ColumnDeduplicator` instance.

        """

        self._reset()
        return self.partial_fit(X, y=y)


    # def fit_transform(self, X, y=None, **fit_params):
    # inherited from FitTransformMixin


    def inverse_transform(
        self,
        X:XContainer,
        copy:bool | None = None
    ) -> XContainer:
        """Revert deduplicated data back to its original state.

        This operation cannot restore any nan-like values that may have
        been in the original untransformed data. :meth:`set_output` does
        not control the output container here, the output container is
        always the same as passed.

        Very little validation is possible to ensure that the passed
        data is valid for the current state of CDT. It is only possible
        to ensure that the number of columns in the passed data match
        the number of columns that are expected to be outputted
        by :meth:`transform` for the current state of CDT. It is up to
        the user to ensure the state of CDT aligns with the state of the
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
        X_inv: array-like of shape (n_samples, n_features)
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

        # the number of columns in X must be equal to the number of
        # features remaining in _column_mask
        if X_inv.shape[1] != np.sum(self._column_mask):
            raise ValueError(
                f"the number of columns in X must be equal to the number "
                f"of columns kept from the fitted data after removing "
                f"duplicates ({np.sum(self._column_mask)})"
            )

        # dont need to do any other validation here, none of the
        # parameters that could be changed by set_params are used here

        # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # ss sparse that cant be sliced
        # if X_inv is coo, dia, bsr, it cannot be sliced. must convert
        # to another ss. so just convert all of them to csc for faster
        # column slicing. need to change it back later.
        if hasattr(X_inv, 'toarray'):
            _og_format = type(X_inv)
            X_inv = X_inv.tocsc()

        X_inv = _inverse_transform(
            X_inv,
            self._removed_columns,
            getattr(self, 'feature_names_in_', None)
        )

        # all scipy sparse were converted to csc before _inverse_transform().
        # change it back to original state.
        if hasattr(X_inv, 'toarray'):
            X_inv = _og_format(X_inv)
            del _og_format

        if isinstance(X_inv, np.ndarray):
            X_inv = np.ascontiguousarray(X_inv)

        return X_inv


    def score(
        self,
        X: Any,
        y: Any = None
    ) -> None:
        """Dummy method to spoof dask Incremental and ParallelPostFit
        wrappers.

        Verified must be here for dask wrappers.

        Parameters
        ----------
        X : Any
            The data. Ignored.
        y : Any
            The target for the data. Ignored.

        Returns
        -------
        None

        """

        check_is_fitted(self)

        return


    # def set_params(self) - inherited from SetParamsMixin


    # def set_output(self) - inherited from SetOutputMixin


    @SetOutputMixin._set_output_for_transform
    def transform(
        self,
        X:XContainer,
        copy:bool | None = None
    ) -> XContainer:
        """Remove the duplicate columns from X.

        Apply the criteria given by `keep`, `do_not_drop`, and `conflict`
        to the sets of duplicate columns found during fit.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            The data to be deduplicated.
        copy : bool | None, default=None
            Whether to make a deepcopy of `X` before the transform.

        Returns
        -------
        X_tr : XContainer of shape (n_samples, n_features - n_removed_features)
            The deduplicated data.

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
            ensure_min_features=2,
            ensure_max_features=None,
            ensure_min_samples=1,
            sample_check=None
        )

        _validation(
            X_tr,
            getattr(self, 'feature_names_in_', None),
            self.conflict,
            self.do_not_drop,
            self.keep,
            self.rtol,
            self.atol,
            self.equal_nan,
            self.n_jobs,
            self.job_size
        )

        self._check_n_features(X_tr, reset=False)

        self._check_feature_names(X_tr, reset=False)

        # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # redo these here in case set_params() was changed after
        # (partial_)fit determine the columns to remove based on given
        # parameters.
        self._removed_columns = \
            _identify_idxs_to_delete(
                self._duplicates,
                self.keep,
                self.do_not_drop,
                getattr(self, 'feature_names_in_', None),
                self.conflict,
                self._rand_idxs
            )

        self._column_mask = np.ones(self.n_features_in_).astype(bool)
        self._column_mask[list(self._removed_columns)] = False
        # end redo

        # ss sparse that cant be sliced
        # if X is coo, dia, bsr, it cannot be sliced. must convert to
        # another ss. so just convert all of them to csc for faster
        # column slicing. need to change it back later.
        if hasattr(X_tr, 'toarray'):
            _og_format = type(X_tr)
            X_tr = X_tr.tocsc()

        X_tr = _transform(X_tr, self._column_mask)

        # all scipy sparse were converted to csc right before the
        # _transform method. change it back to original state.
        if hasattr(X_tr, 'toarray'):
            X_tr = _og_format(X_tr)
            del _og_format

        if isinstance(X_tr, np.ndarray):
            X_tr = np.ascontiguousarray(X_tr)

        return X_tr





