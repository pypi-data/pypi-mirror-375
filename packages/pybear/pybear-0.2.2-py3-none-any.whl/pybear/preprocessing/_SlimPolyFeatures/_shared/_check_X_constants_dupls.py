# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Any



def _check_X_constants_dupls(
    _X_constants: dict[int, Any],
    _X_dupls: list[list[int]]
) -> None:
    """Raise exception if `InterceptManager` found constants in `X` or
    if `ColumnDeduplicator` found duplicates in `X`.

    Parameters
    ----------
    _X_constants : dict[int, Any]
        The constants found in X by `InterceptManager`. The keys of the
        dictionary are the indices of the columns in `X` and the values
        are the constant values in that respective column. If it is
        empty, there are no constant columns.
    _X_dupls : list[list[int]]
        The sets of duplicates found in `X` by `ColumnDeduplicator`.
        Each list of integers is a group of column indices in `X` that
        are duplicate. If `_X_dupls` is empty, there are no duplicate
        columns.

    Returns
    -------
    None

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_X_constants, dict)
    if len(_X_constants):
        assert all(map(isinstance, _X_constants, (int for _ in _X_constants)))

    assert isinstance(_X_dupls, list)
    if len(_X_dupls):
        for _list in _X_dupls:
            assert isinstance(_list, list)
            assert all(map(isinstance, _list, (int for _ in _list)))
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    constants_err = (
        f"X has column(s) of constants: {_X_constants}"
        f"\nPlease use pybear InterceptManager to remove all constant "
        f"columns from X before using SlimPolyFeatures."
    )

    dupl_err = (
        f"X has duplicate columns: {_X_dupls}"
        f"\nPlease use pybear ColumnDeduplicator to remove all duplicate "
        f"columns from X before using SlimPolyFeatures."
    )


    if len(_X_constants) and len(_X_dupls):
        raise ValueError(f"\n{constants_err}" + f"\n{dupl_err}")

    elif len(_X_constants):
        raise ValueError(constants_err)

    elif len(_X_dupls):
        raise ValueError(dupl_err)
    else:
        # no constants, no duplicates in X, all good
        pass




