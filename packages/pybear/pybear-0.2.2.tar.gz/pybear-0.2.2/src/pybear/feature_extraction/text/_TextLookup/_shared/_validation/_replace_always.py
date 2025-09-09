# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_replace_always(
    _replace_always: dict[str, str] | None
) -> None:
    """Validate `replace_always`.

    Must be None or a dictionary with string keys and string values.

    Parameters
    ----------
    _replace_always : dict[str, str] | None
        A dictionary of keys that when the key is a case-sensitive match
        against a word in the text then the respective value is put in
        place of the word in the text body.

    Returns
    -------
    None

    """


    if _replace_always is None:
        return


    try:
        if not isinstance(_replace_always, dict):
            raise Exception
        if not all(map(
            isinstance,
            _replace_always,
            (str for _ in _replace_always)
        )):
            raise Exception
        if not all(map(
            isinstance,
            _replace_always.values(),
            (str for _ in _replace_always.values())
        )):
            raise Exception
    except:
        raise TypeError(
            f"'replace_always' must be None or a dictionary with string "
            f"keys and string values.")




