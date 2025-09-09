# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



if __name__ == '__main__':


    # use these to generate working _delete_instr
    from pybear.preprocessing._MinCountTransformer.MinCountTransformer import \
        MinCountTransformer

    from pybear.preprocessing._MinCountTransformer._print_instructions. \
        _repr_instructions import _repr_instructions

    from sklearn.datasets import load_breast_cancer

    import pandas as pd



    data = load_breast_cancer()

    RAW_X = data.data.astype(int)
    X = pd.DataFrame(data=RAW_X, columns=data.feature_names)
    X = X.drop(columns=['worst area', 'mean area'], inplace=False)
    y = data.target




    print(f'one recursion:')

    print()
    print(X)
    print()

    _threshold = 5

    test_cls = MinCountTransformer(
        count_threshold=_threshold,
        # ignore_columns=[0, 1],
        ignore_float_columns=False,
        ignore_non_binary_integer_columns=False
    )

    test_cls.partial_fit(X, y)

    out = _repr_instructions(
        _delete_instr=test_cls._make_instructions(),
        _total_counts_by_column=test_cls._total_counts_by_column,
        _thresholds=[_threshold for _ in range(X.shape[1])],
        _n_features_in=X.shape[1],
        _feature_names_in=X.columns,
        _clean_printout=True,
        _max_char=99
    )

    [print(i) for i in out]






