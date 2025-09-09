# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import OverallStatisticsType

import numbers
import math

from .._validation._overall_statistics import _val_overall_statistics


# not used as of first release


def _merge_overall_statistics(
    _current_overall_statistics: OverallStatisticsType,
    _overall_statistics: OverallStatisticsType,
    _len_uniques: int
) -> OverallStatisticsType:
    """Combine the statistics for the current batch of strings with those
    from the previous partial fits.

    Parameters
    ----------
    _current_overall_statistics : dict[str, numbers.Real]
        The overall statistics for the current partial fit.
    _overall_statistics : dict[str, numbers.Real]
        The statistics for all strings seen prior to the current partial
        fit.
    _len_uniques : int
        The number of unique strings seen by all partial fits, including
        the current partial fit.

    Returns
    -------
    _overall_statistics : dict[str, numbers.Real]
        The statistics for all strings seen.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_len_uniques, numbers.Real)
    assert not isinstance(_len_uniques, bool)

    # _current_overall_statistics must be passed
    _val_overall_statistics(_current_overall_statistics)

    # _overall_statistics could be empty dict
    try:
        if not len(_overall_statistics):
            raise UnicodeError
        raise TimeoutError
    except UnicodeError:
        pass
    except TimeoutError:
        _val_overall_statistics(_overall_statistics)
        assert _len_uniques >= _overall_statistics['uniques_count']
    except Exception as f:
        raise AssertionError(f)

    assert isinstance(_len_uniques, numbers.Integral)
    assert not isinstance(_len_uniques, bool)
    assert _len_uniques >= _current_overall_statistics['uniques_count']
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # if on first pass, _overall_statistics must be empty dict
    if len(_overall_statistics) == 0:
        return _current_overall_statistics

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # new std -- -- -- -- -- -- -- -- -- --
    # σ1,2 = sqrt((N1*σ1^2+N2*σ2^2+N1*d12+N2*d22) / (N1+N2))
    # Where,
    # σ1,2 = Combined Standard Deviation of the two groups
    # σ1 = Standard Deviation of first group
    # σ2 = Standard Deviation of second group
    # d12=(mean_X1−mean_pooled_X1_X2)^2
    # d22=(mean_X2-mean_pooled_X1_X2)^2
    # mean_pooled_X1_X2 = Combined Arithmetic Mean of the two groups
    # mean_X1 = Arithmetic Mean of first group
    # mean_X2 = Arithmetic Mean of second group
    # N1 = Number of Observations in the first group
    # N2 = Number of Observations in the second group

    m: int = _current_overall_statistics['size']
    n: int = _overall_statistics['size']
    x1_mean: numbers.Real = _current_overall_statistics['average_length']
    x2_mean: numbers.Real = _overall_statistics['average_length']
    x1_stdev: numbers.Real = _current_overall_statistics['std_length']
    x2_stdev: numbers.Real = _overall_statistics['std_length']

    _average_new: numbers.Real = (m * x1_mean + n * x2_mean) / (m + n)

    _top: numbers.Real = m * x1_stdev**2
    _top += n * x2_stdev**2
    _top += m * (x1_mean - _average_new)**2
    _top += n * (x2_mean - _average_new)**2
    _bottom = (m + n)
    _std_new = math.sqrt(_top/_bottom)

    del n, m, x1_mean, x2_mean, x1_stdev, x2_stdev, _top, _bottom
    # END new std -- -- -- -- -- -- -- -- --

    _overall_statistics['size'] += _current_overall_statistics['size']

    _overall_statistics['average_length'] = _average_new

    _overall_statistics['std_length'] = _std_new

    _overall_statistics['uniques_count'] = _len_uniques

    _overall_statistics['max_length'] = max(
        _overall_statistics['max_length'],
        _current_overall_statistics['max_length']
    )

    _overall_statistics['min_length'] = min(
        _overall_statistics['min_length'],
        _current_overall_statistics['min_length']
    )


    return _overall_statistics





