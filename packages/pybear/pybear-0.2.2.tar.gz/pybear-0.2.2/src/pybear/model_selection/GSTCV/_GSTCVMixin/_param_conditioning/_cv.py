# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterable,
)
from ..._type_aliases import GenericKFoldType

import numbers



def _cond_cv(
    _cv:None | int | Iterable[GenericKFoldType],
    _cv_default:int = 5
) -> int | list[GenericKFoldType]:
    """Condition `cv`.

    There was some validation that was forgone in the validation section.
    `cv` might be a generator, and it was not iterated (and spent) in
    the validation section. Do that now.

    1) if `cv` is None, return int(_cv_default)

    2) if `cv` is an integer, return int(_cv)

    3) otherwise, must be an iterable of pairs of iterables. validate
        that the outer container is iterable, with at least 2 iterables
        inside, and each inner iterable is len==2 with iterables inside.
        the outer iterable cannot be empty. return as a list of tuples
        of iterables (which hopefully are 1D vectors).

    Parameters
    ----------
    _cv : None | int | Iterable[GenericKFoldType]

        Possible inputs for cv are:

        1) None, to use the default n-fold cross validation,

        2) integer >= 2 to specify the number of folds in a
            (Stratified)KFold,

        3) An iterable yielding (train, test) split indices as arrays.

        For passed iterables:
        This module will convert generators to lists. No validation is
        done beyond verifying that it is an iterable that contains pairs
        of iterables. `GSTCV` will catch out of range indices and raise
        but any validation beyond that is up to the user outside of
        `GSTCV`.

    _cv_default : int, default=5
        The number of cv folds to be applied when `cv` is None.

    Returns
    -------
    _cv : int | list[GenericKFoldType]
        Conditioned `cv` input

    """


    assert isinstance(_cv_default, numbers.Integral)


    try:
        iter(_cv)
    except:
        # int & None returned here
        try:
            return int(_cv)
        except:
            return int(_cv_default)


    # below here must be iter, None/int was returned above

    err_msg = (
        "Possible inputs for cv are: "
        "\n1) None, to use the default n-fold cross validation, "
        "\n2) integer >= 2, to specify the number of folds in a (Stratified)KFold, "
        "\n3) An iterable yielding at least 2 (train, test) split pairs "
        "with each pair being 2 1D vectors of indices."
    )


    try:
        iter(_cv)
        _addon1 = '\ngot non-iterable inside iterable.'
        _cv = list(map(tuple, _cv))
        if len(_cv) == 0:
            _addon2 = f"\ngot empty iterable."
            raise UnicodeError
        elif len(_cv) == 1:
            _addon2 = f"\ngot one pair."
            raise UnicodeError
        _lens = list(map(len, _cv))
        if not (max(_lens) == min(_lens) == 2):
            _addon2 = f"\ngot inner pair len != 2."
            raise UnicodeError
        del _lens
        # show that the constituents of each tuple are iterable
        _addon1 = f"\ngot a non-iterable inside at least one of the pairs."
        list(map(lambda x: list(map(iter, x)), _cv))
    except UnicodeError:
        raise ValueError(err_msg + _addon2)
    except Exception as e:
        raise TypeError(err_msg + _addon1)


    return _cv






