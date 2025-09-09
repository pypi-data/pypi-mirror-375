# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Literal,
    Sequence
)
from .._type_aliases import CountThresholdType

import numbers

import numpy as np

from ...__shared._validation._any_integer import _val_any_integer



def _val_count_threshold(
    _count_threshold: CountThresholdType,
    _allowed: Sequence[Literal['int', 'Sequence[int]']],
    _n_features_in: int
) -> None:
    """Validate a threshold is non-bool integer >= 2, or a 1D list-like
    of non-bool integers >= 1 with at least one value >= 2 and length
    that equals `_n_features_in`.

    Validate the passed dtype of `_count_threshold` is in the allowed
    dtypes. `_count_threshold` must exist, cannot be None.

    Parameters
    ----------
    _count_threshold : CountThresholdType
        Integer >= 2 or list-like of integers of shape (n_features, )
        with all values >= 1 and at least one value >= 2. The minimum
        frequency a value must have within a column in order to not be
        removed. if list-like, the length must equal the number of
        features in the data.
    _allowed : Sequence[Literal['int', 'Sequence[int]']]
        Must be 1D list-like of literal strings. Indicates the dtype(s)
        of `_count_threshold` that is/are allowed for this validation
        session. Cannot be empty, can contain either 'Sequence[int]',
        'int', or both.
    _n_features_in : int
        The number of features in the data.

    Returns
    -------
    None

    """


    # other validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    _err_msg = (
        f"'_allowed' must be 1D list-like that contains string 'int' "
        f"or 'Sequence[int]' or both, case-sensitive, cannot be empty."
    )
    try:
        iter(_allowed)
        if isinstance(_allowed, (str, dict)):
            raise Exception
        if not all(map(isinstance, _allowed, (str for _ in _allowed))):
            raise Exception
        if len(_allowed) not in [1, 2]:
            raise UnicodeError
        for i in _allowed:
            if i not in ['int', 'Sequence[int]']:
                raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg + f" got {_allowed}.")
    except Exception as e:
        raise TypeError(_err_msg + f" got {_allowed}.")
    del _err_msg

    # END other validation ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # number handling -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    err_msg1 = (f"\nwhen 'count_threshold' is passed as a single integer "
                f"it must be non-boolean >= 2. ")

    is_num = False
    try:
        float(_count_threshold)
        if isinstance(_count_threshold, bool):
            raise MemoryError
        if not int(_count_threshold) == _count_threshold:
            raise IndexError
        if not _count_threshold >= 2:
            raise IndexError
        # if get to this point, we are good to go as integer
        is_num = True
        _count_threshold = int(_count_threshold)
    except MemoryError:
        # # if MemoryError, means bad number
        raise TypeError(err_msg1)
    except IndexError:
        # if IndexError, means bad integer
        raise ValueError(err_msg1)
    except Exception as e:
        # if not MemoryError or IndexError, excepted for not number,
        # must be Sequence to pass, but could be other junk
        pass
    # END number handling -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # iter handling -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    err_msg2 = (
        f"\nwhen 'count_threshold' is passed as a sequence it must be a "
        f"1D list-like of integers where any value can be >= 1, but at "
        f"least one value must be >= 2. \nthe length of the sequence "
        f"also must match the number of features in the data. "
    )

    is_iter = False
    try:
        if is_num:
            raise UnboundLocalError
        iter(_count_threshold)
        if isinstance(_count_threshold, (str, dict)):
            raise UnicodeError
        if len(np.array(list(_count_threshold)).shape) != 1:
            raise MemoryError
        if len(_count_threshold) != _n_features_in:
            raise MemoryError
        if not all(map(
            isinstance,
            _count_threshold,
            (numbers.Integral for _ in _count_threshold)
        )):
            raise MemoryError
        if not all(map(lambda x: x >= 1, _count_threshold)):
            raise MemoryError
        if not any(map(lambda x: x >= 2, _count_threshold)):
            raise MemoryError
        # if passes all these check, good to go as sequence
        is_iter = True
    except UnboundLocalError:
        pass
    except UnicodeError:
        # if UnicodeError is str or dict sequence
        raise TypeError(err_msg2)
    except MemoryError:
        # if MemoryError, bad shape, bad len, non-int, not all >=1, not
        # one >= 2
        raise ValueError(err_msg2)
    except Exception as e:
        # if not Unicode or MemoryError, then is not a float and is not
        # sequence
        raise TypeError(err_msg1 + err_msg2 + f"got {type(_count_threshold)}.")

    # END iter handling -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    assert not (is_num and is_iter)

    if is_num and 'int' not in _allowed:
        raise TypeError(
            f"'threshold' was passed as a non-sequence number but that "
            f"dtype is not allowed."
        )

    if is_iter and 'Sequence[int]' not in _allowed:
        raise TypeError(
            f"'threshold' was passed as a sequence of thresholds but "
            f"that dtype is not allowed."
        )




