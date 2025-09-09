# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.2] - 2025-09-08

### Added
- None

### Changed
- model_selection.autogridsearch_wrapper:
    Adjust how soft integer space calculates next grid's points when 
    last best falls on a non-edge value.
- utilities:
    - nan_mask_string, nan_mask:
        Add pandas.NaT to searched nan-like values.

### Deprecated
- None

### Removed
- None

### Fixed
- preprocessing.SlimPolyFeatures
    Fix pickling error on "large" datasets. Set backend='loky' and 
    max_nbytes="100M" for all usages of joblib.Parallel.

### Security
- None

## [0.2.1] - 2025-08-16

### Added
- None

### Changed
- Python dependency from ">=3.10, <3.14" to ">=3.10"
- Optional and Union type hints replaced with pipes
- numbers.Integral in docs and type hints changed to int

### Deprecated
- None

### Removed
- None

### Fixed
- feature_extraction.text
    - All modules except Lexicon and TextStatistics:
        Fix conversion of pandas dataframes to list[list[str]]. Fix handling 
        and casting of nan-likes; now all cast to str('nan'). 
    - TextSplitter, TextLookup, TextLookupRealTime, TextJoiner, NGramMerger:
        Changed X validation to allow non-finite values (e.g. 'nan')

### Security
- None

## [0.2.0] - 2025-07-28

### Added
    - base:
        cast_to_ndarray,
        check_1D_num_sequence,
        check_1D_str_sequence,
        check_2D_num_array,
        check_2D_str_array,
        check_dtype,
        check_feature_names,
        check_is_finite,
        check_is_fitted,
        check_n_features,
        check_scipy_sparse,
        check_shape,
        copy_X,
        DictMenuPrint,
        ensure_2D,
        get_feature_names,
        get_feature_names_out,
        is_fitted,
        num_features,
        num_samples,
        set_order,
        user_entry,
        validate_data,
        validate_user_float,
        validate_user_int,
        validate_user_mstr,
        validate_user_str,
        validate_user_str_cs,
        ValidateUserDate,
        FeatureMixin,
        FileDumpMixin,
        FitTransformMixin,
        GetParamsMixin,
        ReprMixin,
        SetOutputMixin,
        SetParamsMixin,
        NotFittedError
    
    - feature_extraction
        - text:
            AutoTextCleaner,
            Lexicon,
            NGramMerger,
            StopRemover
            TextJoiner,
            TextJustifier,
            TextLookup,
            TextLookupRealTime,
            TextNormalizer,
            TextPadder,
            TextRemover,
            TextReplacer,
            TextSplitter,
            TextStatistics,
            TextStripper
    
    - model_selection:
        autogridsearch_wrapper,
        AutoGridSearchCV,
        AutoGSTCV,
        GSTCV
    
    - new_numpy:
        - random:
            choice,
            Sparse
            sparse
    
    - preprocessing:
        ColumnDeduplicator,
        InterceptManager,
        MinCountTransformer,
        NanStandardizer,
        SlimPolyFeatures
    
    - utilities:
        array_sparsity, 
        check_pipeline,
        feature_name_mapper,
        get_module_name,
        inf_mask,
        nan_mask,
        nan_mask_numerical,
        nan_mask_string,
        permuter,
        serial_index_mapper,
        time_memory_benchmark,
        timer,
        union_find

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1] - [Unreleased]



