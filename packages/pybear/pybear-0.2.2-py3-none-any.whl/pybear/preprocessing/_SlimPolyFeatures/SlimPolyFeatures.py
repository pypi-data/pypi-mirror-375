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
    PolyDuplicatesType,
    PolyConstantsType,
    KeptPolyDuplicatesType,
    DroppedPolyDuplicatesType,
    CombinationsType,
    FeatureNamesInType,
    FeatureNameCombinerType
)
from ..__shared._type_aliases import XContainer

import numbers
import uuid
import warnings

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from ._validation._validation import _validation
from ._attributes._build_kept_poly_duplicates import \
    _build_kept_poly_duplicates
from ._attributes._build_dropped_poly_duplicates import \
    _build_dropped_poly_duplicates
from ._get_feature_names_out._gfno_poly import _gfno_poly
from ._partial_fit._combination_builder import _combination_builder
from ._partial_fit._columns_getter import _columns_getter
from ._partial_fit._deconstant_poly_dupls import _deconstant_poly_dupls
from ._partial_fit._is_constant import _is_constant
from ._partial_fit._get_dupls_for_combo_in_X_and_poly import \
    _get_dupls_for_combo_in_X_and_poly
from ._partial_fit._merge_constants import _merge_constants
from ._partial_fit._merge_partialfit_dupls import _merge_partialfit_dupls
from ._partial_fit._lock_in_random_combos import _lock_in_random_combos
from ._shared._identify_combos_to_keep import _identify_combos_to_keep
from ._shared._get_active_combos import _get_active_combos
from ._shared._check_X_constants_dupls import _check_X_constants_dupls
from ._transform._build_poly import _build_poly

from ...preprocessing._InterceptManager.InterceptManager import \
    InterceptManager as IM
from ...preprocessing._ColumnDeduplicator. \
    ColumnDeduplicator import ColumnDeduplicator as CDT

from ...base import (
    FeatureMixin,
    FitTransformMixin,
    GetParamsMixin,
    ReprMixin,
    SetOutputMixin,
    SetParamsMixin,
    validate_data
)

from ...base import (
    is_fitted,
    check_is_fitted,
    get_feature_names_out
)
from ...utilities._nan_masking import nan_mask
from ...utilities._union_find import union_find



class SlimPolyFeatures(
    FeatureMixin,
    GetParamsMixin,
    SetOutputMixin,
    SetParamsMixin,
    FitTransformMixin,
    ReprMixin
):
    """`SlimPolyFeatures` (SPF) performs a polynomial feature expansion
    on a dataset, where any feature produced that is a column of constants
    or is a duplicate of another column is omitted from the final output.

    SPF follows the standard scikit-learn transformer API, and makes the
    standard transformer methods available: `get_feature_names_out`,
    `fit`, `partial_fit`, `transform`, `fit_transform`, `set_params`,
    and `get_params`. SPF also has a `reset` method which is covered
    elsewhere in the docs.

    Numpy arrays, pandas dataframes, polars dataframes, and all scipy
    sparse objects (csr, csc, coo, lil, dia, dok, and bsr matrices
    and arrays) are accepted by :meth:`partial_fit`, :meth:`fit`,
    and :meth:`transform`. SPF only accepts numerical data, and will
    raise an exception if passed non-numerical values.

    SPF requires that data passed to it have no duplicate and no constant
    columns. This stipulation is explained in more detail later in
    the docs. If you are expanding non-binary integer or float data
    under this condition, there is low (but non-zero) likelihood that
    polynomial terms will be constant or duplicate. Therefore, SPF has
    the least utility for that type of data, and the user may be better
    off using scikit PolynomialFeatures, which has much lower cost of
    operation than SPF. SPF is of greatest benefit when it is used to
    perform polynomial expansion on one-hot encoded data, where there
    is high likelihood that polynomial terms are constant (all zeros)
    or duplicate.

    A polynomial feature expansion generates all possible multiplicative
    combinations of the original features, typically from the zero-degree
    term up to and including a specified maximum degree. For example, if
    a dataset has two features, called 'a' and 'b', then the degree-2
    polynomial expansion is [1, a, b, a^2, ab, b^2], where the column of
    ones is the zero-degree term, columns 'a' and 'b' are the first
    degree terms, and columns a^2, ab, and b^2 are the second degree
    terms. Generating these features for analysis is useful for finding
    non-linear relationships between the data and the target.

    A conventional workflow would be to perform a polynomial expansion
    (that fits in memory) on data, remove duplicate and constant columns,
    and perform an analysis. The memory occupied by the columns that were
    eventually removed may have prevented us from doing a higher order
    expansion, which may have provided useful information. Unfortunately,
    even low-degree polynomial expansions of modest-sized datasets
    quickly grow to consume large amounts, or maybe even all, available
    RAM. This limits the number of polynomial terms that can be analyzed.

    But there is opportunity to reduce memory footprint for a given
    expansion by not generating features that do not add value. Many
    polynomial expansions generate columns that are duplicate or
    constant (think columns of all zeros from interactions of a one-hot
    encoded feature). SPF finds columns such as these before the data
    is fully expanded and prevents them from ever appearing in the
    final array and occupying memory. This affords the opportunity to
    (possibly) work with more data and do higher order expansions than
    otherwise possible because the non-value-added columns are never even
    created. SPF also saves the time of manually finding and removing
    such columns after the expansion.

    To robustly and tractably do this, SPF requires that the dataset to
    undergo expansion has no duplicate or constant columns. There is
    further discussion in these documents about how SPF handles these
    conditions in-situ during multiple partial fits, but ultimately
    SPF requires that the totality of seen data has no constants and no
    duplicates. When `scan_X` is True, SPF is able to find any columns
    in the original data that are constant/duplicate and prevent
    transform until the condition is fixed; it could only be fixed
    in-situ with more partial fits. To properly pre-condition your
    data beforehand, remove constant columns from your data with
    pybear :class:`InterceptManager`, and remove duplicate columns from
    your data with pybear :class:`ColumnDeduplicator`. If there are no
    constant or duplicate columns in the data, setting `scan_X` to False
    can reduce the cost of the polynomial expansion. See more discussion
    in the `scan_X` parameter.

    During the fitting process, SPF learns what columns in the expansion
    would be constant and/or duplicate. SPF does the expansion out
    brute force, which can be expensive. Even with all that work, this
    preliminary expansion is not directly returned as a result at
    transform time. At transform, the polynomial expansion is built
    based on what was learned about constant and duplicate columns
    during the building of the preliminary expansion.

    At transform time, SPF applies the rules it learned during fitting
    and only builds the polynomial features that could add value to the
    dataset. The internal construction of the polynomial expansion is
    always as a scipy sparse csc array to minimize the RAM footprint
    of the expansion. The expansion is also always done with float64
    datatypes, regardless of datatype of the passed data, to prevent any
    overflow problems that might arise from multiplication of low bit
    number types. However, overflow is still possible with 64 bit
    datatypes, especially when the data has large values or the degree
    of the expansion is high. SPF HAS NO PROTECTIONS FOR OVERFLOW. IT IS
    UP TO THE USER TO AVOID OVERFLOW CONDITIONS AND VERIFY RESULTS.

    Even though `transform` always constructs the expansion as scipy
    sparse csc, SPF will return the expansion in the format of the data
    passed to `transform`, unless instructed otherwise. If dense data
    is passed to `transform`, this negates the memory savings from
    building as sparse csc because the sparse format will be converted
    to the dense format for return. SPF can be instructed to return
    the output in sparse format via the `sparse_output` parameter, which
    preserves the lower memory footprint of the internal expansion. If
    `sparse_output` is set to True, the expansion is returned as scipy
    sparse csr array. If `sparse_output` is set to False, then SPF will
    convert the polynomial expansion from a sparse csc array to the same
    format passed to `transform`.

    The SPF `partial_fit` method allows for incremental fitting. Through
    this method, even if the data is bigger-than-memory, SPF is able to
    learn what columns in `X` are constant/duplicate and what columns in
    the expansion are constant/duplicate, and carry out instructions to
    build the expansion batch-wise. This makes SPF amenable to batch-wise
    fitting and transforming via dask_ml Incremental and ParallelPostFit
    wrappers.

    SPF takes parameters to set the minimum (`min_degree`) and maximum
    (`degree`) degrees of the polynomial terms produced during the
    expansion. The edge case of returning only the 0-degree column of
    ones is disallowed. SPF never returns the 0-degree column of ones
    under any circumstance. The lowest degree SPF ever returns is degree
    one (the original data in addition to whatever other order terms are
    required). SPF terminates if `min_degree` is set to zero (minimum
    allowed setting is 1). To append a zero-degree column to your data,
    use pybear `InterceptManager` after using SPF. Also, SPF does not
    allow the no-op case of `degree` = 1, where the original data would
    be returned unchanged without any polyomial features. The minimum
    setting for `degree` is 2.

    When searching for constant and duplicate columns, SPF ONLY LOOKS IN
    WHAT IS TO BE RETURNED. That is, if you specify `min_degree` to be
    1, then SPF will compare the created polynomial terms against the
    original data and themselves. If you specify `min_degree` to be 2 or
    greater, SPF will only compare the created polynomial terms against
    themselves. The ramifications of the latter case is that if you were
    to merge your original data onto the SPF output, there may be
    duplicates.

    During fitting, SPF is able to tolerate constants and duplicates in
    the passed data. While this condition exists, however, SPF remains
    in a state where it waits for further partial fits to remedy the
    situation and does no-ops with warnings on most other actions (such
    as calls to attributes, `transform`, amongst others.) Only when the
    internal state of SPF is satisfied that there are no constant or
    duplicate columns in the training data will SPF allow access to the
    other functionality.

    SPF MUST ONLY TRANSFORM DATA IT HAS BEEN FITTED ON. TRANSFORMATION
    OF ANY OTHER DATA WILL PRODUCE OUTPUT THAT MAY CONTAIN CONSTANTS,
    DUPLICATES, AND NONSENSICAL RESULTS.

    SPF has 5 property attributes that are accessible at any point after
    fitting. They can only be accessed if there are no constants or
    duplicates in the training data, otherwise attempts to access them
    will result in a no-op that gives a warning and returns None.

    Once SPF is fit, setting of most params via :meth:`set_params` is
    blocked. This is to prevent SPF from failing because of new learning
    states that cannot be reconciled with earlier learning states. The
    only parameters that can be set after a fit are `keep`, `n_jobs`,
    `job_size`, `sparse_output`, and `feature_name_combiner`. SPF has
    a :meth:`reset` method that resets the data-dependent state of SPF.
    This allows for re-initializing the instance and setting different
    learning parameters without forcing the user to create a new instance.

    Parameters
    ----------
    degree : int, default = 2
        The maximum polynomial degree of the generated features. The
        minimum value accepted by SPF is 2; the no-op case of simply
        returning the original degree-one data is not allowed.
    min_degree : int, default = 1
        The minimum polynomial degree of the generated features.
        Polynomial terms with degree below `min_degree` are not included
        in the final output array. The minimum value accepted by SPF is
        1; SPF cannot be used to generate a zero-degree column (a column
        of all ones).
    interaction_only : bool, default = False
        If True, only interaction features are produced, that is,
        polynomial features that are products of 'degree' distinct input
        features. Terms with power of 2 or higher for any feature are
        excluded. If False, produce the full polynomial expansion.

        Consider 3 features 'a', 'b', and 'c'. If `interaction_only` is
        True, `min_degree` is 1, and `degree` is 2, then only the first
        degree interaction terms ['a', 'b', 'c'] and the second degree
        interaction terms ['ab', 'ac', 'bc'] are returned in the
        polynomial expansion.
    scan_X : bool, default = True
        SPF requires that the data being fit has no columns of constants
        and no duplicate columns. When `scan_X` is True, SPF does not
        assume that the analyst knows these states of the data and
        diagnoses them during fitting, which can be very expensive to do,
        especially finding duplicate columns. If the analyst knows that
        there are no constant or duplicate columns in the data, setting
        this to False can greatly reduce the cost of the polynomial
        expansion. When in doubt, pybear recommends setting this to True
        (the default). When this is False, it is possible to pass columns
        of constants or duplicates, but SPF will continue to operate
        under the assumptions of the stated design requirement, and the
        output will be nonsensical.
    keep : Literal['first', 'last', 'random'], default = 'first'
        The strategy for keeping a single representative from a set of
        identical columns in the polynomial expansion. This is overruled
        if a polynomial feature is a duplicate of one of the original
        features, as the original feature will always be kept and the
        polynomial duplicates will always be dropped. One of SPF's
        design rules is to never alter the originally passed data, so
        the original feature will always be kept. Under SPF's design rule
        that the original data has no duplicate columns, an expansion
        feature cannot be identical to 2 of the original features. In
        all cases where the duplicates are only within the polynomial
        expansion, 'first' retains the column left-most in the expansion
        (lowest degree); 'last' keeps the column right-most in the
        expansion (highest degree); 'random' keeps a single randomly
        selected feature of the set of duplicates.
    sparse_output : bool, default = True
        If set to True, the polynomial expansion is returned from
        `transform` as a scipy sparse csr array. If set to False, the
        polynomial expansion is returned in the same format as passed
        to `transform`.
    feature_name_combiner : FeatureNameCombinerType, default = 'as_indices'
        Sets the naming convention for the created polynomial features.
        This does not set nor change any original feature names that may
        have been seen during fitting on containers that have a header.

        `feature_name_combiner` must be literal 'as_feature_names',
        literal 'as_indices', or a user-defined function (callable) for
        mapping polynomial column index combination tuples to polynomial
        feature names.

        If literal 'as_feature_names' is used, SPF generates new
        polynomial feature names based on the feature names in the
        original data. For example, if the feature names of X are
        ['x0', 'x1', ..., 'xn'] and the polynomial column index
        tuple is (1, 1, 3), then the polynomial feature name is
        'x1^2_x3'.

        If the default literal 'as_indices' is used, SPF generates new
        polynomial feature names based on the polynomial column index
        tuple itself. For example, if the polynomial column index tuple
        is (2, 2, 4), then the polynomial feature name is '(2, 2, 4)'.

        If a user-defined callable is passed, it must:

            1) Accept 2 arguments
                a) a 1D vector of strings that contains the original feature
                    names of X, as is used internally in SPF,
                b) the polynomial column combination tuple, which is a tuple
                    of integers of variable length. The minimum length of
                    the tuple must be `min_degree`, and the maximum length
                    must be `degree`, with each integer falling in the range
                    of [0, `n_features_in_`-1]
            2) Return a string that
                a) is not a duplicate of any originally seen feature name
                b) is not a duplicate of any other polynomial feature name
    equal_nan : bool, default = True

        When comparing two columns for equality:

        If `equal_nan` is True, assume that a nan value would otherwise
        be the same as the compared non-nan counterpart, or if both
        compared values are nan, consider them as equal (contrary to the
        default numpy handling of nan, where numpy.nan != numpy.nan).
        If `equal_nan` is False and either one or both of the values in
        the compared pair of values is/are nan, consider the pair to be
        not equivalent, thus making the column pair not equal. This is
        in line with the normal numpy handling of nan values.

        When assessing if a column is constant:

        If `equal_nan` is True, assume any nan values equal the mean of
        all non-nan values in the respective column. If `equal_nan` is
        False, any nan-values could never take the value of the mean of
        the non-nan values in the column, making the column not constant.
    rtol : numbers.Real, default = 1e-5
        The relative difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    atol : numbers.Real, default = 1e-8
        The absolute difference tolerance for equality. Must be a
        non-boolean, non-negative, real number. See numpy.allclose.
    n_jobs : int | None, default=None
        The number of joblib parallel jobs to use when looking for
        duplicate columns. The default is to use processes, but can be
        overridden externally using a joblib `parallel_config` context
        manager. The default number of jobs is None, which uses the
        joblib default setting. To get maximum speed benefit, pybear
        recommends using -1, which means use all processors.
    job_size : int, default=50
        The number of columns to send to a joblib job. Must be an integer
        greater than or equal to 2. This allows the user to optimize
        CPU utilization for their particular circumstance. Long, thin
        datasets should use fewer columns, and wide, flat datasets should
        use more columns. Bear in mind that the columns sent to joblib
        jobs are deep copies of the original data, and larger job sizes
        increase RAM usage. Note that joblib is only engaged in scanning
        the original data when the number of columns in the data is at
        least 2*job_size. Also, joblib is only engaged in scanning the
        polynomial expansion if the number of columns in it is at least
        2*job_size. For example, if `job_size` is 10, data with 20 or
        more columns will be processed with joblib, data with 19 or
        fewer columns will be processed linearly.

    Attributes
    ----------
    n_features_in_ : int
        The number of features in the fitted data, i.e., number of
        features before expansion.
    feature_names_in_ : numpy.ndarray[object]
        The names of the features as seen during fitting. Only accessible
        if `X` is passed to :meth:`partial_fit` or :meth:`fit` in a
        container that has a header.
    poly_combinations_
    poly_constants_
    poly_duplicates_
    dropped_poly_duplicates_
    kept_poly_duplicates_

    Notes
    -----
    Concerning the handling of nan-like representations. SPF accepts
    data in the form of numpy arrays, pandas dataframes, polars
    dataframes, and scipy sparse matrices/arrays. Regardless of the
    format of the passed data, during the construction of the preliminary
    (learning) expansion and during transform columns are extracted from
    the data as a numpy array with float64 dtype (see below for more
    detail about how scipy sparse is handled.) After the conversion to
    numpy array and prior to calculating the products of the columns in
    the extraction, SPF identifies any nan-like representations in the
    extracted numpy array and standardizes all of them to numpy.nan.
    The user is advised that whatever is used to indicate 'not-a-number'
    in the original data must first survive the conversion to numpy
    array and then be recognized by SPF as nan-like, so that SPF can
    standardize it to numpy.nan. nan-like representations that are
    recognized by SPF include, at least, numpy.nan, pandas.NA, None (of
    type None, not string 'None'), and string representations of 'nan'
    (not case sensitive).

    Concerning the handling of infinity. SPF has no special handling for
    the various infinity-types, e.g, numpy.inf, -numpy.inf, float('inf'),
    float('-inf'), etc. This is a design decision to not force infinity
    values to numpy.nan. SPF falls back to the native handling of these
    values for Python and numpy. Specifically, numpy.inf==numpy.inf and
    float('inf')==float('inf').

    Concerning the handling of scipy sparse arrays. When constructing
    the preliminary (learning) expansion and during transform, the
    columns extracted from the data are converted to dense numpy
    arrays via the 'toarray' method, then undergo multiplication.
    This a compromise that causes some memory expansion but allows
    for efficient handling of polynomial calculations.

    **Type Aliases**

    XContainer:
        numpy.ndarray | pandas.DataFrame | polars.DataFrame
        | ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
        | ss._dia.dia_matrix | ss._lil.lil_matrix | ss._dok.dok_matrix
        | ss._bsr.bsr_matrix | ss._csr.csr_array | ss._csc.csc_array
        | ss._coo.coo_array | ss._dia.dia_array | ss._lil.lil_array
        | ss._dok.dok_array | ss._bsr.bsr_array

    FeatureNameCombinerType:
        Callable[[Sequence[str], tuple[int, ...]], str],
        | Literal['as_feature_names', 'as_indices']

    CombinationsType:
        tuple[tuple[int, ...], ...]

    PolyDuplicatesType:
        list[list[tuple[int, ...]]]

    KeptPolyDuplicatesType:
        dict[tuple[int, ...], list[tuple[int, ...]]]

    DroppedPolyDuplicatesType:
        dict[tuple[int, ...], tuple[int, ...]]

    PolyConstantsType:
        dict[tuple[int, ...], Any]

    FeatureNamesInType:
        numpy.ndarray[object]

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
    >>> from pybear.preprocessing import SlimPolyFeatures as SPF
    >>> import numpy as np
    >>> trf = SPF(
    ...     degree=2, min_degree=1, interaction_only=False,
    ...     sparse_output=False, feature_name_combiner='as_indices'
    ... )
    >>> X = np.array([[0,1],[0,1],[1,1],[1,0]], dtype=np.uint8)
    >>> out = trf.fit_transform(X)
    >>> out
    array([[0., 1., 0.],
           [0., 1., 0.],
           [1., 1., 1.],
           [1., 0., 0.]])
    >>> trf.n_features_in_
    2
    >>> trf.poly_combinations_
    ((0, 1),)
    >>> trf.poly_constants_
    {}
    >>> trf.poly_duplicates_
    [[(0,), (0, 0)], [(1,), (1, 1)]]
    >>> trf.kept_poly_duplicates_
    {(0,): [(0, 0)], (1,): [(1, 1)]}
    >>> trf.dropped_poly_duplicates_
    {(0, 0): (0,), (1, 1): (1,)}
    >>> trf.get_feature_names_out()
    array(['x0', 'x1', '(0, 1)'], dtype=object)

    """


    def __init__(
        self,
        degree:int = 2,
        *,
        min_degree:int = 1,
        interaction_only:bool = False,
        scan_X:bool = True,
        keep:Literal['first', 'last', 'random'] = 'first',
        sparse_output:bool = True,
        feature_name_combiner:FeatureNameCombinerType = 'as_indices',
        equal_nan:bool = True,
        rtol:numbers.Real = 1e-5,
        atol:numbers.Real = 1e-8,
        n_jobs:int | None = None,
        job_size:int = 50
    ) -> None:
        """Initialize the SlimPolyFeatures instance."""

        self.degree = degree
        self.min_degree = min_degree
        self.interaction_only = interaction_only
        self.scan_X = scan_X
        self.keep = keep
        self.sparse_output = sparse_output
        self.feature_name_combiner = feature_name_combiner
        self.equal_nan = equal_nan
        self.rtol = rtol
        self.atol = atol
        self.n_jobs = n_jobs
        self.job_size = job_size


    def __pybear_is_fitted__(self) -> bool:
        return hasattr(self, '_poly_duplicates')


    def _check_X_constants_and_dupls(self) -> None:
        """Check X for constant and duplicate columns.

        When `scan_X` is True, SPF uses pybear `InterceptManager`
        and pybear `ColumnDeduplicator` to scan X for constants and
        duplicates. If any are found, this method will raise an
        exception.

        Returns
        -------
        None

        """

        if self.scan_X and hasattr(self, '_IM') and hasattr(self, '_CDT'):
            # if X was scanned for constants and dupls, raise if any
            # were present.
            _check_X_constants_dupls(
                self._IM.constant_columns_,
                self._CDT.duplicates_
            )


    def _attr_access_warning(self) -> str:
        """Warning message for when duplicates and/or constants are found
        in X.

        Returns
        -------
        warning_message : str
            Warning message for when duplicates and/or constants are
            found in X.

        """

        return (
            f"there are duplicate and/or constant columns in the data. "
            f"\nthe attribute / method you have requested cannot be "
            f"returned because it is not accurate when the data has "
            f"duplicate or constant columns. \nthis warning is raised "
            f"and the program not terminated to allow for more partial "
            f"fits."
        )


    # properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    @property
    def poly_combinations_(self) -> CombinationsType | None:
        """Get the `poly_combinations_` attribute.

        The polynomial column combinations from `X` that are in the
        polynomial expansion part of the final output. An example might
        be ((0,0), (0,1), ...), where each tuple holds the column
        indices from `X` that are multiplied to produce a feature in the
        polynomial expansion. This matches one-to-one with the created
        features, and similarly does not have any combinations that are
        excluded from the polynomial expansion for being duplicate or
        constant.

        Returns
        -------
        poly_combinations_ : CombinationsType | None
            The polynomial column combinations from `X` that are in the
            polynomial expansion part of the final output.

        """

        check_is_fitted(self)

        try:
            self._check_X_constants_and_dupls()
            # self._active_combos must be sorted asc degree,
            # then asc on idxs. if _combos is sorted
            # then this is sorted correctly at construction.
            return self._active_combos
        except:
            warnings.warn(self._attr_access_warning())
            return


    @property
    def poly_duplicates_(self) -> PolyDuplicatesType | None:

        # in-process _poly_duplicates may have constants if they are
        # also duplicate because they need to be tracked until the final
        # partial fit in case at some they become no longer constant but
        # are still duplicate, but the external API poly_duplicates_
        # cannot have the constants in it. the builder functions at the
        # end of partial_fit() and transform() must use this version of
        # poly_duplicates_. the internal _poly_duplicates must always
        # have constants in it (if applicable) and must be used for all
        # other internal operations.

        """Get the `poly_duplicates_` attribute.

        A list of the groups of identical polynomial features, indicated
        by tuples of their zero-based column index positions in the
        originally fit data. Columns from the original data itself can
        be in a group of duplicates, along with any duplicates from the
        polynomial expansion. For example, `poly_duplicates_` for some
        dataset might look like:
        [[(1,), (2,3), (2,4)], [(5,6), (5,7), (6,7)]]

        Returns
        -------
        poly_duplicates_ : PolyDuplicatesType | None
            The groups of identical polynomial features.

        """

        check_is_fitted(self)

        try:
            self._check_X_constants_and_dupls()

            return _deconstant_poly_dupls(
                _poly_duplicates=self._poly_duplicates,
                _poly_constants=self._poly_constants
            )
        except:
            warnings.warn(self._attr_access_warning())

            return


    @property
    def kept_poly_duplicates_(self) -> KeptPolyDuplicatesType | None:
        """Get the `kept_poly_duplicates_` attribute.

        A dictionary whose keys are tuples of the indices of the columns
        of `X` that produced a polynomial column that was kept from the
        sets of duplicates. The dictionary values are lists of the tuples
        of indices that created polynomial columns that were duplicate
        of the column indicated by the dictionary key, but were removed
        from the polynomial expansion.

        Returns
        -------
        kept_poly_duplicates_ : KeptPolyDuplicatesType | None
            A dictionary whose keys are the columns that were kept out
            of the sets of duplicates and the values are lists of the
            columns that were duplicates of the respective key.

        """

        check_is_fitted(self)

        try:
            self._check_X_constants_and_dupls()

            # must use poly_duplicates_ here not _poly_duplicates
            return _build_kept_poly_duplicates(
                    self.poly_duplicates_,
                    self._kept_combos
                )
        except:
            warnings.warn(self._attr_access_warning())
            return


    @property
    def dropped_poly_duplicates_(self) -> DroppedPolyDuplicatesType | None:
        """Get the `dropped_poly_duplicates_` attribute.

        A dictionary whose keys are the tuples that are removed from the
        polynomial expansion because they produced a duplicate of another
        column. The values of the dictionary are the tuples of indices
        of the respective duplicate that was kept.

        Returns
        -------
        dropped_poly_duplicates_ : DroppedPolyDuplicatesType | None
            keys: the poly combinations that were dropped from the
            expansion; values: the respective duplicate that was kept.

        """

        check_is_fitted(self)

        try:

            self._check_X_constants_and_dupls()

            # must use poly_duplicates_ here not _poly_duplicates
            return _build_dropped_poly_duplicates(
                    self.poly_duplicates_,
                    self._kept_combos
                )

        except:
            warnings.warn(self._attr_access_warning())
            return


    @property
    def poly_constants_(self) -> PolyConstantsType | None:
        """Get the `poly_constants_` attribute.

        A dictionary whose keys are tuples of indices in the original
        data that produced a column of constants in the polynomial
        expansion. The dictionary values are the constant values in
        those columns. For example, if an expansion has a constant
        column that was produced by multiplying the second and third
        columns in `X` (index positions 1 and 2, respectively) and the
        constant value is 0, then `constant_columns_` will be {(1,2): 0}.
        If there are no constant columns, then `constant_columns_` is an
        empty dictionary. These are always excluded from the polynomial
        expansion.

        Returns
        -------
        poly_constants_ : PolyConstantsType | None
            keys: the poly combinations that produced a column of
            constants; values: the constant value for that poly feature.
            These are always omitted from the final expansion.

        """

        check_is_fitted(self)

        try:
            self._check_X_constants_and_dupls()

            return self._poly_constants
        except:
            warnings.warn(self._attr_access_warning())
            return
    # END properties v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def reset(self) -> Self:
        """Reset the internal data-dependent state of SPF.

        __init__ parameters are not changed. reset is part of the
        external API because setting most params after a partial fit
        is  blocked, and this allows for re-initializing the instance
        without forcing the user to create a new instance.

        Returns
        -------
        self : object
            The `SlimPolyFeatures` instance.

        """

        if hasattr(self, "_poly_duplicates"):
            delattr(self, '_poly_duplicates')

        if hasattr(self, '_poly_constants'):
            delattr(self, '_poly_constants')

        if hasattr(self, '_combos'):
            delattr(self, '_combos')

        if hasattr(self, 'n_features_in_'):
            delattr(self, 'n_features_in_')

        if hasattr(self, 'feature_names_in_'):
            delattr(self, 'feature_names_in_')

        # _rand_combos, _kept_combos, and _active_combos may not exist
        # even if _poly_duplicates exists because
        # partial_fit short circuits before making them if there
        # are dupls/constants in X.
        if hasattr(self, '_rand_combos'):
            delattr(self, '_rand_combos')
            delattr(self, '_kept_combos')
            delattr(self, '_active_combos')

        if hasattr(self, '_IM'):
            del self._IM

        if hasattr(self, '_CDT'):
            del self._CDT

        return self


    def get_feature_names_out(
        self,
        input_features:Sequence[str] | None = None
    ) -> FeatureNamesInType:
        """Get the feature names for the output of `transform`.

        Use `input_features` and `feature_name_combiner` to build the
        feature names for the polynomial component of the transformed
        data.

        Parameters
        ----------
        input_features : Sequence[str] | None, default = None
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
        # pybear.base.FeatureMixin, but since this transformer adds columns,
        # must build a one-off.

        check_is_fitted(self)

        try:
            self._check_X_constants_and_dupls()
        except:
            warnings.warn(self._attr_access_warning())
            return

        # if did not except....
        _X_header: npt.NDArray[object] = get_feature_names_out(
            input_features,
            getattr(self, 'feature_names_in_', None),
            self.n_features_in_
        )

        # _X_header must exist as an actual header, and not None. if
        # self.features_names_in_ is None, the default boilerplate
        # feature names should have been generated for _X_header.
        assert _X_header is not None

        # there must be a poly header, self.degree must be >= 2
        feature_names_out: npt.NDArray[object] = _gfno_poly(
            _X_header,
            self._active_combos,
            self.feature_name_combiner
        )

        if self.min_degree == 1:
            feature_names_out = \
                np.hstack((_X_header, feature_names_out)).astype(object)
        # else poly header is returned as is

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
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Incrementally train the SPF transformer instance on one or
        more batches of data.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data to undergo polynomial expansion.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `SlimPolyFeatures` instance.

        """


        X = validate_data(
            X,
            copy_X=False,
            cast_to_ndarray=False,
            accept_sparse=("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
            dtype='numeric',
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
            X,
            self.degree,
            self.min_degree,
            self.scan_X,
            self.keep,
            self.interaction_only,
            self.sparse_output,
            self.feature_name_combiner,
            self.rtol,
            self.atol,
            self.equal_nan,
            self.n_jobs,
            self.job_size
        )

        # do not make an assignment! let the function handle it.
        self._check_n_features(
            X,
            reset=not hasattr(self, "_poly_duplicates")
        )

        # do not make an assignment! let the function handle it.
        self._check_feature_names(
            X,
            reset=not hasattr(self, "_poly_duplicates")
        )
        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # _validation should have caught non-numeric X.
        # X must only be numeric throughout all of SPF.

        # ss sparse that cant be sliced
        # avoid copies of X, do not mutate X. if X is coo, dia, bsr, it
        # cannot be sliced. must convert to another ss. so just convert
        # all of them to csc for faster column slicing. need to change
        # it back later.
        if hasattr(X, 'toarray'):
            _og_dtype = type(X)
            X = X.tocsc()

        # these both must be None on the first pass!
        # on subsequent passes, the holders may not be empty.
        if not hasattr(self, '_poly_duplicates'):
            self._poly_duplicates: PolyDuplicatesType | None = None
        if not hasattr(self, '_poly_constants'):
            self._poly_constants: PolyConstantsType | None = None

        # Identify constants & duplicates in X v^v^v^v^v^v^v^v^v^v^v^v^v
        # This is to know if we reject X for having constant or
        # duplicate columns.
        if self.scan_X:

            if not hasattr(self, '_IM'):
                self._IM = IM(
                    keep=self.keep,
                    equal_nan=self.equal_nan,
                    rtol=self.rtol,
                    atol=self.atol
                )

            if not hasattr(self, '_CDT'):
                self._CDT = CDT(
                    keep=self.keep,
                    do_not_drop=None,
                    conflict='ignore',
                    equal_nan=self.equal_nan,
                    rtol=self.rtol,
                    atol=self.atol,
                    n_jobs=self.n_jobs
                    # leave job_size at CDT default
                )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._IM.partial_fit(X)
                self._CDT.partial_fit(X)

            try:
                self._check_X_constants_and_dupls()
            except:
                warnings.warn(
                    f"There are duplicate and/or constant columns in X."
                )
        # END Identify constants & duplicates in X v^v^v^v^v^v^v^v^v^v^v


        _poly_dupls_current_partial_fit: list[list[tuple[int, ...]]] = []
        _poly_constants_current_partial_fit: dict[tuple[int, ...], Any] = {}

        # GENERATE COMBINATIONS # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # get the permutations to run, based on the size of x,
        # min degree, max degree, and interaction_only.
        self._combos: list[tuple[int, ...]] = _combination_builder(
            n_features_in_=self.n_features_in_,
            _min_degree=self.min_degree,
            _max_degree=self.degree,
            _intx_only=self.interaction_only
        )

        # _combo must always be at least degree 2, degree 1 is
        # just the original data and should not be processed here
        assert min(map(len, self._combos)) >= 2
        # END GENERATE COMBINATIONS # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # poly constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        # iterate over the combos to find what is constant
        if self._poly_constants and len(self._poly_constants) == 0:
            pass
            # if _poly_constants (the place that holds what poly columns
            # are constants across all partial fits) exists and it is
            # empty, then there cannot possibly be any columns of constants
            # going forward, so dont even expend the energy to check.
        else:
            for _combo in self._combos:
                _poly_is_constant: uuid.UUID | Any = \
                    _is_constant(
                        _column=_columns_getter(X, _combo).ravel(),
                        _equal_nan=self.equal_nan,
                        _rtol=self.rtol,
                        _atol=self.atol
                    )

                if not isinstance(_poly_is_constant, uuid.UUID):
                    _poly_constants_current_partial_fit[_combo] = _poly_is_constant
        # END poly constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # constant columns - NEED TO KNOW IF they are also a member of
        # duplicates because even though they are constants now, they
        # might not be after more partial fits, but they still might be
        # duplicates.

        # poly duplicates v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        # iterate over the combos and find what is duplicate.
        # this function scans the combos columns across the columns in X
        # and themselves looking for dupls. it returns a vector of tuples
        # with each tuple being a pair of tuples that hold the column
        # indices of X that produced them.
        _dupl_pairs: list[tuple[tuple[int,...], tuple[int, ...]]] = \
            _get_dupls_for_combo_in_X_and_poly(
                X,
                self._combos,
                _min_degree=self.min_degree,
                _equal_nan=self.equal_nan,
                _rtol=self.rtol,
                _atol=self.atol,
                _n_jobs=self.n_jobs,
                _job_size=self.job_size
            )

        # use union-find to unite the pairs in _dupl_pairs into contiguous
        # groups of identical columns
        _poly_dupls_current_partial_fit:list[list[tuple[int, ...]]] = \
            list(map(list, union_find(_dupl_pairs)))

        # all scipy sparse were converted to csc near the top of this
        # method. change it back to original state. do not mutate X!
        if hasattr(X, 'toarray'):
            X = _og_dtype(X)
            del _og_dtype

        # what do we have at this point?
        # the original X
        # X constants in _IM()
        # X duplicates in _CDT()
        # _combos
        # _poly_constants for all fits
        # _poly_duplicates for all fits
        # _poly_constants_current_partial_fit
        # _poly_dupls_current_partial_fit

        # poly_constants -----------------------
        # merge _poly_constants_current_partial_fit into
        # self._poly_constants, which would be holding the constants
        # found in previous partial fits

        self._poly_constants: dict[tuple[int, ...], Any] = \
            _merge_constants(
                self._poly_constants,
                _poly_constants_current_partial_fit,
                _rtol=self.rtol,
                _atol=self.atol
            )

        del _poly_constants_current_partial_fit
        # END poly_constants -----------------------

        # poly duplicates -----------------------
        # merge the current _poly_dupls_current_partial_fit with
        # self._poly_duplicates, which could be holding duplicates found
        # in previous partial fits.
        # need to leave X tuples in here, need to follow the
        # len(dupl_set) >= 2 rule to correctly merge
        # _poly_dupls_current_partial_fit into _poly_duplicates
        self._poly_duplicates: list[list[tuple[int, ...]]] = \
            _merge_partialfit_dupls(
                self._poly_duplicates,
                _poly_dupls_current_partial_fit
            )

        del _poly_dupls_current_partial_fit

        # _merge_partialfit_dupls sorts _poly_duplicates on the way out.
        # within dupl sets, sort on combo len (degree) asc, then sort asc
        # on idxs. sort across all dupl sets, only look at the first
        # value, sort on len asc, then idxs asc
        # END poly duplicates -----------------------

        # iff self.poly_constants_ is None at this point it is because
        # @property for it is excepting on self._check_X_constants_and_dupls()
        # and returning None. In that case, all @properties will also
        # trip on that and return None. partial_fit and transform will
        # continue to warn and the @properties will continue to warn as
        # long as the dupl and/or constants condition in X exists.
        # because all access points are a no-op when dupls or constants
        # in X, then the below hidden params are not needed. skip making
        # them because while there are dupls/constants in X, _get_active_combos
        # is calling self.poly_constants_ and self.dropped_poly_duplicates_
        # and they are returning None which is getting caught in the
        # validation for the modules that build the hidden attrs.
        # _rand_combos and _kept_combos arent raising but they arent
        # needed and are just filling with nonsense because of the
        # degenerate state of X.
        if self.poly_constants_ is None:
            return self

        # when doing partial fits, columns that are currently constant
        # must be tracked in self._poly_duplicates if they are also
        # duplicates because in future partial fits they may no longer
        # be constant, but may still be duplicates. but this creates a
        # problem in that things that are constant in the present state
        # are mixed into self._poly_duplicates, which clouds the water
        # when building _rand_combos, _kept_combos, and _active_combos.
        # need a de-constanted _poly_duplicates for building these
        # objects, while preserving the state of _poly_duplicates.
        # all of this machinery is built into @property poly_duplicates_
        # ---------------------------------------------------------------------
        # BELOW THIS LINE USE poly_duplicates_ ONLY, DO NOT USE _poly_duplicates

        # if 'keep' == 'random', _transform() must pick the same random
        # duplicate columns at every call after fitting is completed.
        # need to set an instance attribute here that doesnt change when
        # _transform() is called. must set a random idx for every set of
        # dupls.
        self._rand_combos: tuple[tuple[int, ...], ...] = \
            _lock_in_random_combos(poly_duplicates_=self.poly_duplicates_)

        # this needs to be before _get_active_combos because _kept_combos
        # is an input into @property dropped_poly_duplicates_
        self._kept_combos: tuple[tuple[int, ...], ...] = \
            _identify_combos_to_keep(
                self.poly_duplicates_,
                self.keep,
                self._rand_combos
            )

        # @property dropped_poly_duplicates_ needs self.poly_duplicates_
        # and self._kept_combos
        self._active_combos = _get_active_combos(
            self._combos,
            self.poly_constants_,
            self.dropped_poly_duplicates_
        )

        return self


    def fit(
        self,
        X:XContainer,
        y:Any = None
    ) -> Self:
        """Perform a single fitting on a dataset.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            Required. The data to undergo polynomial expansion.
        y : Any, default=None
            Ignored. The target for the data.

        Returns
        -------
        self : object
            The fitted `SlimPolyFeatures` instance.

        """

        self.reset()

        return self.partial_fit(X, y)


    # def fit_transform(self, X, y=None, **fit_params):
    # inherited from FitTransformMixin


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


    # def set_output() - inherited from SetOutputMixin


    def set_params(self, **params) -> Self:
        """Set the parameters of the SPF instance.

        Pass the exact parameter name and its value as a keyword argument
        to the `set_params` method call. Or use ** dictionary unpacking
        on a dictionary keyed with exact parameter names and the new
        parameter values as the dictionary values. Valid parameter keys
        can be listed with :meth:`get_params`. Note that you can directly
        set the parameters of `MinCountTransformer`.

        Once SPF is fitted, only the following parameters can be changed
        via `set_params`: `sparse_output`, `keep`,  `n_jobs`, `job_size`,
        and `feature_name_combiner`. All other parameters are blocked.
        To use different parameters without creating a new instance of
        SPF, call SPF :meth:`reset` on the instance, otherwise create a
        new SPF instance.

        Parameters
        ----------
        **params : dict[str, Any]
            `SlimPolyFeatures` parameters.

        Returns
        -------
        self : object
            The `SlimPolyFeatures` instance.

        """


        # if this is fitted, impose blocks on some params.
        # if not fitted, allow everything to be set.
        if is_fitted(self):

            allowed_params = (
                'keep', 'sparse_output', 'feature_name_combiner', 'n_jobs',
                'job_size'
            )

            _valid_params = {}
            _invalid_params = {}
            _garbage_params = {}
            _spf_params = self.get_params()
            for param in params:
                if param not in _spf_params:
                    _garbage_params[param] = params[param]
                elif param in allowed_params:
                    _valid_params[param] = params[param]
                else:
                    _invalid_params[param] = params[param]


            if any(_garbage_params):
                # let super.set_params raise
                super().set_params(**params)

            if any(_invalid_params):
                warnings.warn(
                    "Once this transformer is fitted, only :params: 'keep', "
                    "'sparse_output', 'feature_name_combiner', 'n_jobs' "
                    "and 'job_size' can be changed via :meth: set_params. "
                    "\nAll other parameters are blocked. \nThe currently "
                    f"passed parameters {', '.join(list(_invalid_params))} "
                    f"have been blocked, but any valid parameters that "
                    f"were passed have been set. \nTo use different "
                    f"parameters without creating a new instance of this "
                    f"transformer class, call :meth: reset on this instance, "
                    f"otherwise create a new instance of SPF."
                )

            super().set_params(**_valid_params)

            del allowed_params, _valid_params, _invalid_params
            del _garbage_params, _spf_params

        else:

            super().set_params(**params)


        return self


    @SetOutputMixin._set_output_for_transform
    def transform(
        self,
        X: XContainer
    ) -> XContainer:
        """Apply the expansion footprint that was learned during fitting
        to the given data.

        pybear strongly urges that only data that was seen during fitting
        be passed here.

        Parameters
        ----------
        X : XContainer of shape (n_samples, n_features)
            The data to undergo polynomial expansion.

        Returns
        -------
        X_tr : XContainer of shape (n_samples, n_transformed_features)
            The polynomial feature expansion for `X`.

        """

        check_is_fitted(self)

        # this does a no-op if there are dupls or constants in X
        # returns None with a warning, allowing for more partial fits
        try:
            self._check_X_constants_and_dupls()
        except:
            warnings.warn(self._attr_access_warning())
            return


        X = validate_data(
            X,
            copy_X=False,
            cast_to_ndarray=False,
            accept_sparse=("csr", "csc", "coo", "dia", "lil", "dok", "bsr"),
            dtype='numeric',
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
            X,
            self.degree,
            self.min_degree,
            self.scan_X,
            self.keep,
            self.interaction_only,
            self.sparse_output,
            self.feature_name_combiner,
            self.rtol,
            self.atol,
            self.equal_nan,
            self.n_jobs,
            self.job_size
        )

        self._check_n_features(X, reset=False)

        self._check_feature_names(X, reset=False)

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # _validation should have caught non-numeric X. X must only be
        # numeric throughout all of SPF.

        _og_format = type(X)

        # ss sparse that cant be sliced
        # avoid copies of X, do not mutate X. if X is coo, dia, bsr, it
        # cannot be sliced. must convert to another ss. so just convert
        # all of them to csc for faster column slicing. need to change
        # it back later.
        if hasattr(X, 'toarray'):
            X = X.tocsc()

        # pd df with funky nan-likes that np and ss dont like
        if self.min_degree == 1 and isinstance(X, pd.DataFrame):
            try:
                X.astype(np.float64)
                # if excepts, there are pd nan-likes that arent recognized
                # by numpy. if passes, this df should just hstack with
                # X_tr without a problem.
                _X = X
            except:
                warnings.warn(
                    f"pybear works hard to avoid mutating or creating "
                    f"copies of your original data. \nyou have passed a "
                    f"dataframe that has nan-like values that are not "
                    f"recognized by numpy/scipy. \nbut to merge this "
                    f"data with the polynomial expansion, pybear must "
                    f"make a copy to replace all the nan-likes with "
                    f"numpy.nan. \nto avoid this copy, pass your "
                    f"dataframe with numpy.nan in place of any nan-likes "
                    f"that are only recognized by pandas."
                )
                _X = X.copy()
                _X[nan_mask(_X)] = np.nan
        else:
            _X = X

        # --------------------------------------------------------------
        # BELOW THIS LINE USE poly_duplicates_ ONLY, DO NOT USE _poly_duplicates

        # SPF params may have changed via set_params. need to recalculate
        # some attributes.
        # poly_constants_ does not change no matter what params are
        # poly_duplicates_ does not change no matter what params are
        # poly_combinations_, kept_poly_duplicates_, and
        # dropped_poly_duplicates_ might change based on :param: 'keep'

        # this needs to be before _get_active_combos because _kept_combos
        # is an input into @property dropped_poly_duplicates_
        self._kept_combos: tuple[tuple[int, ...], ...] = \
            _identify_combos_to_keep(
                self.poly_duplicates_,
                self.keep,
                self._rand_combos
            )

        # @property dropped_poly_duplicates_ needs self.poly_duplicates_
        # and self._kept_combos
        self._active_combos = _get_active_combos(
            self._combos,
            self.poly_constants_,
            self.dropped_poly_duplicates_
        )

        X_tr: ss.csc_array = \
            _build_poly(
                _X,
                self._active_combos
            )

        # experiments show that if stacking with ss.hstack:
        # 1) at least one of the terms must be a scipy sparse
        # 2) if one is ss, and the other is not, always returns as COO
        #       regardless of what ss format was passed
        # 3) if both are ss, but different types, always returns as COO
        # 4) only when both same type of ss is that type of ss returned
        # 5) OK to mix ss array and ss matrix, array will trump matrix
        # so need to convert X to X_tr format to maintain X_tr format
        if self.min_degree == 1:
            # this excepts when trying to do type(X_tr)(_X) when type(X_tr)
            # is ss and _X.dtype is object or str. we know from _validation
            # that X is numeric, if original X dtype is str or object set
            # the dtype of the merging X to float64
            try:
                X_tr = ss.hstack((type(X_tr)(_X.astype(np.float64)), X_tr))
            except:
                X_tr = ss.hstack((type(X_tr)(_X.cast(pl.Float64)), X_tr))

        assert isinstance(X_tr, ss.csc_array)

        del _X

        # all scipy sparse were converted to csc near the top of this
        # method. change it back to original state. do not mutate X!
        if hasattr(X, 'toarray'):
            X = _og_format(X)

        if self.sparse_output:
            return X_tr.tocsr()
        elif 'scipy' in str(_og_format).lower():
            # if input was scipy, but not 'sparse_output', return in the
            # original scipy format
            return _og_format(X_tr)
        else:
            # ndarray or pd/pl df, return in the given format
            X_tr = X_tr.toarray()

            if _og_format is np.ndarray:
                return np.ascontiguousarray(X_tr)

            elif _og_format is pd.DataFrame:
                return pd.DataFrame(
                    data=X_tr,
                    columns=self.get_feature_names_out()
                )
            elif _og_format is pl.DataFrame:
                return pl.from_numpy(
                    data=X_tr,
                    schema=list(self.get_feature_names_out())
                )
            else:
                raise Exception




