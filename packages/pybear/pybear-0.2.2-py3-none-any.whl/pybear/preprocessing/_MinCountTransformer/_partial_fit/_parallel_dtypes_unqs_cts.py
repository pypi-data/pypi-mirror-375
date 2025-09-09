# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Any
import numpy.typing as npt

import numpy as np

from ....utilities._nan_masking import nan_mask



def _parallel_dtypes_unqs_cts(
    _chunk_of_X: npt.NDArray,
) -> list[tuple[str, dict[Any, int]]]:
    """Parallelized collection of dtype, uniques, and frequencies from a
    chunk of `X`.

    Sometimes np.nan is showing up multiple times in uniques.
    Troubleshooting has shown that the condition that causes this is
    when dtype(`_chunk_of_X`) is object. The problem of multiple nans
    could be fixed by casting object dtype to str, but when the chunk
    dtype is object, we need to get the uniques in their given dtype,
    not as str. There are much gymnastics done to handle this issue.

    All nan-likes are cast to np.nan in :func:`_columns_getter`.

    Parameters
    ----------
    _chunk_of_X : NDArray
        A chunk of columns from `X`.

    Returns
    -------
    _dtypes_unqs_cts : list[tuple[str, dict[Any, int]]]
        List of tuples, each tuple representing one column and holding
        the MCT-assigned dtype and a dictionary. dtype can be in
        ['bin_int', 'int', 'float', 'obj']. The dictionary holds the
        uniques in the column as keys and the respective frequencies as
        values.

    """


    assert isinstance(_chunk_of_X, np.ndarray)


    _dtypes_unqs_cts = []
    for _c_idx in range(_chunk_of_X.shape[1]):

        _column_of_X = _chunk_of_X[:, _c_idx]    # 1D

        if _column_of_X.dtype != object:
            UNQ_CT_DICT = dict((zip(*np.unique(_column_of_X, return_counts=True))))
        elif _column_of_X.dtype == object:
        # remember the nan notes in the docstring, that when object
        # multiple nans show up in uniques. changing the dtype to str
        # works for getting only one nan, but this changes any numbers
        # in the obj column to string also, which persists even when
        # changing the dtype of the column back to obj, which then
        # populates UNQ_CT_DICT with str(num). this opens a huge can of
        # worms for making row masks. so we need to get the uniques in
        # the original dtype, then if object, remove any extra nans.
        # DO NOT MUTATE _column_of_X DTYPES!

        # but, there is another huge problem here, numpy.unique cant do
        # the mixed dtypes that might be in an 'object' column.
        # TypeError: '<' not supported between instances of 'float' and 'str'
        # we need to separate out num from str.

            NUM_LIKE = []
            STR_LIKE = []
            for _value in _column_of_X:
                try:
                    float(_value)
                    NUM_LIKE.append(_value)
                except:
                    STR_LIKE.append(_value)

            NUM_LIKE_UNQ_CT_DICT = \
                dict((zip(*np.unique(NUM_LIKE, return_counts=True))))
            STR_LIKE_UNQ_CT_DICT = \
                dict((zip(*np.unique(STR_LIKE, return_counts=True))))

            del NUM_LIKE, STR_LIKE

            UNQ_CT_DICT = NUM_LIKE_UNQ_CT_DICT | STR_LIKE_UNQ_CT_DICT
            del NUM_LIKE_UNQ_CT_DICT, STR_LIKE_UNQ_CT_DICT

            UNQS = np.fromiter(UNQ_CT_DICT.keys(), dtype=object)
            CTS = np.fromiter(map(int, UNQ_CT_DICT.values()), dtype=int)
            # if more than 1 nan, chop out all of them after the first,
            # but dont forget to put the total of all the nans on the
            # one kept!
            NANS = nan_mask(UNQS).astype(bool)
            if np.sum(NANS) > 1:
                NAN_IDXS = np.arange(len(UNQS))[NANS]
                CHOP_NAN_IDXS = NAN_IDXS[1:]
                CTS[NAN_IDXS[0]] += int(np.sum(CTS[CHOP_NAN_IDXS]))
                del NAN_IDXS
                CHOP_NAN_BOOL = np.ones(len(UNQS)).astype(bool)
                CHOP_NAN_BOOL[CHOP_NAN_IDXS] = False
                del CHOP_NAN_IDXS
                UNQ_CT_DICT = dict((
                    zip(UNQS[CHOP_NAN_BOOL], map(int, CTS[CHOP_NAN_BOOL]))
                ))
            del UNQS, CTS, NANS


        UNQ_CT_DICT = dict((zip(
            np.fromiter(UNQ_CT_DICT.keys(), dtype=_column_of_X.dtype),
            map(int, UNQ_CT_DICT.values())
        )))

        # get the nans out to get the dtype of the remaining
        UNIQUES = np.fromiter(UNQ_CT_DICT.keys(), dtype=_column_of_X.dtype)
        UNIQUES_NO_NAN = UNIQUES[np.logical_not(nan_mask(UNIQUES))]

        del UNIQUES


        # float64 RAISES ValueError ON STR DTYPES, IN THAT CASE MUST BE STR
        # if accepted astype, must be numbers from here down
        try:
            _column_of_X.astype(np.float64)
            raise UnicodeError
        except UnicodeError:
            # if is num
            if len(UNIQUES_NO_NAN) == 0:
                # a column of X cannot be empty, so it must have at least
                # 1 unq. if UNIQUES_NO_NAN is empty, then the unq was nan
                _dtypes_unqs_cts.append(('float', UNQ_CT_DICT))
            # determine if is integer
            elif np.allclose(
                UNIQUES_NO_NAN.astype(np.float64),
                UNIQUES_NO_NAN.astype(np.float64).astype(np.int32),
                atol=1e-6
            ):
                if np.array_equal(
                    sorted(list(UNIQUES_NO_NAN.astype(np.int32))), [0, 1]
                ):
                    _dtypes_unqs_cts.append(('bin_int', UNQ_CT_DICT))
                else:
                    _dtypes_unqs_cts.append(('int', UNQ_CT_DICT))
            else:
                _dtypes_unqs_cts.append(('float', UNQ_CT_DICT))
        except Exception as e:
            # if is non-num
            _dtypes_unqs_cts.append(('obj', UNQ_CT_DICT))


    return _dtypes_unqs_cts




