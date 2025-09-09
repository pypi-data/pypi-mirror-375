# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
)
from ..._type_aliases import ScorerInputType

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score
)



# **** IMPORTANT ****
# THIS IS THE DECLARATION THAT DICTATES WHAT SCORERS GSTCV CAN USE
master_scorer_dict = {
    'accuracy': accuracy_score,
    'balanced_accuracy': balanced_accuracy_score,
    'average_precision': average_precision_score,
    'f1': f1_score,
    'precision': precision_score,
    'recall': recall_score
}



def _val_scoring(
    _scoring:ScorerInputType,
    _must_be_dict:bool = True
) -> None:
    """Validate `scoring`, the scoring metric(s) used to evaluate the
    predictions on the test (and possibly train) sets.

    Can be dict[str, Callable] for any number of scorers, singular or
    plural.

    For a single scoring metric, can be a single string or a single
    callable. Valid strings that can be passed are 'accuracy',
    'balanced_accuracy', 'average_precision', 'f1', 'precision', and
    'recall'.

    For evaluating multiple metrics, scoring can also be a vector-like
    of (unique) strings, containing a combination of the allowed strings.

    Parameters
    ----------
    _scoring : ScorerInputType
        The scoring metric(s) used to evaluate the predictions on the
        test (and possibly train) sets.
    _must_be_dict : bool, default = True
        Whether 'scoring' must have already been conditioned into
        dict[str, Callable].

    Returns
    -------
    None

    """


    # helper functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    def string_validation(_string: str) -> None:

        """Check scorer name is valid."""

        if _string.lower() not in master_scorer_dict:
            if 'roc_auc' in _string or 'average_precision' in _string:
                raise ValueError(
                    f"Don't need to use GridSearchThreshold when scoring "
                    f"is roc_auc or average_precision (auc_pr). \nUse "
                    f"regular sklearn/dask GridSearch and use max(tpr-fpr) "
                    f"to find best threshold for roc_auc, \nor use max(f1) "
                    f"to find the best threshold for average_precision."
                )
            else:
                raise ValueError(
                    f"When specifying scoring by scorer name, must be "
                    f"in \n{', '.join(list(master_scorer_dict))} ('{_string}')"
                )


    def check_callable_is_valid_metric(
        fxn_name: str,
        _callable: Callable
    ) -> None:

        """Check user scorer callable works and returns a number."""

        _truth = np.random.randint(0, 2, (100,))
        _pred = np.random.randint(0, 2, (100,))

        try:
            _value = _callable(_truth, _pred)
        except:
            raise ValueError(
                f"scoring function '{fxn_name}' excepted during validation"
            )

        try:
            float(_value)
        except:
            raise ValueError(
                f"scoring function '{fxn_name}' returned a non-numeric ({_value})"
            )

        del _truth, _pred, _value
    # END helper functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    if _must_be_dict and not isinstance(_scoring, dict):
        raise TypeError(
            f"'scoring'/'scorer_' must be a dict of: "
            f"\n(metric name: callable(y_true, y_pred), ...)."
        )


    _err_msg = (
        f"scoring must be "
        f"\n1) a single metric name as string, or "
        f"\n2) a callable(y_true, y_pred) that returns a single "
            f"numeric value, or "
        f"\n3) a list-type of metric names as strings, or "
        f"\n4) a dict of: (metric name: callable(y_true, y_pred), ...)."
        f"\nCannot pass None or bool. Cannot use estimator's default scorer."
    )

    try:
        if isinstance(_scoring, Callable):
            raise Exception
        iter(_scoring)
        if isinstance(_scoring, (str, dict)):
            raise Exception
        _is_list_like = True
    except Exception as e:
        _is_list_like = False


    if isinstance(_scoring, str):
        string_validation(_scoring)
    elif callable(_scoring):
        check_callable_is_valid_metric(f'score', _scoring)
    elif _is_list_like:
        try:
            _scoring = list(np.array(list(_scoring)).ravel())
            if len(_scoring) == 0:
                raise UnicodeError
        except UnicodeError:
            raise ValueError(f"'scoring' is and empty list-like --- " + _err_msg)
        except Exception as e:
            raise TypeError(_err_msg)

        for _scorer_name in _scoring:
            if not isinstance(_scorer_name, str ):
                raise TypeError(_err_msg)
            string_validation(_scorer_name)

    elif isinstance(_scoring, dict):
        if len(_scoring) == 0:
            raise ValueError(f'scoring is empty --- ' + _err_msg)

        if not all(map(isinstance, _scoring, (str for _ in _scoring))):
            raise ValueError(_err_msg)

        for key in list(_scoring.keys()):
            # DONT USE string_validation() HERE, USER-DEFINED CALLABLES
            # CAN HAVE USER-DEFINED NAMES
            check_callable_is_valid_metric(key.lower(), _scoring[key])

    else:
        raise TypeError(_err_msg)

    del _err_msg, _is_list_like
    del string_validation, check_callable_is_valid_metric






