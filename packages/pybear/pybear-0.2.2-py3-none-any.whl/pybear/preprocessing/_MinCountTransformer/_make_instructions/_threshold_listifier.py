# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import CountThresholdType

import numbers

from .._validation._count_threshold import _val_count_threshold



def _threshold_listifier(
    _n_features_in: int,
    *_threshold: CountThresholdType
) -> list[int] | tuple[list[int], ...]:
    """Return `_threshold` as list-like(s) of integers with number of
    entries equaling the number of features in the data.

    Any number of threshold values can be passed as positional arguments
    to be converted to a list, if not already a list. This module will
    return the number of threshold values that are passed to it.

    Parameters
    ----------
    _n_features_in : int
        The number of features in the data.
    *_threshold : CountThresholdType
        The threshold value(s) to be converted to list[int]. Any number
        of threshold values can be passed as positional arguments.

    Return
    ------
    _threshold_lists : list[int] | tuple[list[int], ...]
        A single list[int] or a tuple of list[int]s that indicate the
        threshold for each feature in the data.

    """


    _threshold_lists: list[list[int]] = []
    for _threshold_entry in _threshold:

        # _n_features_in is validated by _val_count_threshold
        _val_count_threshold(
            _threshold_entry,
            ['int', 'Sequence[int]'],
            _n_features_in
        )
        # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        if isinstance(_threshold_entry, numbers.Integral):
            _threshold_lists.append(
                [int(_threshold_entry) for _ in range(_n_features_in)]
            )
        else:
            # if not int, must be Sequence[int] because of validation
            _threshold_lists.append(list(map(int, _threshold_entry)))


    if len(_threshold_lists) == 1:
        return _threshold_lists[0]
    else:
        return tuple(_threshold_lists)





