# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
)



def _val_match_callable(
    _match_callable: Callable[[str, str], bool] | None
) -> None:
    """Validate `match_callable`.

    Must be None or a callable with signature [str, str] that returns a
    bool.

    Parameters
    ----------
    _match_callable : Callable[[str, str], bool] | None
        None to use the default `StopRemover` matching criteria, or a
        custom callable that defines what constitutes matches of words
        in the text against the stop words.

    Returns
    -------
    None

    """


    if _match_callable is None:
        return


    try:
        if not callable(_match_callable):
            raise Exception
    except Exception as e:
        raise TypeError(f"'match_callable' must be None or a callable.")

    # let the callable fall on it's own sword if the signature is wrong
    # or it doesnt return a bool.




