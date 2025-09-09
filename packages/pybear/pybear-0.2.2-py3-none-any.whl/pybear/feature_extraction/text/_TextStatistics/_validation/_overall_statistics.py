# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import OverallStatisticsType

import numbers



def _val_overall_statistics(
    _overall_statistics: OverallStatisticsType
) -> None:
    """Validate `overall_statistics` is a dictionary with the required
    keys and valid values.

    Parameters
    ----------
    _overall_statistics : dict[str, numbers.Real]
        The dictionary containing summary statistics about the strings
        fit on the `TextStatistics` instance, such as number of strings,
        average length of strings, etc.

    Returns
    -------
    None

    """


    assert isinstance(_overall_statistics, dict)
    assert len(_overall_statistics) == 6

    _allowed_keys = [
        'size',
        'uniques_count',
        'max_length',
        'min_length',
        'average_length',
        'std_length'
    ]

    for key in _overall_statistics:
        if key not in _allowed_keys:
            raise AssertionError(
                f"dict key '{key}' not an allowed key for overall_statistics"
            )

    _size = _overall_statistics['size']
    _uniques_count =_overall_statistics['uniques_count']
    _max_len = _overall_statistics['max_length']
    _min_len = _overall_statistics['min_length']
    _average_length = _overall_statistics['average_length']
    _std_length = _overall_statistics['std_length']

    assert isinstance(_size, int)
    assert not isinstance(_size, bool)
    assert _size >= 0

    assert isinstance(_uniques_count, int)
    assert not isinstance(_uniques_count, bool)
    assert _uniques_count >= 0
    assert _uniques_count <= _size

    assert isinstance(_max_len, int)
    assert not isinstance(_max_len, bool)
    assert _max_len >= 0

    assert isinstance(_min_len, int)
    assert not isinstance(_min_len, bool)
    assert _min_len >= 0
    assert _min_len <= _max_len

    assert isinstance(_average_length, numbers.Real)
    assert not isinstance(_average_length, bool)
    assert _average_length <= _max_len
    assert _average_length >= _min_len

    assert isinstance(_std_length, numbers.Real)
    assert not isinstance(_std_length, bool)
    assert _std_length >= 0




