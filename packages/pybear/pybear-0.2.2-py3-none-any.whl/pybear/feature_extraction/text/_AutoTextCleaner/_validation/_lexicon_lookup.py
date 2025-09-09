# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import LexiconLookupType



def _val_lexicon_lookup(
    _lexicon_lookup: LexiconLookupType | None
) -> None:
    """Validate 'lexicon_lookup'.

    Must be None or a dictionary of parameters for TextLookupRealTime.

    Parameters
    ----------
    _lexicon_lookup : LexiconLookupType | None
        If None, do not look up the words in the text against the Lexicon.
        Otherwise, a dictionary of parameters that indicate how
        TextLookupRealTime should handle the lookup. For a human-less
        lookup experience, use 'auto_add' or 'auto_delete'.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    class LexiconLookupType(TypedDict):

        update_lexicon: NotRequired[bool]

        skip_numbers: NotRequired[bool]
        skip_numbers: NotRequired[bool]
        auto_split: NotRequired[bool]
        auto_add_to_lexicon: NotRequired[bool]
        auto_delete: NotRequired[bool]
        DELETE_ALWAYS: NotRequired[Sequence[str] | None]
        REPLACE_ALWAYS: NotRequired[dict[str, str] | None]
        SKIP_ALWAYS: NotRequired[Sequence[str] | None]
        SPLIT_ALWAYS: NotRequired[dict[str, Sequence[str]] | None]
        remove_empty_rows: NotRequired[bool]
        verbose: NotRequired[bool]

    """


    if _lexicon_lookup is None:
        return


    err_msg = (f"'lexicon_lookup' must be None or a dictionary of "
               f"valid parameters for TextLookupRealTime'. \nSee the "
               f"docs for TextLookupRealTime for information about valid "
               f"keys and values.")


    if not isinstance(_lexicon_lookup, dict):
        raise TypeError(err_msg)

    _allowed = [
        'update_lexicon', 'skip_numbers', 'auto_split', 'auto_add_to_lexicon',
        'auto_delete', 'DELETE_ALWAYS', 'REPLACE_ALWAYS', 'SKIP_ALWAYS',
        'SPLIT_ALWAYS', 'remove_empty_rows', 'verbose'
    ]
    for _key in _lexicon_lookup or {}:
        if _key not in _allowed:
            raise ValueError(err_msg)

    del _allowed






