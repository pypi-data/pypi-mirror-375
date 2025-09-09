# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ...__shared._type_aliases import XContainer



def _val_X_supplemental(
    _X: XContainer,
    _interaction_only: bool
) -> None:
    """Supplemental validation of the data.

    When `_interaction_only` is True, `_X` must have at least 2 columns.
    When `_interaction_only` is False, `_X` must have at least 1 column.

    Parameters
    ----------
    _X : XContainer of shape (n_samples, n_features)
        The data to undergo polynomial expansion.
    _interaction_only : bool
        If True, only interaction features are produced, that is,
        polynomial features that are products of 'degree' distinct input
        features. Terms with power of 2 or higher for any feature are
        excluded.
        Consider 3 features 'a', 'b', and 'c'. If 'interaction_only' is
        True, 'min_degree' is 1, and 'degree' is 2, then only the first
        degree interaction terms ['a', 'b', 'c'] and the second degree
        interaction terms ['ab', 'ac', 'bc'] are returned in the
        polynomial expansion.

    Return
    ------
    None

    """


    assert isinstance(_interaction_only, bool)

    if _interaction_only:
        if _X.shape[1] < 2:
            _err_msg = (
                f"\nWhen only generating interaction terms (:param: "
                f"interaction_only is True), 'X' must have at least 2 "
                f"features."
            )
            raise ValueError(_err_msg)
    elif not _interaction_only:
        if _X.shape[1] < 1:
            _err_msg = (
                f"\nWhen generating all polynomial terms (:param: "
                f"interaction_only is False), 'X' must have at least 1 "
                f"feature."
            )
            raise ValueError(_err_msg)





