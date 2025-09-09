# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_return_train_score(
    _return_train_score: bool
) -> None:
    """Validate `return_train_score`, which indicates whether to score
    the train data during the grid search; only booleans allowed.

    The test data is always scored. Train scores for the different folds
    can be compared against the test scores for anomalies.

    Parameters
    ----------
    _return_train_score : bool
        Whether to score the training data.

    Returns
    -------
    None

    """



    if not isinstance(_return_train_score, bool):
        raise TypeError(f"'return_train_score' must be boolean")





