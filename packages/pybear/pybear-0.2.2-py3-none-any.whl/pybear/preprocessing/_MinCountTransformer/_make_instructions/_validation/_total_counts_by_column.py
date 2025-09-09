# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import TotalCountsByColumnType

import numpy as np



def _val_total_counts_by_column(
    _total_counts_by_column: TotalCountsByColumnType
) -> None:
    """Validate `_total_counts_by_column` is dict, outer keys are
    integer >= 0, values are dict with data values as keys and counts
    (integers >= 0) as values.

    Parameters
    ----------
    _total_counts_by_column : dict[int, dict[DataType, int]]
        The uniques and their frequencies for all the columns in the
        data.

    Return
    ------
    None

    """


    _tcbc = _total_counts_by_column

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # must be dict
    # outer keys must be zero-indexed contiguous integer
    err_msg = (
        f"'_total_counts_by_column' must be a dictionary of dictionaries, "
        f"\nwith positive integer keys and dictionaries as values."
    )

    try:
        if not isinstance(_tcbc, dict):
            raise Exception
        map(float, _tcbc)
        if any(map(isinstance, _tcbc, (bool for i in _tcbc))):
            raise Exception
        if not all(int(i)==i for i in _tcbc):
            raise Exception
        if not np.array_equiv(list(range(len(_tcbc))), list(_tcbc.keys())):
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # inner objects must be dict
    if not all(map(isinstance, _tcbc.values(), (dict for i in _tcbc.values()))):
        raise TypeError(
            f"_total_counts_by_column values must be dictionaries keyed "
            f"with data values and have integer values (counts)"
        )
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # inner dicts are intentionally not validated to have len > 0
    # (meaning that they can be empty)
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # inner key (DataType) must be non-sequence
    for _outer_key in _tcbc:
        for _inner_key in _tcbc[_outer_key]:
            try:
                list(_inner_key)
                if not isinstance(_inner_key, str):
                    raise UnicodeError
            except UnicodeError:
                raise TypeError(
                    f"_total_counts_by_column inner dictionaries must be "
                    f"keyed with data values (DataType)"
                )
            except Exception as e:
                pass
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # inner values must be int
    _inner_values = list(map(dict.values, _tcbc.values()))

    err_msg = (f"_total_counts_by_column inner dictionaries' counts "
               f"must be integers")

    if any(map(
        lambda x: any(map(isinstance, x, (bool for i in x))),
        _inner_values
    )):
        raise TypeError(err_msg)
    if not all(map(
        lambda x: all(map(isinstance, x, (int for i in x))),
        _inner_values
    )):
        raise TypeError(err_msg)

    # inner values must be >= 0
    if not all(v >= 0 for COLUMN_VALUES in _inner_values for v in COLUMN_VALUES):
        raise ValueError(f"all unique value counts must be >= 0")

    del _inner_values





