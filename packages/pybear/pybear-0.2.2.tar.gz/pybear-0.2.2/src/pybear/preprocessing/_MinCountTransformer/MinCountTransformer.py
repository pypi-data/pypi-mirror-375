# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Sequence
)
from typing_extensions import Self
import numpy.typing as npt
from ._type_aliases import (
    DataType,
    CountThresholdType,
    OriginalDtypesType,
    TotalCountsByColumnType,
    InstructionsType,
    IgnoreColumnsType,
    HandleAsBoolType,
    YContainer,
    FeatureNamesInType
)
from ..__shared._type_aliases import XContainer

import numbers
import warnings

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ._make_instructions._make_instructions import _make_instructions
from ._partial_fit._original_dtypes_merger import _original_dtypes_merger
from ._partial_fit._tcbc_merger import _tcbc_merger
from ._partial_fit._get_dtypes_unqs_cts import _get_dtypes_unqs_cts
from ._print_instructions._repr_instructions import _repr_instructions
from ._transform._ic_hab_condition import _ic_hab_condition
from ._transform._make_row_and_column_masks import _make_row_and_column_masks
from ._transform._tcbc_update import _tcbc_update
from ._validation._validation import _validation
from ._validation._y import _val_y

from ...base import (
    FeatureMixin,
    # FitTransformMixin, not used, fit_transform needs special handling
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin,
    is_fitted,
    check_is_fitted,
    get_feature_names_out as _get_feature_names_out,
    validate_data
)



class MinCountTransformer(
    FeatureMixin,
    # FitTransformMixin,  # do not use this, need custom code
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin
):
    """Remove examples that contain values whose frequencies within
    their respective feature fall below the specified count threshold.

    `MinCountTransformer` (MCT) is useful in cases where interest is
    only in the events (values) that happen most frequently. MCT removes
    infrequent occurrences that may distort relationships that govern
    the more frequent events.

    MCT follows the scikit-learn API. It has `partial_fit`, `fit`,
    `transform`, `fit_transform`, `set_params`, `get_params`, and
    `get_feature_names_out` methods. The methods that accept `X` and `y`
    arguments can accommodate several types of containers. All MCT `X`
    arguments must be 2D and can be passed as numpy array, pandas
    dataframe, polars dataframe, or any scipy sparse matrix/array. All
    MCT `y` arguments (if passed) can be 1 or 2D and can be passed as
    numpy array, pandas dataframe, pandas series, polars dataframe, or
    polars series.

    At fit time, frequencies of unique values are totalled independently
    on each feature, not across the entire dataset. The uniques and
    their frequencies are generated for every feature, regardless of
    whether the user has made any indications to ignore some of them.
    These results are stored within MCT to be used in conjunction with
    the threshold(s) specified by `count_threshold` during transform.
    At transform time, the ignore policies are applied and for those
    features that are not ignored the frequencies found during fit are
    compared against the count threshold(s) to determine which values
    are to be removed. MCT formulates a recipe for how to act on the
    data, such as "in this particular feature remove values x, y, and z"
    and so on and so forth for all the features that are not ignored.
    Values are removed by deleting the example (row) or feature (column)
    that contains it from the entire dataset. The way in which MCT
    removes the infrequent values depends on the datatype.

    While scanning the features to get uniques and frequencies, MCT
    also assigns an internal datatype to each feature. There are four
    datatypes: 'bin_int' for binary integers in [0, 1] only, 'int' for
    any other column of integers, 'float' for columns that are entirely
    numeric and contain one or more floating-point decimal value, and
    'obj' for columns that contain at least one non-numeric value.

    For all cases except binary integer features, the entire example
    (row) is removed from the dataset. For features of these datatypes
    (string, float, and non-binary integer), the example will always be
    deleted, and the feature will not be deleted for simply containing
    a value whose frequency is below the count threshold. The only way
    a feature of these datatypes can be completely removed is if one
    unique value remains after the instructions to delete rows are
    applied. In that case, those remaining same-valued examples are not
    deleted (reducing the dataset to empty) but the entire feature is
    removed instead. This is always the case when operations leave a
    single value in a column, and cannot be toggled.

    For binary integers, however, the default action is not to delete
    examples, but to delete the entire feature, while leaving the row
    axis intact. MCT does this to preserve as much data as possible.
    The alternative would be to delete the entire row and lose maybe
    thousands of valid values in other features just because of a single
    oddball value in a one-hot encoding, when the value could be removed
    with less collateral damage by simply removing the feature. But,
    should the user want the 'usual' behavior, this can be controlled
    via the `delete_axis_0` parameter. When set to the default value of
    False, the default removal method for binary integers is applied as
    described above. However, if the `delete_axis_0` parameter is set to
    True, both the rows containing the sub-threshold value(s) and the
    feature are removed from the dataset. This makes binary integer
    columns mimic the behavior of all other datatypes.

    To try to further clarify why the `delete_axis_0` parameter exists,
    consider binary integer columns that arose by dummying (one-hot
    encoding) a feature that was originally categorical as strings. Had
    that column not been dummied, MCT would have deleted the examples
    containing infrequent values for that feature, but not the entire
    feature. But as binary integer dummies, the default behavior is to
    delete the feature without deleting the rows. The `delete_axis_0`
    parameter allows the user to force removal of rows as would happen
    under any other case. The `delete_axis_0` parameter is a global
    setting and cannot be toggled for individual features.

    MCT will remove all features that are processed down to a single
    constant value, and this behavior also applies when MCT receives
    training data that from the outset has a feature with a single
    value. MCT will ALWAYS remove a feature with a single constant
    value in it unless the column is ignored. This includes an intercept
    column that the user may want to keep. If the user wishes to retain
    such features, the simplest solution would be to ignore the column
    using `ignore_columns`, which is explained in more detail later.
    Another option is to process the data with MCT, which will remove
    the columns of constants, then re-append them afterward using
    pybear :class:`InterceptManager`. Another workaround is to extract
    the column(s) manually before processesing with MCT then manually
    re-append them later.

    By default, MCT ignores columns it designates as 'float',
    meaning they are excluded from application of the frequency
    rules at transform time. But this behavior can be toggled by
    `ignore_float_columns` (default True). When True, any impact on
    these features could only happen when an example is removed in
    enacting rules made for other features. The user can override
    ignoring float columns and allow the float features' values to be
    subject to removal at transform time. A column of all nans is
    always classified as 'float' by MCT, and would be subject to how
    `ignore_float_columns` is set. See the Notes section for more
    discussion about float columns.

    MCT also defaults to ignoring non-binary integer columns. The
    `ignore_non_binary_integer_columns` parameter (default True) controls
    this behavior in the same way as described for `ignore_float_columns`.
    When set to False, these type of features will also have low
    frequency values removed at transform time (which may mean all the
    values!)

    The `ignore_nan` parameter toggles whether to apply thresholding
    rules to nan values at transform time just like any other discrete
    value. The default behavior (True) will count nan values during the
    fit process, but overlook their frequency counts during the transform
    process and not develop any rules for removal. See the Notes section
    for in-depth discussion about how MCT handles nan-like values.

    The `ignore_float_columns`, `ignore_non_binary_integer_columns`, and
    `ignore_nan` policies are global settings and these behaviors cannot
    be toggled for individual features.

    There is one more 'ignore' parameter: `ignore_columns`. This allows
    the user to specify any individual column(s) they would like MCT to
    ignore during the transform process. The function of the parameter
    is self-explanatory. It accepts several types of values, all of
    which are described in more detail later.

    The `handle_as_bool` parameter (default=None) causes a feature to be
    handled as if it were boolean, i.e., in the same way as binary
    integer columns. Consider a bag-of-words `TextVectorizer` operation
    which results in a feature that is sparse except for a few non-zero
    integer values (which may be different.) `handle_as_bool` allows for
    the non-zero values to be handled as if they are the same value. In
    that way, `handle_as_bool` can be used to indicate the frequency of
    presence (or absence) as opposed to the frequency of each unique
    value.

    In all cases, `ignore_columns`, `ignore_non_binary_integer_columns`,
    and `ignore_float_columns` override the behavior of other parameters.
    For example, if column index 0 was indicated in `ignore_columns` but
    is also indicated in `handle_as_bool`, `ignore_columns` supercedes
    `handle_as_bool` and the feature will be ignored.

    The `ignore_columns` and `handle_as_bool` parameters accept

        a single vector of features names if the fit data is passed
        in a format that contains feature names (e.g., a pandas or
        polars dataframe)

        a single vector of indices that indicate feature positions, or

        a callable that returns 1) or 2) when passed `X`.

    If data is passed as a dataframe with strings as column names during
    fit, MCT will recognize those names when passed to these parameters
    in a 1D list-like.

    In all cases, column indices are recognized, as long as they are
    within range.

    The callable functionality affords the luxury of identifying
    features to ignore or handle as boolean when the ultimate name or
    index of the desired feature(s) is/are not known beforehand, such
    as if the data undergoes another transformation prior to MCT. The
    callable must accept a single argument, the `X` parameter passed to
    methods :meth:`partial_fit`, :meth:`fit`, and :meth:`transform`,
    whereby columns can be identified based on characteristics of `X`.
    Consider a serialized process that includes some operations that act
    on the features of the data, e.g. `TextVectorizer` or `OneHotEncoder`.
    In that case, columns can be identified as ignored or handled as
    boolean mid-stream by passing a callable with an appropriate
    algorithm on the output of the preceding transformer.

    Additional care must be taken when using callables. The safest use
    is with :meth:`fit_transform`, however, use is not limited to only
    that case to allow for use with batch-wise operations. Upon every
    call to `partial_fit` and `transform`, the callable is executed on
    the currently-passed data `X`, generating column names or indices. In
    a serialized data processing operation, the callable must generate
    the same indices for each `X` seen or MCT will return nonsensical
    results.

    The `reject_unseen_values` parameter tells MCT how to handle values
    passed to `transform` that were not seen during fit. When True, any
    value in data passed to `transform` that was not seen during training
    will raise an exception. When False (the default), values not seen
    during fit are ignored and no operations take place for those values
    because rules were not generated for them. The `transform` and
    `fit_transform` methods only execute the rules prescribed by applying
    the count threshold to the frequencies discovered during fit. This
    may lead to the transformed data containing things that appear to
    violate MCT's stated design. In some circumstances, transforming new
    unseen data may result in output that contains one or more features
    that only contain a single value, and this one value could possibly
    be the 'nan' value. (If the rules would have left only one value in
    the feature during fit, then there would be instruction to delete
    the feature entirely.) In these cases, no further action is taken by
    the transform operation to diagnose or address any such conditions.
    The analyst must take care to discover if such conditions exist in
    the transformed data and address it appropriately. By its nature,
    data passed to `fit_transform` must see `fit` before being passed to
    `transform`, which makes `reject_unseen_values` irrelevant in that
    case.

    As MCT removes examples that contain values below the threshold,
    it also collaterally removes values in other features that were not
    necessarily below the threshold as well, possibly causing those
    values' frequencies to fall below the threshold. Another pass
    through MCT would then mark the rows/features associated with those
    values and remove them. MCT can perform this recursive action with
    a single call by appropriate settings to the `max_recursions`
    parameter. This functionality is only available for `fit_transform`
    and not with `partial_fit`, `fit`, and `transform`. This ensures
    that the recursive functionality is working with the entire set of
    data so that the rules developed as the recursion proceeds are
    uniform across all the data. Recursion continues until it is stopped
    for any of these four reasons:

        1) the `max_recursions` specified by the user is reached
        2) all values appear at least `count_threshold` times
        3) all rows would be deleted
        4) all columns would be deleted

    MCT has a convenient `print_instructions` method that allows the
    analyst to view the recipes for deleting rows and columns before
    transforming any data. MCT gets uniques and counts during fit, and
    then uses the parameter settings to formulate instructions for
    ignoring features, deleting rows, and deleting columns. These
    instructions are data-agnostic after fit and can be viewed ad libido
    for any valid parameter settings. In the fitted state, the analyst
    can experiment with different settings via :meth:`set_params` to
    see the impact on the transformation. See the documentation for the
    `print_instructions` method for more information.

    MCT has a :meth:`get_support` method that is available at any time
    that MCT is in a fitted state. It can be either a boolean vector or
    a vector of indices that indicates which features are kept from any
    data that is transformed.

    There is another method, :meth:`get_row_support`, that is only
    available after MCT has transformed data. It is either a boolean
    vector or a vector of indices that indicates which rows were kept
    from the last batch of data passed to `transform`. It is not
    cumulative, meaning this vector is not compiled across multiple
    batches passed to `transform`, it only reflects the last batch.

    Parameters
    ----------
    count_threshold : CountThresholdType, default=3
        The threshold that determines whether a value is removed from
        the data (frequency is below threshold) or retained (frequency
        is greater than or equal to threshold.) When passed as a single
        integer, it must be >= 2 and that threshold value is applied
        to all features. If passed as a 1D vector, it must have the
        same length as the number of the features in the data and each
        value is applied to its respective feature. All thresholds must
        be >= 1, and at least one value must be >= 2. Setting the
        threshold for a feature to 1 is the same as ignoring the feature.
    ignore_float_columns : bool, default=True
        If True, values and frequencies within float features are ignored
        and the feature is retained through transform. If False, the
        feature is handled as if it is categorical and unique values are
        subject to count threshold rules and possible removal. See the
        Notes section for more discussion about float features.
    ignore_non_binary_integer_columns : bool, default=True
        If True, values and frequencies within non-binary integer
        features are ignored and the feature is retained through
        transform. If False, the feature is handled as if it is
        categorical and unique values are subject to count threshold
        rules and possible removal.
    ignore_columns : IgnoreColumnsType, default=None
        Excludes indicated features from the thresholding operation. A
        one-dimensional vector of integer index positions or feature
        names (if data formats containing column names were used during
        fitting.) Also accepts a callable that creates such vectors when
        passed the data (the `X` argument). THERE ARE NO PROTECTIONS IN
        PLACE IF THE CALLABLE GENERATES DIFFERENT PLAUSIBLE OUTPUTS ON
        DIFFERENT BATCHES IN AN EPOCH OF DATA. IF CONSISTENCY OF IGNORED
        COLUMNS IS REQUIRED, THEN THE USER MUST ENSURE THAT THE CALLABLE
        PRODUCES IDENTICAL OUTPUTS FOR EACH BATCH OF DATA WITHIN AN
        EPOCH.
    ignore_nan : bool, default=True
        If True, nan-like values are ignored in all features and pass
        through the transform operation; one could only be removed
        collateraly by removal of examples for causes dictated by other
        features. If False, frequencies for nan-likes are calculated and
        compared against `count_threshold`. See the Notes section for
        more on how MCT handles nan-like values.
    handle_as_bool : HandleAsBoolType, default=None
        For the indicated features, non-zero values within the feature
        are treated as if they are the same value. Accepts a 1D vector
        of integer index positions or feature names (if data formats
        containing column names were used during fitting.) Also accepts
        a callable that creates such vectors when passed the data (the
        `X` argument). THERE ARE NO PROTECTIONS IN PLACE IF THE CALLABLE
        GENERATES DIFFERENT PLAUSIBLE OUTPUTS ON DIFFERENT BATCHES IN AN
        EPOCH OF DATA. IF CONSISTENCY OF COLUMNS TO BE HANDLED AS BOOLEAN
        IS REQUIRED, THEN THE USER MUST ENSURE THAT THE CALLABLE PRODUCES
        IDENTICAL OUTPUTS FOR EACH BATCH OF DATA WITHIN AN EPOCH.
    delete_axis_0 : bool, default=False
        Only applies to features indicated in `handle_as_bool` or binary
        integer features such as those generated by `OneHotEncoder`.
        Under normal operation of MCT, when the frequency of one of the
        two values in a binary feature is below `count_threshold`, the
        minority-class examples would not be removed along the example
        axis, but the entire feature would be removed, leaving all
        other data intact. The `delete_axis_0` parameter overrides this
        behavior. When `delete_axis_0` is False, the default behavior
        for binary columns is used, as described above. If True, however,
        the default behavior is overrided and examples associated with
        the minority value are removed along the example axis which would
        leave only one value in the feature, at which point the feature
        would be also be removed for containing only one value.
    reject_unseen_data : bool, default=False
        If False, new values encountered during transform that were not
        seen during fit are ignored. If True, MCT will terminate when
        a value that was not seen during fit is encountered while
        transforming data.
    max_recursions : int, default=1
        The number of times MCT repeats its algorithm on passed data.
        Only available for `fit_transform`.

    Attributes
    ----------
    n_features_in_ : int
        The number of features seen during fit.
    feature_names_in_ : FeatureNamesInType of shape (`n_features_in_`,)
        Names of features seen during fit. Defined only when `X` is
        passed in a container that has feature names and the feature
        names are all strings. If accessed when not defined, MCT will
        raise an AttributeError.
    original_dtypes_
    total_counts_by_column_
    instructions_

    Notes
    -----
    Concerning the handling of nan-like values. MCT can recognize
    various nan-like formats, such as numpy.nan, pandas.NA, str(nan),
    None, and others. When collecting uniques and counts during fit,
    MCT extracts chunks of columns from the data and converts them to
    numpy array. Then MCT casts all nan-like values to numpy.nan. The
    user should be wary that regardless of what type of nan-like values
    were passed during fit, MCT will report them as all numpy.nan in the
    attributes :attr:`total_counts_by_column_` and :attr:`instructions_`.
    If you are unlucky enough to have multiple types of nan-like values
    in your data, be a pro and use pybear :class:`NanStandardizer`
    or `nan_mask` to cast them all to the same format. See `ignore_nan`.

    Concerning float features. MCT was never really intended to perform
    thresholding on float columns, but there are use cases where float
    columns have repeating values. So the functionality exists, on the
    off-chance of a legitimate application. pybear typically recommends
    ignoring all float columns. Internally, when MCT gathers uniques and
    counts, it builds a dictionary keyed by column indices and the values
    are dictionaries. The sub-dictionaries are keyed by the uniques in
    each respective column, and the values are the respective counts for
    those uniques. For a float column, in most applications every value
    in the column is unique, and the dictionary fills as such. The user
    is advised that a float column with, say, 100,000,000 unique values
    will generate an equally sized Python dictionary, which has immense
    carrying-cost, and will be a pinch-point for MCT and your RAM.

    The analyst is cautioned that this transformer

        modifies data dimensionality along the example axis, and

        necessarily forces such an operation on a target object,
        which MCT methods accommodate by accepting target arguments.

    In supervised learning, if the data dimensionality along the example
    axis is changed, the target must also correspondingly change along
    the example axis. These two characteristics of MCT violate at least
    the scikit-learn transformer API and the scikit-learn pipeline API.

    For pipeline applications, there are some options available beyond
    the scikit-learn pipeline implementation.

    https://stackoverflow.com/questions/25539311/
    custom-transformer-for-sklearn-pipeline-that-alters-both-x-and-y
    The package imblearn, which is built on top of sklearn, contains an
    estimator FunctionSampler that allows manipulating both the features
    array, X, and target array, y, in a pipeline step. Note that using
    it in a pipeline step requires using the Pipeline class in imblearn
    that inherits from the one in sklearn.

    For technical reasons, pybear does not recommend wrapping MCT
    with dask_ml Incremental and ParallelPostFit wrappers. However,
    you can accomplish the same effect by embedding MCT in for loops
    and computing the chunks of your data before passing them to
    `partial_fit` and `transform`.

    **Type Aliases**

    XContainer:
        numpy.ndarray | pandas.DataFrame | polars.DataFrame
        | ss.csr_matrix | ss.csc_matrix | ss.coo_matrix | ss.dia_matrix
        | ss.lil_matrix | ss.dok_matrix | ss.bsr_matrix | ss.csr_array
        | ss.csc_array | ss.coo_array | ss.dia_array | ss.lil_array
        | ss.dok_array | ss.bsr_array

    YContainer:
        numpy.ndarray | pandas.DataFrame | pandas.Series
        | polars.DataFrame | polars.Series

    DataType:
        numbers.Number | str

    CountThresholdType:
        int | Sequence[int]

    OriginalDtypesType:
        numpy.ndarray[Literal['bin_int', 'int', 'float', 'obj']]

    TotalCountsByColumnType:
        dict[int, dict[DataType, int]]

    InstrLiterals:
        Literal['INACTIVE', 'DELETE ALL', 'DELETE COLUMN']

    InstructionsType:
        dict[int, list[DataType | InstrLiterals]]

    IcHabCallable:
        Callable[[XContainer], Sequence[int] | Sequence[str]]

    IgnoreColumnsType:
        None | Sequence[int] | Sequence[str] | IcHabCallable]

    HandleAsBoolType:
        None | Sequence[int] | Sequence[str] | IcHabCallable]

    FeatureNamesInType:
        numpy.ndarray[object]

    Examples
    --------
    >>> from pybear.preprocessing import MinCountTransformer
    >>> import numpy as np
    >>> column1 = np.array(['a', 'a', 'b', 'c', 'b', 'd'])
    >>> column2 = np.array([0, 1, 0, 1, 2, 0])
    >>> data = np.vstack((column1, column2)).transpose().astype(object)
    >>> data
    array([['a', '0'],
           ['a', '1'],
           ['b', '0'],
           ['c', '1'],
           ['b', '2'],
           ['d', '0']], dtype=object)
    >>> MCT = MinCountTransformer(2, ignore_non_binary_integer_columns=False)
    >>> MCT.fit(data)
    MinCountTransformer(count_threshold=2, ignore_non_binary_integer_columns=False)
    >>> print(MCT.original_dtypes_)
    ['obj' 'int']
    >>> tcbc = MCT.total_counts_by_column_
    >>> tcbc[0]
    {np.str_('a'): 2, np.str_('b'): 2, np.str_('c'): 1, np.str_('d'): 1}
    >>> tcbc[1]
    {np.str_('0'): 3, np.str_('1'): 2, np.str_('2'): 1}
    >>> print(MCT.instructions_)
    {0: [np.str_('c'), np.str_('d')], 1: [np.str_('2')]}
    >>> print(MCT.transform(data))
    [['a' '0']
     ['a' '1']
     ['b' '0']]

    """


    def __init__(
        self,
        count_threshold:CountThresholdType = 3,
        *,
        ignore_float_columns:bool = True,
        ignore_non_binary_integer_columns:bool = True,
        ignore_columns:IgnoreColumnsType = None,
        ignore_nan:bool = True,
        handle_as_bool:HandleAsBoolType = None,
        delete_axis_0:bool = False,
        reject_unseen_values:bool = False,
        max_recursions:int = 1
    ) -> None:
        """Initialize the `MinCountTransformer` instance."""

        self.count_threshold = count_threshold
        self.ignore_float_columns = ignore_float_columns
        self.ignore_non_binary_integer_columns = ignore_non_binary_integer_columns
        self.ignore_columns = ignore_columns
        self.ignore_nan = ignore_nan
        self.handle_as_bool = handle_as_bool
        self.delete_axis_0 = delete_axis_0
        self.reject_unseen_values = reject_unseen_values
        self.max_recursions = max_recursions


    # properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @property
    def original_dtypes_(self) -> OriginalDtypesType:
        """Get the `original_dtypes_` attribute.

        The datatype assigned by MCT to each feature. nan-like values
        are ignored while discovering datatypes and the collective
        datatype of the non-nan values is reported.

        Returns
        -------
        original_dtypes_ : OriginalDtypesType of shape (n_features_in,)
            The datatype assigned by MCT to each feature.

        """

        check_is_fitted(self)

        return self._original_dtypes


    @property
    def total_counts_by_column_(self) -> TotalCountsByColumnType:
        """Get the `total_counts_by_column_` attribute.

        A dictionary of the uniques and their frequencies found in each
        column of the fitted data. The keys are the zero-based column
        indices and the values are dictionaries. The inner dictionaries
        are keyed by the unique values found in that respective column
        and the values are their counts. All nan-like values are
        represented by numpy.nan.

        Returns
        -------
        total_counts_by_column_ : TotalCountsByColumnType
            A dictionary of the uniques and their frequencies found in
            each column of the fitted data.

        """

        check_is_fitted(self)

        return self._total_counts_by_column


    @property
    def instructions_(self) -> InstructionsType:
        """Get the `instructions_` attribute.

        A dictionary that is keyed by column index and the values are
        lists. Within the lists is information about operations to
        perform with respect to values in the column. The following
        items may be in the list:

        'INACTIVE'
            ignore the column and carry it through for all other
            operations.

        Individual values
            indicates to delete the rows along the example axis that
            contain that value in that column, possibly including
            nan-like values.

        'DELETE ALL'
            delete every value in the column along the example axis,
            thereby deleting all data.

        'DELETE COLUMN'
            perform any individual row deletions that need to take place
            while the column is still in the data, then delete the column
            from the data.

        Returns
        -------
        instructions_ : InstructionsType
            A dictionary that is keyed by column index and the values
            are lists. Within the lists is information about operations
            to perform with respect to values in the column.

        """

        check_is_fitted(self)

        return self._make_instructions()
    # END properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def __pybear_is_fitted__(self) -> bool:
        # must have this because there are no trailing-underscore attrs
        # generated by {partial_}fit(). all the trailing-underscore attrs
        # are accessed via @property.
        return hasattr(self, '_total_counts_by_column')


    def reset(self) -> Self:
        """Reset the internal state of `MinCountTransformer`.

        __init__ parameters are not changed.

        Returns
        -------
        self : object
            The `MinCountTransformer` instance.

        """

        _attrs = [
            '_ignore_columns', '_handle_as_bool', '_n_rows_in',
            '_original_dtypes', '_total_counts_by_column', '_row_support',
            'n_features_in_', 'feature_names_in_'
        ]

        for _attr in _attrs:

            if hasattr(self, _attr):
                delattr(self, _attr)

        del _attrs

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

        feature_names_out = _get_feature_names_out(
            input_features,
            getattr(self, 'feature_names_in_', None),
            self.n_features_in_
        )

        return feature_names_out[self.get_support(indices=False)]


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

        Get the uniques and their frequencies for all features in the
        batch of data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data used to determine the uniques and their
            frequencies.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `MinCountTransformer` instance.

        """


        self._recursion_check()


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
            ensure_min_samples=3,
            sample_check=None
        )

        # GET n_features_in_, feature_names_in_, _n_rows_in_ ** * ** *
        # do not make assignments! let the functions handle it.
        self._check_feature_names(X, reset=not is_fitted(self))
        self._check_n_features(X, reset=not is_fitted(self))

        # IF WAS PREVIOUSLY FITTED, THEN self._n_rows_in EXISTS
        if hasattr(self, '_n_rows_in'):
            self._n_rows_in += X.shape[0]
        else:
            self._n_rows_in = X.shape[0]

        # END GET n_features_in_, feature_names_in_, _n_rows_in_ ** * **

        _validation(
            X,
            self.count_threshold,
            self.ignore_float_columns,
            self.ignore_non_binary_integer_columns,
            self.ignore_columns,
            self.ignore_nan,
            self.handle_as_bool,
            self.delete_axis_0,
            self.reject_unseen_values,
            self.max_recursions,
            getattr(self, 'n_features_in_'),
            getattr(self, 'feature_names_in_', None)
        )


        # GET TYPES, UNQS, & CTS FOR ACTIVE COLUMNS ** ** ** ** ** ** **

        # scipy coo, dia, and bsr cant be sliced by columns, need to be
        # converted to another format. standardize all scipy sparse to
        # csc, makes for quicker column scans when getting unqs/cts.
        # need to change it back after the scan. dont mutate X, avoid
        # copies of X.
        if hasattr(X, 'toarray'):
            _og_dtype = type(X)
            X = ss.csc_array(X)


        # need to run all columns to get the dtypes; no columns are
        # ignored, for this operation, so any ignore inputs do not matter.
        # getting dtypes on columns that are ignored is needed to validate
        # new partial fits have appropriate data.

        DTYPE_UNQS_CTS_TUPLES: list[tuple[str, dict[DataType, int]]] = \
            _get_dtypes_unqs_cts(X)

        # if scipy sparse, change back to the original format. do this
        # before going into the ic/hab callables below, possible that
        # the callable may have some dependency on the container.
        if hasattr(X, 'toarray'):
            X = _og_dtype(X)
            del _og_dtype


        _col_dtypes = np.empty(self.n_features_in_, dtype='<U8')
        # DOING THIS for LOOP 2X TO KEEP DTYPE CHECK SEPARATE AND PRIOR
        # TO MODIFYING self._total_counts_by_column, PREVENTS INVALID
        # DATA FROM INVALIDATING ANY VALID UNQS/CT IN THE INSTANCE'S
        # self._total_counts_by_column
        for col_idx, (_dtype, UNQ_CT_DICT) in enumerate(DTYPE_UNQS_CTS_TUPLES):
            _col_dtypes[col_idx] = _dtype

        self._original_dtypes = _original_dtypes_merger(
            _col_dtypes,
            getattr(self, '_original_dtypes', None),
            self.n_features_in_
        )

        del _col_dtypes

        self._total_counts_by_column: dict[int, dict[DataType, int]] = \
            _tcbc_merger(
                DTYPE_UNQS_CTS_TUPLES,
                getattr(self, '_total_counts_by_column', {})
            )

        del DTYPE_UNQS_CTS_TUPLES

        # END GET TYPES, UNQS, & CTS FOR ACTIVE COLUMNS ** ** ** ** ** *

        self._ignore_columns, self._handle_as_bool = \
            _ic_hab_condition(
                X,
                self.ignore_columns,
                self.handle_as_bool,
                self.ignore_float_columns,
                self.ignore_non_binary_integer_columns,
                self._original_dtypes,
                self.count_threshold,
                self.n_features_in_,
                getattr(self, 'feature_names_in_', None),
                _raise=True
            )

        X = np.ascontiguousarray(X)

        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Perform a single fitting on a dataset.

        Get the uniques and their frequencies for all features in the
        dataset.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data used to determine the uniques and their
            frequencies.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `MinCountTransformer` instance.

        """

        self.reset()

        return self.partial_fit(X, y)


    def fit_transform(
        self,
        X:XContainer,
        y:YContainer = None
    ) -> XContainer | tuple[XContainer, YContainer]:
        """Fits `MinCountTransformer` to `X` and returns a transformed
        version of `X`.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            The data that is to be reduced according to the thresholding
            rules found during fit.
        y : YContainer, default=None
            The target for the data. None for unsupervised transformations.

        Returns
        -------
        out : XContainer | tuple[XContainer, YContainer]

            X_tr: XContainer of shape (n_transformed_samples,
            n_transformed_features) - the transformed data.

            y_tr: array-like of shape (n_transformed_samples, ) or
            (n_transformed_samples, n_outputs) - Transformed target,
            if provided.

        """

        # cant use FitTransformMixin, need custom code to handle
        # _recursion_check

        # this temporarily creates an attribute that is only looked at
        # by self._recursion_check. recursion check needs to be disabled
        # when calling transform() from this method, but otherwise the
        # recursion check in transform() must always be operative.
        self.recursion_check_disable = True

        __ = self.fit(X, y).transform(X, y)

        delattr(self, 'recursion_check_disable')

        return __


    def get_row_support(self, indices:bool=False) -> npt.NDArray:
        """Get a boolean mask or the integer indices of the rows retained
        during the last transform.

        Parameters
        ----------
        indices : bool, default=False
            If True, the return value will be a vector of integers;
            otherwise, a 1D boolean mask.

        Returns
        -------
        row_support : numpy.ndarray
            A slicer that selects the retained rows from the `X` most
            recently seen by `transform`. If `indices` is False, this is
            a boolean array of shape (n_samples, ) in which an element
            is True if its corresponding row is selected for retention.
            If `indices` is True, this is an integer array of shape
            (n_transformed_samples, ) whose values are indices into the
            sample axis.

        """

        check_is_fitted(self)

        if not hasattr(self, '_row_support'):
            raise AttributeError(
                f"get_row_support() can only be accessed after some data "
                f"has been transformed"
            )

        if indices is False:
            return self._row_support
        elif indices is True:
            return np.arange(len(self._row_support))[self._row_support]


    def get_support(self, indices:bool = False) -> npt.NDArray:
        """Get a boolean mask or the integer indices of the features
        retained from the fitted data.

        Parameters
        ----------
        indices : bool, default=False
            If True, the return value will be a vector of integers; if
            False, the return will be a 1D boolean mask.

        Returns
        -------
        support : numpy.ndarray
            A mask that selects the features that are  retained during
            transform. If `indices` is False, this is a boolean vector
            of shape (`n_features_in_`,) in which an element is True if
            its corresponding feature is selected for retention. If
            `indices` is True, this is an integer array of shape
            (n_transformed_features, ) whose values are indices into
            the input features.

        """

        check_is_fitted(self)

        # must use _make_instructions() in order to construct the column
        # support mask after fit and before a transform. otherwise, if an
        # attribute _column_support were assigned to COLUMN_KEEP_MASK in
        # transform() like _row_support is assigned to ROW_KEEP_MASK, then
        # a transform would have to be done before being able to access
        # get_support().

        COLUMNS = np.array(
            ['DELETE COLUMN' not in v for v in self._make_instructions().values()]
        )

        if indices is False:
            return np.array(COLUMNS)
        elif indices is True:
            return np.arange(self.n_features_in_)[COLUMNS].astype(np.uint32)


    def print_instructions(
        self,
        *,
        clean_printout:bool = True,
        max_char:int = 99
    ) -> None:
        """Display instructions generated for the current fitted state,
        subject to the current settings of the parameters.

        The printout will indicate what values and columns will be
        deleted, and if all columns or all rows will be deleted.
        Use :meth:`set_params` after finishing fits to change MCTs
        parameters and see the impact on the transformation.

        If the instance has multiple recursions (i.e., `max_recursions`
        is > 1), parameters cannot be changed via `set_params`, but the
        net effect of all recursions is displayed (remember that multiple
        recursions can only be accessed through :meth:`fit_transform`).
        The results are displayed as a single set of instructions, as if
        to perform the cumulative effect of the recursions in a single
        step.

        This print utility can only report the instructions and outcomes
        that can be directly inferred from the information learned
        about uniques and counts during fitting. It cannot predict any
        interaction effects that occur during transform of a dataset
        that may ultimately cause all rows to be deleted. It also cannot
        capture the effects of previously unseen values that may be
        passed during transform.

        Parameters
        ----------
        clean_printout : bool
            Truncate printout to fit on screen.
        max_char : int, default=99
            The maximum number of characters to display per line if
            `clean_printout` is set to True. Ignored if `clean_printout`
            is False. Must be an integer in range [72, 120].

        Returns
        -------
        None

        """

        check_is_fitted(self)

        # params can be changed after fit & before calling this by
        # set_params(). need to validate params. _make_instructions()
        # handles the validation of almost all the params in __init__
        # except max_recursions and reject_unseen_params.
        # max_recursions cannot be changed in set_params once fitted.
        # Neither of these are used here.

        # after fit, ic & hab are blocked from being set to callable
        # (but is OK if they were already a callable when fit.) that
        # means that the mapping of the callables used during fit lives
        # in self._ignore_columns and/or self._handle_as_bool. but,
        # set_params does not block setting ic/hab to Sequence[str] or
        # Sequence[int]. so if self.ignore_columns and/or
        # self.handle_as_bool are callable, we need to pass the output
        # that lives in _ic & _hab. but if not callable, need to use the
        # (perhaps changed) ic/hab in self.ignore_columns &
        # self.handle_as_bool. if ic/hab were changed to Sequence[str]
        # in set_params, need to map to Sequence[int].

        # _ic_hab_condition takes X, but we dont have it so we need to
        # spoof it. X doesnt matter here, X is only for ic/hab callable
        # in partial_fit() and transform(). since we are always passing
        # ic/hab as vectors, dont need to worry about the callables.


        if callable(self.ignore_columns):
            _wip_ic = self._ignore_columns
        else:
            _wip_ic = self.ignore_columns

        if callable(self.handle_as_bool):
            _wip_hab = self._handle_as_bool
        else:
            _wip_hab = self.handle_as_bool

        self._ignore_columns, self._handle_as_bool = \
            _ic_hab_condition(
                None,     # placehold X
                _wip_ic,
                _wip_hab,
                self.ignore_float_columns,
                self.ignore_non_binary_integer_columns,
                self._original_dtypes,
                self.count_threshold,
                self.n_features_in_,
                getattr(self, 'feature_names_in_', None),
                _raise=True
            )

        del _wip_ic, _wip_hab

        _repr_instructions(
            _delete_instr=self._make_instructions(),
            _total_counts_by_column=self._total_counts_by_column,
            _thresholds=self.count_threshold,
            _n_features_in=self.n_features_in_,
            _feature_names_in=getattr(self, 'feature_names_in_', None),
            _clean_printout=clean_printout,
            _max_char=max_char
        )


    def score(
        self,
        X:Any,
        y:Any = None
    ) -> None:
        """Dummy method to spoof dask_ml Incremental and ParallelPostFit
        wrappers.

        As of first release no longer designing for dask_ml wrappers.

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


    # def set_output(self, transform) - inherited from SetOutputMixin


    def set_params(self, **params) -> Self:
        """Set the parameters of the MCT instance.

        Pass the exact parameter name and its value as a keyword argument
        to the `set_params` method call. Or use ** dictionary unpacking
        on a dictionary keyed with exact parameter names and the new
        parameter values as the dictionary values. Valid parameter keys
        can be listed with :meth:`get_params`. Note that you can directly
        set the parameters of `MinCountTransformer`.

        Once MCT is fitted, `set_params` blocks some parameters from
        being set to ensure the validity of results. In these cases, to
        use different parameters without creating a new instance of MCT,
        call MCT :meth:`reset` on the instance. Otherwise, create a new
        MCT instance.

        `max_recursions` is always blocked when MCT is in a fitted state.

        If MCT was fit with `max_recursions` >= 2 (only
        a :meth:`fit_transform` could have be done), all parameters are
        blocked. To break the block, call `reset` before calling
        `set_params`. All information learned from any prior
        `fit_transform` will be lost.

        Also, when MCT has been fitted, `ignore_columns` and
        `handle_as_bool` cannot be set to a callable (they can, however,
        be changed to None, Sequence[int], or Sequence[str]). To set
        these parameters to a callable when MCT is in a fitted state,
        call `reset` then use `set_params` to set them to a callable.
        All information learned from any prior fit(s) will be lost when
        calling 'reset'.

        Parameters
        ----------
        **params : dict[str, Any]
            `MinCountTransformer` parameters.

        Returns
        -------
        self : object
            The `MinCountTransformer` instance.

        """


        # if MCT is fitted with max_recursions==1, allow everything but
        # block 'ignore_columns' and 'handle_as_bool' from being set to
        # callables.
        # if max_recursions is >= 2, block everything.
        # if not fitted, allow everything to be set.
        if is_fitted(self):

            if self.max_recursions > 1:
                raise ValueError(
                    f":meth: 'set_params' blocks all parameters from being "
                    f"set when MCT is fitted with :param: 'max_recursions' "
                    f">= 2. \nto set new parameter values, call :meth: "
                    f"'reset' then call :meth: 'set_params'."
                )

            _valid_params = {}
            _invalid_params = {}
            _garbage_params = {}
            _spf_params = self.get_params()
            for param in params:
                if param not in _spf_params:
                    _garbage_params[param] = params[param]
                elif param == 'max_recursions':
                    _invalid_params[param] = params[param]
                elif param in ['ignore_columns', 'handle_as_bool'] \
                        and callable(params[param]):
                    _invalid_params[param] = params[param]
                else:
                    _valid_params[param] = params[param]

            if any(_garbage_params):
                # let super.set_params raise
                super().set_params(**params)

            if 'max_recursions' in _invalid_params:
                warnings.warn(
                    "Once MCT is fitted, :param: 'max_recursions' cannot be "
                    "changed. To change this setting, call :meth: 'reset' or "
                    "create a new instance of MCT. 'max_recursions' has not "
                    "been changed but any other valid parameters passed have "
                    "been set."
                )

            if any(
                [_ in _invalid_params for _ in ['ignore_columns', 'handle_as_bool']]
            ):
                warnings.warn(
                    "Once MCT is fitted, :params: 'ignore_columns' and "
                    "'handle_as_bool' cannot be set to callables. \nThe "
                    "currently passed parameter(s) "
                    f"{', '.join(list(_invalid_params))} has/have been "
                    "skipped, but any other valid parameters that were "
                    "passed have been set. \nTo set "
                    "ignore_columns/handle_as_bool to callables without "
                    "creating a new instance of MCT, call :meth: 'reset' "
                    "on this instance then set the callable parameter "
                    "values (all results from previous fits will be lost). "
                    "Otherwise, create a new instance of MCT."
                )

            super().set_params(**_valid_params)

            del _valid_params, _invalid_params, _garbage_params, _spf_params

        else:

            super().set_params(**params)


        return self


    @SetOutputMixin._set_output_for_transform
    def transform(
        self,
        X:XContainer,
        y:YContainer | None = None,
        *,
        copy:bool | None = None
    ) -> tuple[XContainer, YContainer] | XContainer:
        """Reduce `X` by the thresholding rules found during fit.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            The data that is to be reduced according to the thresholding
            rules found during fit.
        y : YContainer | None, default=None
            The target for the data. None for unsupervised
            transformations.
        copy : bool | None, default=None
            Whether to make a deep copy of `X` (and `y`, if provided)
            before doing the transformation.

        Returns
        -------
        out : XContainer | tuple[XContainer, YContainer]

            X_tr : XContainer of shape (n_transformed_samples,
            n_transformed_features) The transformed data.

            y_tr: YContainer of shape (n_transformed_samples, ) or
            (n_transformed_samples, n_outputs) - Transformed target,
            if provided.

        """


        check_is_fitted(self)

        if not isinstance(copy, (bool, type(None))):
            raise TypeError(f"'copy' must be boolean or None")

        self._recursion_check()

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
            ensure_min_samples=3,
            sample_check=None
        )

        self._check_feature_names(X_tr, reset=False)
        self._check_n_features(X_tr, reset=False)

        _validation(
            X_tr,
            self.count_threshold,
            self.ignore_float_columns,
            self.ignore_non_binary_integer_columns,
            self.ignore_columns,
            self.ignore_nan,
            self.handle_as_bool,
            self.delete_axis_0,
            self.reject_unseen_values,
            self.max_recursions,
            getattr(self, 'n_features_in_'),
            getattr(self, 'feature_names_in_', None)
        )

        # END X handling ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # y handling ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if y is not None:

            # When dask_ml Incremental and ParallelPostFit (versions
            # 2024.4.4 and 2023.5.27 at least) are passed y = None, they
            # are putting y = ('', order[i]) into the dask graph for y
            # and sending that as the value of y to the wrapped partial
            # fit method. All use cases where y=None are like this, it
            # will always happen and there is no way around it. To get
            # around this, look to see if y is of the form tuple(str, int).
            # If that is the case, override y with y = None.

            # as of 25_06_17 no longer designing for dask_ml wrappers.
            # if isinstance(y, tuple) and isinstance(y[0], str) \
            #         and isinstance(y[1], int):
            #     y = None

            # END accommodate dask_ml junk y ** * ** * ** * ** * ** * **

            y_tr = validate_data(
                y,
                copy_X=copy or False,
                cast_to_ndarray=False,
                accept_sparse=None,
                dtype='any',
                require_all_finite=False,
                cast_inf_to_nan=False,
                standardize_nan=False,
                allowed_dimensionality=(1, 2),
                ensure_2d=False,
                order='C',
                ensure_min_features=1,
                ensure_max_features=None,
                ensure_min_samples=3,
                sample_check=X.shape[0]
            )

            _val_y(y_tr)
        else:
            y_tr = None
        # END y handling ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # extra count_threshold val
        _base_err = (
            f":param: 'count_threshold' is >= the total number of rows "
            f"seen during fitting. this is a degenerate condition. "
            f"\nfit more data or set a lower count_threshold."
        )
        if isinstance(self.count_threshold, numbers.Integral) \
                and self.count_threshold >= self._n_rows_in:
            raise ValueError(_base_err)
        # must be list-like
        elif np.any(self.count_threshold) >= self._n_rows_in:
            raise ValueError(f"at least one value in " + _base_err)
        del _base_err


        # VALIDATE _ignore_columns & handle_as_bool; CONVERT TO IDXs **

        # PERFORM VALIDATION & CONVERT ic/hab callables to IDXS.
        # _ignore_columns MUST BE BEFORE _make_instructions

        self._ignore_columns, self._handle_as_bool = \
            _ic_hab_condition(
                X_tr,
                self.ignore_columns,
                self.handle_as_bool,
                self.ignore_float_columns,
                self.ignore_non_binary_integer_columns,
                self._original_dtypes,
                self.count_threshold,
                self.n_features_in_,
                getattr(self, 'feature_names_in_', None),
                _raise=True
            )
        # END handle_as_bool -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # END VALIDATE _ignore_columns & handle_as_bool; CONVERT TO IDXs

        _delete_instr = self._make_instructions()

        # if scipy sparse, dia, coo, and bsr cannot be indexed, need to
        # convert to an indexable sparse. since this needs to be done,
        # might as well convert all scipy sparse to csc for fast column
        # operations. need to change this back later.
        # do this after the ignore_columns/handle_as_bool callables, the
        # callables may depend on the container.
        if hasattr(X_tr, 'toarray'):
            _og_dtype = type(X_tr)
            X_tr = X_tr.tocsc()

        # BUILD ROW_KEEP & COLUMN_KEEP MASKS ** ** ** ** ** ** ** ** **

        ROW_KEEP_MASK, COLUMN_KEEP_MASK = \
            _make_row_and_column_masks(
                X_tr,
                self._total_counts_by_column,
                _delete_instr,
                self.reject_unseen_values
            )

        # END BUILD ROW_KEEP & COLUMN_KEEP MASKS ** ** ** ** ** ** ** **

        self._row_support = ROW_KEEP_MASK.copy()

        if all(ROW_KEEP_MASK) and all(COLUMN_KEEP_MASK):
            # Skip all recursion code.
            # if all rows and all columns are kept, the data has converged
            # to a point where all the values in every column appear in
            # their respective column at least count_threshold times.
            # There is no point to performing any more possible recursions.
            pass
        else:
            # X must be 2D, np, pd, or csc
            if isinstance(X_tr, np.ndarray):
                X_tr = X_tr[ROW_KEEP_MASK, :]
                X_tr = X_tr[:, COLUMN_KEEP_MASK]
            elif isinstance(X_tr, pd.DataFrame):
                X_tr = X_tr.loc[ROW_KEEP_MASK, :]
                X_tr = X_tr.loc[:, COLUMN_KEEP_MASK]
            elif isinstance(X_tr, pl.DataFrame):
                X_tr = X_tr.filter(ROW_KEEP_MASK)
                X_tr = X_tr[:, COLUMN_KEEP_MASK]
            elif isinstance(X_tr, (ss.csc_matrix, ss.csc_array)):
                # ensure bool mask for ss
                X_tr = X_tr[ROW_KEEP_MASK.astype(bool), :]
                X_tr = X_tr[:, COLUMN_KEEP_MASK.astype(bool)]
            else:
                raise Exception(
                    f"expected X as ndarray, pd df, or csc. got {type(X_tr)}."
                )

            if y_tr is not None:
                # y can be only np or pd, 1 or 2D
                if isinstance(y_tr, np.ndarray):
                    y_tr = y_tr[ROW_KEEP_MASK]
                elif isinstance(y_tr, pd.Series):
                    y_tr = y_tr.loc[ROW_KEEP_MASK]
                elif isinstance(y_tr, pd.DataFrame):
                    y_tr = y_tr.loc[ROW_KEEP_MASK, :]
                elif isinstance(y_tr, pl.Series):
                    y_tr = y_tr.filter(ROW_KEEP_MASK)
                elif isinstance(y_tr, pl.DataFrame):
                    y_tr = y_tr.filter(ROW_KEEP_MASK)
                else:
                    raise Exception(
                        f"expected y as ndarray or pd/pl df/series, got {type(y_tr)}."
                    )

            # v v v everything below here is for recursion v v v v v v
            if self.max_recursions > 1:

                # NEED TO RE-ALIGN _ignore_columns, _handle_as_bool AND
                # count_threshold FROM WHAT THEY WERE FOR self TO WHAT
                # THEY ARE FOR THE CURRENT (POTENTIALLY COLUMN MASKED)
                # DATA GOING INTO THIS RECURSION
                # do not pass the function!
                IGN_COL_MASK = np.zeros(self.n_features_in_).astype(bool)
                IGN_COL_MASK[self._ignore_columns.astype(np.uint32)] = True
                NEW_IGN_COL = np.arange(sum(COLUMN_KEEP_MASK))[
                                        IGN_COL_MASK[COLUMN_KEEP_MASK]
                ]
                del IGN_COL_MASK

                # do not pass the function!
                HDL_AS_BOOL_MASK = np.zeros(self.n_features_in_).astype(bool)
                HDL_AS_BOOL_MASK[self._handle_as_bool.astype(np.uint32)] = True
                NEW_HDL_AS_BOOL_COL = np.arange(sum(COLUMN_KEEP_MASK))[
                                        HDL_AS_BOOL_MASK[COLUMN_KEEP_MASK]]
                del HDL_AS_BOOL_MASK

                if isinstance(self.count_threshold, numbers.Integral):
                    NEW_COUNT_THRESHOLD = self.count_threshold
                else:
                    NEW_COUNT_THRESHOLD = self.count_threshold[COLUMN_KEEP_MASK]

                # END RE-ALIGN _ic, _hab, count_threshold ** * ** * ** *

                RecursiveCls = MinCountTransformer(
                    NEW_COUNT_THRESHOLD,
                    ignore_float_columns=self.ignore_float_columns,
                    ignore_non_binary_integer_columns=
                        self.ignore_non_binary_integer_columns,
                    ignore_columns=NEW_IGN_COL,
                    ignore_nan=self.ignore_nan,
                    handle_as_bool=NEW_HDL_AS_BOOL_COL,
                    delete_axis_0=self.delete_axis_0,
                    max_recursions=self.max_recursions-1
                )

                del NEW_IGN_COL, NEW_HDL_AS_BOOL_COL, NEW_COUNT_THRESHOLD

                if y_tr is None:
                    X_tr = RecursiveCls.fit_transform(X_tr, y_tr)
                else:
                    X_tr, y_tr = RecursiveCls.fit_transform(X_tr, y_tr)

                # vvv tcbc update vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
                MAP_DICT = dict((
                    zip(
                        list(range(RecursiveCls.n_features_in_)),
                        sorted(list(map(int, self.get_support(indices=True))))
                    )
                ))

                self._total_counts_by_column = \
                    _tcbc_update(
                        self._total_counts_by_column,
                        RecursiveCls._total_counts_by_column,
                        MAP_DICT
                )
                # ^^^ tcbc update ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

                self._row_support[self._row_support] = RecursiveCls._row_support

                del RecursiveCls, MAP_DICT

            del ROW_KEEP_MASK, COLUMN_KEEP_MASK


        if hasattr(X_tr, 'toarray'):
            X_tr = _og_dtype(X_tr)
            del _og_dtype
        elif isinstance(X_tr, np.ndarray):
            X_tr = np.ascontiguousarray(X_tr)

        if y_tr is None:
            return X_tr
        else:
            return X_tr, y_tr


    def _make_instructions(self) -> InstructionsType:
        """Make the instructions dictionary for the current uniques and
        counts stored in the instance and the current settings of the
        parameters.

        Returns
        -------
        _instr : InstructionType
            The instructions for the counts learned during training and
            the current MCT parameter configuration.

        """

        check_is_fitted(self)

        return _make_instructions(
            self.count_threshold,
            self.ignore_float_columns,
            self.ignore_non_binary_integer_columns,
            self._ignore_columns,
            self.ignore_nan,
            self._handle_as_bool,
            self.delete_axis_0,
            self._original_dtypes,
            self.n_features_in_,
            getattr(self, 'feature_names_in_', None),
            self._total_counts_by_column
        )


    def _recursion_check(self) -> None:
        """Raise exception if attempting to use recursion with `fit`,
        `partial_fit`, and `transform`. Only allow `fit_transform`.

        Returns
        -------
        None

        """


        if getattr(self, 'recursion_check_disable', False) is False:

            if self.max_recursions > 1:
                raise ValueError(
                    f"partial_fit(), fit(), and transform() are not "
                    f"available if max_recursions > 1. fit_transform() "
                    f"only."
                )




