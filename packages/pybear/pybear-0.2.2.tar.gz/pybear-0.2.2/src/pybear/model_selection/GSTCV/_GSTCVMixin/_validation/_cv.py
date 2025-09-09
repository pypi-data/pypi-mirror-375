# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterable,
)
from ..._type_aliases import GenericKFoldType



def _val_cv(
    _cv:None | int | Iterable[GenericKFoldType],
    _can_be_None:bool = False,
    _can_be_int:bool = False
) -> None:
    """Validate `cv`.

    Validate that `_cv` is:

    1) None,

    2) an integer >= 2, or

    3) an iterable; the contents of the iterable are not validated, to
        not spend the iterable here.

    Parameters
    ----------
    _cv : None | int | Iterable[GenericKFoldType

        Possible inputs for cv are:

        1) None, to use the default n-fold cross validation,

        2) integer >= 2 to specify the number of folds in a
            (Stratified)KFold,

        3) An iterable yielding (train, test) split indices as arrays.
    _can_be_None : bool, default = False
    _can_be_int : bool, default = False


    Returns
    -------
    None

    """


    assert isinstance(_can_be_None, bool)
    assert isinstance(_can_be_int, bool)


    err_msg = (
        "Possible inputs for cv are: "
        "\n1) None, to use the default n-fold cross validation, "
        "\n2) integer >= 2, to specify the number of folds in a (Stratified)KFold, "
        "\n3) An iterable yielding at least 2 (train, test) split pairs "
        "with each pair being 2 vectors of indices."
    )


    _addon = ''

    try:
        if _cv is None:
            if _can_be_None:
                raise TimeoutError
            elif not _can_be_None:
                _addon = f"\ngot None but None is disallowed."
                raise UnicodeError

        # DONT ITER THE ITERABLE HERE. IF IT IS A GENERATOR IT WILL BE
        # SPENT. HAVE TO WAIT UNTIL CONDITIONING WHERE GENERATOR WOULD
        # BE CACHED AS LIST.
        iter(_cv)
        if isinstance(_cv, (dict, str)):
            _addon = f"\ngot {type(_cv)}"
            raise UnicodeError
    except TimeoutError:
        pass
    except UnicodeError:
        raise TypeError(err_msg + _addon)
    except Exception as e:
        # to handle a non-iterable
        try:
            _addon = f"\nGot {_cv}"
            float(_cv)
            if isinstance(_cv, bool):
                raise Exception
            if int(_cv) != _cv:
                raise Exception
            if not _can_be_int:
                _addon = f"\ngot int but int is disallowed."
                raise Exception
            if _cv < 2:
                raise MemoryError
        except MemoryError:
            raise ValueError(err_msg + _addon)
        except Exception as e:
            raise TypeError(err_msg + _addon)





