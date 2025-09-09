# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    SKSlicerType,
    SKSplitType,
    SKXType,
    SKYType
)

import numpy as np
import pandas as pd
import scipy.sparse as ss



def _fold_splitter(
    train_idxs: SKSlicerType,
    test_idxs: SKSlicerType,
    *data_objects: SKXType | SKYType
) -> tuple[SKSplitType, ...]:
    """Split given data objects into train / test pairs using the given
    train and test indices.

    The train and test indices independently slice the given data
    objects; the entire data object need not be consumed in a train /
    test split and the splits can also possibly share indices. Standard
    indexing rules apply. Returns a tuple whose length is equal to the
    number of data objects passed, holding tuples of the train / test
    splits for the respective data objects. `train_idxs` and `test_idxs`
    must be 1D vectors of indices, not booleans.

    Parameters
    ----------
    train_idxs : SKSlicerType
        1D vector of row indices used to slice train sets out of every
        given data object.
    test_idxs : SKSlicerType
        1D vector of row indices used to slice test sets out of every
        given data object.
    *data_objects : SKXType | SKYType
        The data objects to slice. Need not be of equal size, and need
        not be completely consumed in the train / test splits. However,
        standard indexing rules apply when slicing by `train_idxs` and
        `test_idxs`.

    Returns
    -------
    SPLITS : tuple[SKSplitType, ...]
        Return the train / test splits for the given data objects in the
        order passed in a tuple of tuples, each inner tuple containing a
        train/test pair.

    """


    SPLITS = []
    for _data in data_objects:

        if isinstance(_data, (np.ndarray, pd.Series)):
            _data_train = _data[train_idxs]
            _data_test = _data[test_idxs]
        elif isinstance(_data, pd.DataFrame):
            _data_train = _data.iloc[train_idxs, :]
            _data_test = _data.iloc[test_idxs, :]
        elif hasattr(_data, 'toarray'):
            _og_type = type(_data)
            _data = ss.csr_array(_data)
            _data_train = _og_type(_data[train_idxs, :])
            _data_test = _og_type(_data[test_idxs, :])
            _data = _og_type(_data)
            del _og_type
        elif hasattr(_data, 'clone'):
            _bool_train_idxs = np.zeros(_data.shape[0]).astype(bool)
            _bool_train_idxs[train_idxs] = True
            _data_train = _data.filter(_bool_train_idxs)
            del _bool_train_idxs
            _bool_test_idxs = np.zeros(_data.shape[0]).astype(bool)
            _bool_test_idxs[test_idxs] = True
            _data_test = _data.filter(_bool_test_idxs)
            del _bool_test_idxs
        else:
            _og_container = type(_data)
            _data_train = np.array(list(_data))[train_idxs]
            _data_test = np.array(list(_data))[test_idxs]
            try:
                _data_train = _og_container(map(_og_container, _data_train))
                _data_test = _og_container(map(_og_container, _data_test))
            except:
                _data_train = _og_container(_data_train)
                _data_test = _og_container(_data_test)
            del _og_container


        SPLITS.append(tuple((_data_train, _data_test)))


    return tuple(SPLITS)




