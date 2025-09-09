# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Any
from .._type_aliases import SKKFoldType

import numpy as np

from ._fold_splitter import _fold_splitter



def _estimator_fit_params_helper(
    _data_len: int,
    _fit_params: dict[str, Any],
    _KFOLD: SKKFoldType
) -> dict[int, dict[str, Any]]:
    """This module customizes the estimator's fit params for each pass of
    cv, to be passed at fit time for the respective fold.

    This is being done via a dictionary keyed by fold index, whose
    values are dictionaries holding the respective fit params for that
    fold. In particular, this is designed to perform splitting on any
    fit param whose length matches the number of examples in the data,
    so that the contents of that fit param are matched correctly to the
    train fold of data concurrently being passed to fit. Other params
    that are not split are simply replicated into each dictionary inside
    the helper.

    Parameters
    ----------
    _data_len : int
        The number of examples in the full data set.
    _fit_params : dict[str, Any]
        All the fit params passed to `GSTCV` fit for the estimator.
    _KFOLD : SKKFoldType
        The KFold indices that were used to create the train / test
        splits of data.

    Returns
    -------
    _fit_params_helper : dict[int, dict[str, Any]]
        A dictionary of customized fit params for each pass of cv.

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    try:
        float(_data_len)
        if isinstance(_data_len, bool):
            raise Exception
        if not int(_data_len) == _data_len:
            raise Exception
        _data_len = int(_data_len)
        if not _data_len > 0:
            raise Exception
    except:
        raise TypeError(f"'data_len' must be an integer greater than 0")

    assert isinstance(_fit_params, dict)
    assert all(map(isinstance, list(_fit_params), (str for i in _fit_params)))

    assert isinstance(_KFOLD, list), f"{type(_KFOLD)=}"
    assert all(map(isinstance, _KFOLD, (tuple for _ in _KFOLD)))
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _fit_params_helper = {}

    for f_idx, (train_idxs, test_idxs) in enumerate(_KFOLD):

        _fit_params_helper[f_idx] = {}

        for _fit_param_key, _fit_param_value in _fit_params.items():

            try:
                iter(_fit_param_value)
                if isinstance(_fit_param_value, (dict, str)):
                    raise Exception
                if np.array(list(_fit_param_value)).shape[0] != _data_len:
                    raise Exception
                # remember we only care about the train fold.
                _fit_params_helper[f_idx][_fit_param_key] = \
                    _fold_splitter(train_idxs, test_idxs, _fit_param_value)[0][0]
            except:
                _fit_params_helper[f_idx][_fit_param_key] = _fit_param_value


    return _fit_params_helper





